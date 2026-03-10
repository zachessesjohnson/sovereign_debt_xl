from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats

from ._coerce import safe_err, to_1d_floats


def xl_weighted_average(values: Any, weights: Any) -> float | str:
    """Weighted mean of a range."""
    try:
        v = to_1d_floats(values)
        w = to_1d_floats(weights)
        if len(v) == 0 or len(w) == 0:
            return safe_err(ValueError("Empty values/weights"))
        if len(v) != len(w):
            return safe_err(ValueError("values and weights must have same length"))
        wsum = float(np.sum(w))
        if wsum == 0:
            return safe_err(ValueError("Sum of weights is zero"))
        return float(np.average(v, weights=w))
    except Exception as e:
        return safe_err(e)


def xl_rolling_average(values: Any, window: int) -> list[float] | str:
    """Rolling/moving average over N periods (returns a column array)."""
    try:
        v = to_1d_floats(values, drop_nan=False)
        if window <= 0:
            return safe_err(ValueError("window must be > 0"))
        if len(v) == 0:
            return []
        out: list[float] = []
        for i in range(len(v)):
            start = max(0, i - window + 1)
            chunk = [x for x in v[start : i + 1] if not np.isnan(x)]
            out.append(float(np.mean(chunk)) if len(chunk) else float("nan"))
        return out
    except Exception as e:
        return safe_err(e)


def xl_trimmed_mean(values: Any, trim_pct: float) -> float | str:
    """Mean after trimming top/bottom X% (trim_pct in [0, 0.5))."""
    try:
        v = to_1d_floats(values)
        if len(v) == 0:
            return safe_err(ValueError("Empty values"))
        if not (0 <= trim_pct < 0.5):
            return safe_err(ValueError("trim_pct must be in [0, 0.5)"))
        return float(stats.trim_mean(v, proportiontocut=float(trim_pct)))
    except Exception as e:
        return safe_err(e)


def xl_describe(values: Any) -> list[list[Any]] | str:
    """Returns a table: count, mean, std, min, max, median, skewness, kurtosis."""
    try:
        v = np.array(to_1d_floats(values), dtype=float)
        if v.size == 0:
            return safe_err(ValueError("Empty values"))
        out = [
            ["stat", "value"],
            ["count", int(v.size)],
            ["mean", float(np.mean(v))],
            ["std", float(np.std(v, ddof=1)) if v.size > 1 else float("nan")],
            ["min", float(np.min(v))],
            ["max", float(np.max(v))],
            ["median", float(np.median(v))],
            ["skewness", float(stats.skew(v, bias=False)) if v.size > 2 else float("nan")],
            ["kurtosis", float(stats.kurtosis(v, bias=False)) if v.size > 3 else float("nan")],
        ]
        return out
    except Exception as e:
        return safe_err(e)
