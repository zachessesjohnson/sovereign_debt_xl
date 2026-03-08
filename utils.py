from __future__ import annotations

from typing import Any

from pyxll import xl_func

from ._coerce import business_day_count, safe_err, to_2d_list, flatten_2d


@xl_func("object[][] range: object[][]", name="SOV_ARRAY_SHAPE")
def xl_array_shape(range: Any) -> list[list[Any]] | str:
    """Returns rows x cols of a range (debugging helper)."""
    try:
        grid = to_2d_list(range)
        rows = len(grid)
        cols = max((len(r) for r in grid), default=0)
        return [["rows", "cols"], [rows, cols]]
    except Exception as e:
        return safe_err(e)


@xl_func("object[][] range: object[]", name="SOV_FLATTEN")
def xl_flatten(range: Any) -> list[Any] | str:
    """Flatten a 2D range to a 1D column."""
    try:
        return flatten_2d(range)
    except Exception as e:
        return safe_err(e)


@xl_func("object start_date, object end_date: int", name="SOV_DATE_DIFF_BUS")
def xl_date_diff_bus(start_date: Any, end_date: Any) -> int | str:
    """Business day count between two dates (NETWORKDAYS-like inclusive)."""
    try:
        return business_day_count(start_date, end_date)
    except Exception as e:
        return safe_err(e)
