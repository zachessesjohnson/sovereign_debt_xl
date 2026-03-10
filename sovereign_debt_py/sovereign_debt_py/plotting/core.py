"""Core validation utilities for sovereign_debt_py.plotting."""
from __future__ import annotations

import datetime
from typing import Any

import numpy as np


def to_1d_array(data: Any) -> np.ndarray:
    """Convert *data* to a 1-D NumPy array.

    Raises
    ------
    ValueError
        If the resulting array is not 1-D.
    """
    arr = np.asarray(data)
    if arr.ndim != 1:
        raise ValueError(f"Input must be 1-D; got shape {arr.shape}")
    return arr


def validate_same_length(a: np.ndarray, b: np.ndarray) -> None:
    """Raise ValueError if *a* and *b* have different lengths."""
    if len(a) != len(b):
        raise ValueError(
            f"Arrays must have the same length (got {len(a)} and {len(b)})"
        )


def coerce_dates(dates: Any) -> list[datetime.date]:
    """Coerce a sequence of values to a list of :class:`datetime.date` objects.

    Accepts :class:`datetime.date`, :class:`datetime.datetime`, or ISO-format
    strings (``"YYYY-MM-DD"``).

    Raises
    ------
    ValueError
        If any value cannot be parsed as a date.
    """
    result: list[datetime.date] = []
    for d in dates:
        if isinstance(d, datetime.datetime):
            result.append(d.date())
        elif isinstance(d, datetime.date):
            result.append(d)
        elif isinstance(d, str):
            try:
                result.append(datetime.date.fromisoformat(d))
            except ValueError:
                raise ValueError(f"Cannot parse date string: {d!r}")
        else:
            raise ValueError(f"Cannot coerce to date: {d!r}")
    return result
