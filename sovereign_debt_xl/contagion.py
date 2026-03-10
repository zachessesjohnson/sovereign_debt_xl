from __future__ import annotations

from typing import Any

import numpy as np
import statsmodels.api as sm
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats, to_2d_list


@xl_func(
    "float[] target_country_spreads, float[] source_country_spreads,"
    " float[] global_factor_series, int window_days: object[][]",
    name="SOV_CONTAGION_BETA",
)
def sovereign_contagion_beta(
    target_country_spreads: Any,
    source_country_spreads: Any,
    global_factor_series: Any,
    window_days: int,
) -> list[list[Any]] | str:
    """Rolling regression beta isolating bilateral contagion after controlling for a global factor.

    For each rolling window of size window_days, regresses target spread changes
    on source spread changes and global factor changes.  Returns the time-series of
    bilateral betas (coefficient on source) and summary statistics.
    """
    try:
        target = np.array(to_1d_floats(target_country_spreads), dtype=float)
        source = np.array(to_1d_floats(source_country_spreads), dtype=float)
        global_f = np.array(to_1d_floats(global_factor_series), dtype=float)
        n = len(target)
        if n < 10:
            return safe_err(ValueError("Need at least 10 observations"))
        if len(source) != n or len(global_f) != n:
            return safe_err(ValueError("All series must have the same length"))
        if window_days < 5 or window_days >= n:
            return safe_err(ValueError(f"window_days must be in [5, {n - 1}]"))
        d_target = np.diff(target)
        d_source = np.diff(source)
        d_global = np.diff(global_f)
        m = len(d_target)
        betas: list[float] = []
        for i in range(window_days - 1, m):
            start = i - window_days + 1
            y = d_target[start : i + 1]
            X = np.column_stack([d_source[start : i + 1], d_global[start : i + 1]])
            X = sm.add_constant(X)
            try:
                res = sm.OLS(y, X).fit()
                betas.append(float(res.params[1]))
            except Exception:
                betas.append(float("nan"))
        betas_arr = np.array(betas, dtype=float)
        valid = betas_arr[~np.isnan(betas_arr)]
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["n_windows", len(betas)])
        out.append(["mean_beta", round(float(np.mean(valid)), 4) if len(valid) else float("nan")])
        out.append(["median_beta", round(float(np.median(valid)), 4) if len(valid) else float("nan")])
        out.append(["beta_std", round(float(np.std(valid, ddof=1)), 4) if len(valid) > 1 else float("nan")])
        out.append(["", ""])
        out.append(["window_index", "beta"])
        for i, b in enumerate(betas):
            out.append([i + window_days, round(b, 4) if not np.isnan(b) else float("nan")])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] spread_series_a, float[] spread_series_b, int window: object[][]",
    name="SOV_DCC_GARCH_CORR",
)
def dcc_garch_correlation(
    spread_series_a: Any,
    spread_series_b: Any,
    window: int,
) -> list[list[Any]] | str:
    """Dynamic conditional correlation between two sovereign spread series.

    Uses a rolling-window DCC approximation: standardise each series by its
    rolling EWMA volatility, then compute the rolling correlation of the
    standardised residuals.  This is a tractable proxy for full DCC-GARCH
    suitable for Excel use.
    """
    try:
        a = np.array(to_1d_floats(spread_series_a), dtype=float)
        b = np.array(to_1d_floats(spread_series_b), dtype=float)
        n = len(a)
        if n < 10:
            return safe_err(ValueError("Need at least 10 observations"))
        if len(b) != n:
            return safe_err(ValueError("Both series must have the same length"))
        if window < 5 or window >= n:
            return safe_err(ValueError(f"window must be in [5, {n - 1}]"))

        # EWMA variance (decay = 0.94, RiskMetrics style)
        decay = 0.94
        da = np.diff(a)
        db = np.diff(b)
        m = len(da)
        var_a = np.zeros(m)
        var_b = np.zeros(m)
        var_a[0] = da[0] ** 2
        var_b[0] = db[0] ** 2
        for t in range(1, m):
            var_a[t] = decay * var_a[t - 1] + (1 - decay) * da[t] ** 2
            var_b[t] = decay * var_b[t - 1] + (1 - decay) * db[t] ** 2
        std_a = np.sqrt(np.maximum(var_a, 1e-12))
        std_b = np.sqrt(np.maximum(var_b, 1e-12))
        ea = da / std_a
        eb = db / std_b

        # Rolling correlation of standardised residuals
        corrs: list[float] = []
        for i in range(window - 1, m):
            s = i - window + 1
            ca, cb = ea[s : i + 1], eb[s : i + 1]
            if np.std(ca) == 0 or np.std(cb) == 0:
                corrs.append(float("nan"))
            else:
                corrs.append(float(np.corrcoef(ca, cb)[0, 1]))

        valid = [c for c in corrs if not np.isnan(c)]
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["mean_dcc", round(float(np.mean(valid)), 4) if valid else float("nan")])
        out.append(["min_dcc", round(float(np.min(valid)), 4) if valid else float("nan")])
        out.append(["max_dcc", round(float(np.max(valid)), 4) if valid else float("nan")])
        out.append(["", ""])
        out.append(["window_index", "dcc"])
        for i, c in enumerate(corrs):
            out.append([i + window, round(c, 4) if not np.isnan(c) else float("nan")])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[][] spread_matrix, int lags, float significance_level: object[][]",
    name="SOV_GRANGER_CAUSALITY",
)
def granger_causality_spreads(
    spread_matrix: Any,
    lags: int,
    significance_level: float,
) -> list[list[Any]] | str:
    """Pairwise Granger causality across sovereign spreads.

    spread_matrix: columns are countries (T × N), each column is one spread series.
    Returns an N × N adjacency matrix where entry [i, j] = 1 if country i
    Granger-causes country j at the given significance level.
    """
    try:
        from statsmodels.tsa.stattools import grangercausalitytests

        grid = to_2d_list(spread_matrix)
        if not grid or not grid[0]:
            return safe_err(ValueError("spread_matrix is empty"))
        # Try to detect if it has a header row
        start = 1 if isinstance(grid[0][0], str) else 0
        data_rows = grid[start:]
        if len(data_rows) < 10:
            return safe_err(ValueError("Need at least 10 data rows"))
        try:
            arr = np.array([[float(v) for v in row] for row in data_rows], dtype=float)
        except Exception:
            return safe_err(ValueError("All cells in spread_matrix must be numeric"))
        T, N = arr.shape
        if N < 2:
            return safe_err(ValueError("Need at least 2 country columns"))
        if lags < 1 or lags >= T // 2:
            return safe_err(ValueError(f"lags must be in [1, {T // 2 - 1}]"))
        if not (0.0 < significance_level < 1.0):
            return safe_err(ValueError("significance_level must be in (0, 1)"))

        adj: list[list[int | str | float]] = []
        header: list[Any] = ["causes\\is_caused_by"] + [f"c{j + 1}" for j in range(N)]
        adj.append(header)
        for i in range(N):
            row_vals: list[Any] = [f"c{i + 1}"]
            for j in range(N):
                if i == j:
                    row_vals.append(0)
                    continue
                test_data = arr[:, [j, i]]  # [caused, cause]
                try:
                    result = grangercausalitytests(test_data, maxlag=lags, verbose=False)
                    # Use F-test p-value at the selected lag
                    pval = result[lags][0]["ssr_ftest"][1]
                    row_vals.append(1 if float(pval) < significance_level else 0)
                except Exception:
                    row_vals.append(float("nan"))
            adj.append(row_vals)
        return adj
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[][] bilateral_trade_flows, float[] gdp_values: object[][]",
    name="SOV_TRADE_LINKAGE_MATRIX",
)
def trade_linkage_matrix(
    bilateral_trade_flows: Any,
    gdp_values: Any,
) -> list[list[Any]] | str:
    """Trade-weighted exposure matrix normalised by GDP.

    bilateral_trade_flows: N × N matrix of bilateral trade (rows = exporters, cols = importers).
    gdp_values: length-N vector of GDP values (same currency as trade flows).

    Returns an N × N matrix where entry [i, j] = trade_{i→j} / GDP_j,
    showing country j's real-economy exposure to stress in country i.
    """
    try:
        grid = to_2d_list(bilateral_trade_flows)
        if not grid:
            return safe_err(ValueError("bilateral_trade_flows is empty"))
        start = 1 if isinstance(grid[0][0], str) else 0
        data_rows = grid[start:]
        try:
            flows = np.array([[float(v) for v in row] for row in data_rows], dtype=float)
        except Exception:
            return safe_err(ValueError("All cells in bilateral_trade_flows must be numeric"))
        N, M = flows.shape
        if N != M:
            return safe_err(ValueError("bilateral_trade_flows must be a square N × N matrix"))
        gdp = np.array(to_1d_floats(gdp_values), dtype=float)
        if len(gdp) != N:
            return safe_err(ValueError("gdp_values must have N elements matching the matrix dimension"))
        if np.any(gdp == 0):
            return safe_err(ValueError("All GDP values must be non-zero"))
        # exposure[i, j] = flows[i, j] / gdp[j]
        exposure = flows / gdp[np.newaxis, :]
        out: list[list[Any]] = [["exporter\\importer"] + [f"c{j + 1}" for j in range(N)]]
        for i in range(N):
            out.append([f"c{i + 1}"] + [round(float(exposure[i, j]), 6) for j in range(N)])
        return out
    except Exception as e:
        return safe_err(e)
