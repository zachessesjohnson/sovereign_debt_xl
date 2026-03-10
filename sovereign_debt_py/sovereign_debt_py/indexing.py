from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats

from ._coerce import safe_err, to_1d_floats


def xl_rank_pct(value: float, values: Any) -> float | str:
    """Percentile rank of a value within a dataset (0..1)."""
    try:
        v = to_1d_floats(values)
        if len(v) == 0:
            return safe_err(ValueError("Empty values"))
        # percentileofscore returns 0..100
        p = stats.percentileofscore(v, value, kind="mean") / 100.0
        return float(p)
    except Exception as e:
        return safe_err(e)


def xl_zscore(values: Any) -> list[float] | str:
    """Z-score normalize a range (returns a column array)."""
    try:
        v = np.array(to_1d_floats(values, drop_nan=False), dtype=float)
        if v.size == 0:
            return []
        mu = np.nanmean(v)
        sd = np.nanstd(v, ddof=1)
        if np.isnan(sd) or sd == 0:
            return [float("nan") for _ in v.tolist()]
        z = (v - mu) / sd
        return [float(x) if not np.isnan(x) else float("nan") for x in z.tolist()]
    except Exception as e:
        return safe_err(e)


def xl_normalize_minmax(values: Any) -> list[float] | str:
    """Min-max scale a range to [0, 1] (returns a column array)."""
    try:
        v = np.array(to_1d_floats(values, drop_nan=False), dtype=float)
        if v.size == 0:
            return []
        vmin = np.nanmin(v)
        vmax = np.nanmax(v)
        if np.isnan(vmin) or np.isnan(vmax) or vmax == vmin:
            return [float("nan") for _ in v.tolist()]
        out = (v - vmin) / (vmax - vmin)
        return [float(x) if not np.isnan(x) else float("nan") for x in out.tolist()]
    except Exception as e:
        return safe_err(e)


def xl_index_to_base(values: Any, base_period: int) -> list[float] | str:
    """Rebase a time series to a given index period = 100 (1-based base_period)."""
    try:
        v = np.array(to_1d_floats(values, drop_nan=False), dtype=float)
        if v.size == 0:
            return []
        if base_period < 1 or base_period > v.size:
            return safe_err(ValueError("base_period out of range (1-based)"))
        base = v[base_period - 1]
        if np.isnan(base) or base == 0:
            return safe_err(ValueError("base value is NaN or zero"))
        out = (v / base) * 100.0
        return [float(x) if not np.isnan(x) else float("nan") for x in out.tolist()]
    except Exception as e:
        return safe_err(e)
