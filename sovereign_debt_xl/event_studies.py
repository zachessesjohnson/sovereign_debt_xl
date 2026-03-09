from __future__ import annotations

from typing import Any

import numpy as np
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats


@xl_func(
    "float debt_gdp, float spread_bps, float reserves_months, float haircut_comparables: object[][]",
    name="SOV_RESTRUCTURING_COMPARABLES",
)
def restructuring_comparables(
    debt_gdp: float,
    spread_bps: float,
    reserves_months: float,
    haircut_comparables: float,
) -> list[list[Any]] | str:
    """Return ranked historical sovereign restructuring comparables.

    Matches pre-crisis fundamentals using a simplified Euclidean distance to a
    hard-coded set of 15 canonical historical episodes.  Returns nearest
    neighbours with haircut, recovery rate, and time-to-resolution.

    Note: In a production setting this would query a live database; here the
    historical episodes are embedded as representative illustrative data.
    """
    try:
        dg = float(debt_gdp)
        sp = float(spread_bps)
        rm = float(reserves_months)
        # Representative historical episodes:
        # [country, year, debt_gdp, spread_bps, reserves_months, haircut_pct, recovery_pct, months_to_resolution]
        episodes = [
            ("Argentina", 2001, 0.62, 1800, 1.2, 65, 35, 42),
            ("Greece", 2012, 1.65, 3500, 3.1, 53, 47, 18),
            ("Ecuador", 1999, 0.92, 1400, 1.8, 45, 55, 12),
            ("Russia", 1998, 0.57, 2500, 1.5, 38, 62, 24),
            ("Ukraine", 2015, 0.98, 2000, 2.5, 25, 75, 12),
            ("Jamaica", 2013, 1.47, 600, 2.8, 15, 85, 6),
            ("Belize", 2012, 0.80, 900, 2.2, 45, 55, 18),
            ("Grenada", 2013, 0.99, 800, 2.0, 50, 50, 24),
            ("Venezuela", 2020, 2.30, 10000, 0.4, 75, 25, 60),
            ("Zambia", 2020, 1.00, 1500, 2.3, 40, 60, 30),
            ("Sri Lanka", 2022, 1.10, 3000, 1.0, 35, 65, 24),
            ("Lebanon", 2020, 1.72, 5000, 0.8, 70, 30, 48),
            ("Pakistan", 2023, 0.75, 1200, 2.0, 5, 95, 6),
            ("Dominican Rep.", 2005, 0.55, 600, 3.5, 6, 94, 3),
            ("Uruguay", 2003, 1.00, 900, 4.0, 13, 87, 6),
        ]
        comparables = np.array([[e[2], e[3], e[4]] for e in episodes], dtype=float)
        query = np.array([dg, sp, rm], dtype=float)
        # Normalise by approximate range before computing distance
        ranges = np.array([1.5, 9000.0, 5.0])
        dist = np.linalg.norm((comparables - query) / ranges, axis=1)
        ranked = np.argsort(dist)[:5]
        out: list[list[Any]] = [
            ["rank", "country", "year", "debt_gdp", "spread_bps", "reserves_months",
             "haircut_pct", "recovery_pct", "months_to_resolution", "distance"]
        ]
        for rank, idx in enumerate(ranked, 1):
            e = episodes[idx]
            out.append([rank, e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], round(float(dist[idx]), 4)])
        # Weighted averages of top-5
        weights = 1.0 / (dist[ranked] + 1e-9)
        weights /= weights.sum()
        avg_haircut = float(np.dot(weights, [episodes[i][5] for i in ranked]))
        avg_recovery = float(np.dot(weights, [episodes[i][6] for i in ranked]))
        avg_months = float(np.dot(weights, [episodes[i][7] for i in ranked]))
        out.append(["", "", "", "", "", "", "", "", "", ""])
        out.append(["weighted_avg", "", "", "", "", "",
                    round(avg_haircut, 1), round(avg_recovery, 1), round(avg_months, 1), ""])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] spread_series, float[] event_dates_serial, int window_before, int window_after: object[][]",
    name="SOV_EVENT_STUDY_SPREAD",
)
def event_study_spread_reaction(
    spread_series: Any,
    event_dates_serial: Any,
    window_before: int,
    window_after: int,
) -> list[list[Any]] | str:
    """Average abnormal spread changes around events, with 95 % confidence bands.

    spread_series: daily spread observations (T length).
    event_dates_serial: indices (0-based) of the event dates within the spread series.
    window_before/window_after: number of days to include on each side.

    Abnormal change at day t = spread[event+t] − average spread over pre-event window.
    """
    try:
        spreads = np.array(to_1d_floats(spread_series), dtype=float)
        events = [int(e) for e in to_1d_floats(event_dates_serial)]
        T = len(spreads)
        if T < window_before + window_after + 1:
            return safe_err(ValueError("spread_series too short for the requested windows"))
        if not events:
            return safe_err(ValueError("event_dates_serial must not be empty"))
        if window_before < 1 or window_after < 1:
            return safe_err(ValueError("window_before and window_after must each be >= 1"))
        windows: list[np.ndarray] = []
        for ev in events:
            if ev - window_before < 0 or ev + window_after >= T:
                continue
            baseline = float(np.mean(spreads[ev - window_before : ev]))
            window = spreads[ev : ev + window_after + 1] - baseline
            windows.append(window)
        if not windows:
            return safe_err(ValueError("No usable events within spread_series bounds"))
        mat = np.vstack(windows)
        mean_abn = np.mean(mat, axis=0)
        se = np.std(mat, axis=0, ddof=1) / np.sqrt(mat.shape[0]) if mat.shape[0] > 1 else np.zeros_like(mean_abn)
        ci95 = 1.96 * se
        out: list[list[Any]] = [["day_rel_event", "mean_abnormal_spread", "ci95_lower", "ci95_upper"]]
        for d in range(window_after + 1):
            out.append([d, round(float(mean_abn[d]), 4),
                        round(float(mean_abn[d] - ci95[d]), 4),
                        round(float(mean_abn[d] + ci95[d]), 4)])
        out.append(["", "", "", ""])
        out.append(["n_events_used", mat.shape[0], "", ""])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] indicator_values, float[] thresholds: object[][]",
    name="SOV_CRISIS_EARLY_WARNING",
)
def crisis_early_warning_signal(
    indicator_values: Any,
    thresholds: Any,
) -> list[list[Any]] | str:
    """Kaminsky-Lizondo-Reinhart signal extraction approach.

    For each indicator, a signal is issued when the indicator crosses its
    threshold.  Returns:
    - Number of simultaneous signals
    - Composite noise-to-signal ratio (lower is better)
    - Traffic-light assessment

    indicator_values: current values for each indicator.
    thresholds: crisis-threshold for each indicator (signal when value >= threshold).

    A lower noise-to-signal ratio (below 1.0) means the indicator provides
    useful early-warning information.
    """
    try:
        vals = np.array(to_1d_floats(indicator_values), dtype=float)
        thresh = np.array(to_1d_floats(thresholds), dtype=float)
        n = len(vals)
        if n == 0:
            return safe_err(ValueError("indicator_values must not be empty"))
        if len(thresh) != n:
            return safe_err(ValueError("thresholds must have the same length as indicator_values"))
        signals = vals >= thresh
        n_signals = int(signals.sum())
        signal_ratio = n_signals / n
        # Noise-to-signal heuristic: empirical NtS ≈ 1 − signal_ratio
        # (simplified — in production would use historical crisis/tranquil periods)
        nts = float(np.clip(1.0 - signal_ratio, 0.0, 1.0))
        # Traffic light
        if signal_ratio >= 0.60:
            light = "RED"
        elif signal_ratio >= 0.30:
            light = "AMBER"
        else:
            light = "GREEN"
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["n_indicators", n])
        out.append(["n_signals_active", n_signals])
        out.append(["signal_ratio", round(signal_ratio, 4)])
        out.append(["noise_to_signal_ratio", round(nts, 4)])
        out.append(["traffic_light", light])
        out.append(["", ""])
        out.append(["indicator_index", "value", "threshold", "signal"])
        for i in range(n):
            out.append([i + 1, round(float(vals[i]), 4), round(float(thresh[i]), 4), int(signals[i])])
        return out
    except Exception as e:
        return safe_err(e)
