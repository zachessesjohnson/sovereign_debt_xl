from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Iterable

import math
import numpy as np


def _is_nan(x: Any) -> bool:
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False


def to_2d_list(x: Any) -> list[list[Any]]:
    """Coerce Excel/PyXLL inputs into a 2D list without mutating the input."""
    if x is None:
        return []
    if isinstance(x, (str, bytes, int, float, bool, datetime, date)):
        return [[x]]
    if isinstance(x, list):
        if len(x) == 0:
            return []
        if any(isinstance(r, list) for r in x):
            return [list(r) if isinstance(r, list) else [r] for r in x]
        return [[v] for v in x]
    return [[x]]


def flatten_2d(x: Any) -> list[Any]:
    grid = to_2d_list(x)
    return [v for row in grid for v in row]


def to_1d_floats(x: Any, *, drop_nan: bool = True) -> list[float]:
    vals = []
    for v in flatten_2d(x):
        if _is_nan(v):
            if not drop_nan:
                vals.append(float("nan"))
            continue
        try:
            vals.append(float(v))
        except Exception:
            continue
    return vals


def to_2d_floats(x: Any, *, drop_nan_rows: bool = False) -> list[list[float]]:
    grid = to_2d_list(x)
    out: list[list[float]] = []
    for row in grid:
        new_row: list[float] = []
        row_has_non_nan = False
        for v in row:
            if _is_nan(v):
                new_row.append(float("nan"))
                continue
            try:
                fv = float(v)
                new_row.append(fv)
                if not math.isnan(fv):
                    row_has_non_nan = True
            except Exception:
                new_row.append(float("nan"))
        if drop_nan_rows and (len(new_row) == 0 or not row_has_non_nan):
            continue
        out.append(new_row)
    return out


def safe_err(e: Exception) -> str:
    return f"#ERR: {e}"


def excel_serial_to_date(serial: float) -> date:
    # Excel serial dates: day 1 is 1899-12-31 in Excel's system, but Excel also
    # has the 1900 leap-year bug. This mapping is the common practical approach:
    # serial 1 => 1899-12-31 + 1 day = 1900-01-01
    base = date(1899, 12, 30)  # so 1 -> 1900-01-01
    return base + timedelta(days=int(serial))


def to_date(x: Any) -> date:
    """Accept Excel serials, ISO strings, datetime/date."""
    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, (int, float)) and not _is_nan(x):
        return excel_serial_to_date(float(x))
    if isinstance(x, str):
        s = x.strip()
        # ISO date
        return datetime.fromisoformat(s).date()
    raise ValueError(f"Unsupported date value: {x!r}")


def business_day_count(start: Any, end: Any) -> int:
    s = to_date(start)
    e = to_date(end)
    if e < s:
        s, e = e, s
        sign = -1
    else:
        sign = 1
    # numpy.busday_count counts days in [start, end), so add 1 day to make end inclusive?
    # We'll match Excel NETWORKDAYS-like inclusive behavior by adding 1 to end.
    count = np.busday_count(np.datetime64(s), np.datetime64(e) + np.timedelta64(1, "D"))
    return int(sign * count)
