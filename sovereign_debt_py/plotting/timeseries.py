"""sovereign_debt_py.plotting.timeseries

Time-series and spread charts:
- ``plot_timeseries``
- ``plot_rolling_average``
- ``plot_spread``
"""

from __future__ import annotations

import datetime
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .core import (
    to_1d_array,
    validate_same_length,
    coerce_dates,
    apply_sdpy_style,
    _make_fig_ax,
)

__all__ = ["plot_timeseries", "plot_rolling_average", "plot_spread"]


def _rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    """Compute a rolling mean with NaN for the first ``window-1`` positions.

    Uses pandas if available; falls back to a pure-numpy implementation.
    """
    if window < 1:
        raise ValueError(f"window must be >= 1; got {window}.")
    if window > len(values):
        raise ValueError(
            f"window ({window}) is larger than the number of data points ({len(values)})."
        )

    try:
        import pandas as pd
        return pd.Series(values).rolling(window).mean().to_numpy()
    except ImportError:
        result = np.full_like(values, np.nan, dtype=float)
        for i in range(window - 1, len(values)):
            result[i] = values[i - window + 1 : i + 1].mean()
        return result


_TWO_YEARS_DAYS = 366 * 2


def _auto_date_format(ax: Axes, dates: list[datetime.datetime]) -> None:
    """Apply sensible date tick formatting to *ax* based on the date range."""
    if len(dates) < 2:
        return
    span = (dates[-1] - dates[0]).days
    if span <= 90:
        fmt = mdates.DateFormatter("%d-%b")
        locator = mdates.WeekdayLocator()
    elif span <= _TWO_YEARS_DAYS:
        fmt = mdates.DateFormatter("%b %Y")
        locator = mdates.MonthLocator()
    else:
        fmt = mdates.DateFormatter("%Y")
        locator = mdates.YearLocator()

    ax.xaxis.set_major_formatter(fmt)
    ax.xaxis.set_major_locator(locator)
    ax.figure.autofmt_xdate(rotation=30, ha="right")


# ---------------------------------------------------------------------------
# plot_timeseries
# ---------------------------------------------------------------------------

def plot_timeseries(
    dates,
    values,
    *,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    grid: bool = True,
    fig: Figure | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot a date-indexed time series.

    Parameters
    ----------
    dates:
        Sequence of date-like objects (``datetime.date``, ``datetime.datetime``,
        ISO-format strings, or pandas timestamps).
    values:
        Numeric array-like of the same length as *dates*.
    title:
        Optional chart title.
    x_label, y_label:
        Optional axis labels.
    grid:
        Show grid lines.
    fig, ax:
        Optional existing Figure/Axes to draw onto.

    Returns
    -------
    (fig, ax) :
        The Matplotlib Figure and Axes objects.

    Raises
    ------
    ValueError
        If *dates* and *values* have different lengths.
    """
    dt = coerce_dates(dates)
    v = to_1d_array(values)
    validate_same_length(dt, v)

    fig, ax = _make_fig_ax(fig, ax)

    ax.plot(dt, v, linewidth=2.0, color="#1f4e79")

    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)

    _auto_date_format(ax, dt)
    apply_sdpy_style(ax, grid=grid)
    return fig, ax


# ---------------------------------------------------------------------------
# plot_rolling_average
# ---------------------------------------------------------------------------

def plot_rolling_average(
    dates,
    values,
    window: int,
    *,
    title: str | None = None,
    base_label: str = "Series",
    roll_label: str | None = None,
    grid: bool = True,
    fig: Figure | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot a time series with a rolling-mean overlay.

    Parameters
    ----------
    dates:
        Sequence of date-like objects.
    values:
        Numeric array-like of the same length as *dates*.
    window:
        Rolling window size (number of observations).
    title:
        Optional chart title.
    base_label:
        Legend label for the raw series.
    roll_label:
        Legend label for the rolling-average line.  Defaults to
        ``"<window>-period MA"``.
    grid:
        Show grid lines.
    fig, ax:
        Optional existing Figure/Axes to draw onto.

    Returns
    -------
    (fig, ax) :
        The Matplotlib Figure and Axes objects.

    Raises
    ------
    ValueError
        If *dates* and *values* have different lengths, or *window* is invalid.
    """
    dt = coerce_dates(dates)
    v = to_1d_array(values)
    validate_same_length(dt, v)
    roll = _rolling_mean(v, window)

    if roll_label is None:
        roll_label = f"{window}-period MA"

    fig, ax = _make_fig_ax(fig, ax)

    ax.plot(dt, v, linewidth=1.5, alpha=0.55, color="#1f4e79", label=base_label)
    ax.plot(dt, roll, linewidth=2.5, color="#c00000", label=roll_label)

    ax.legend(fontsize=9)

    if title:
        ax.set_title(title)

    _auto_date_format(ax, dt)
    apply_sdpy_style(ax, grid=grid)
    return fig, ax


# ---------------------------------------------------------------------------
# plot_spread
# ---------------------------------------------------------------------------

def plot_spread(
    dates_or_tenors,
    series_a,
    series_b,
    *,
    label_a: str = "A",
    label_b: str = "B",
    title: str | None = None,
    spread_label: str = "Spread",
    fig: Figure | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot the spread between two series (series_a − series_b).

    The function creates **two vertically stacked** sub-plots:

    1. Both input series overlaid.
    2. The spread (``series_a - series_b``).

    Parameters
    ----------
    dates_or_tenors:
        Shared x-axis values (date-like or numeric tenors).
    series_a, series_b:
        Numeric array-likes of the same length as *dates_or_tenors*.
    label_a, label_b:
        Legend labels for the two input series.
    title:
        Optional overall figure title.
    spread_label:
        Label for the spread subplot.
    fig, ax:
        If provided, the spread is drawn onto the supplied Axes only (single
        panel).  Pass ``None`` for the default two-panel layout.

    Returns
    -------
    (fig, ax) :
        The Figure and the **spread** Axes (bottom panel, or the only panel
        when *ax* is supplied explicitly).

    Raises
    ------
    ValueError
        If inputs have different lengths.
    """
    a = to_1d_array(series_a)
    b = to_1d_array(series_b)
    validate_same_length(a, b)

    # Decide whether *dates_or_tenors* looks like dates or numeric tenors.
    # Avoid attempting pandas Timestamp coercion on plain integers/floats
    # (which triggers a nanosecond-discard UserWarning).
    def _looks_like_dates(seq) -> bool:
        for item in seq:
            if isinstance(item, (datetime.date, datetime.datetime)):
                return True
            if isinstance(item, str):
                return True
        return False

    if _looks_like_dates(dates_or_tenors):
        try:
            x = coerce_dates(dates_or_tenors)
            is_dates = True
        except (ValueError, TypeError):
            x = to_1d_array(dates_or_tenors)
            is_dates = False
    else:
        x = to_1d_array(dates_or_tenors)
        is_dates = False

    validate_same_length(a, list(x) if is_dates else x)

    spread = a - b

    if fig is None and ax is None:
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 5))
        ax_series, ax_spread = axes
    else:
        fig, ax_spread = _make_fig_ax(fig, ax)
        ax_series = None  # single-panel caller

    # Panel 1: both series
    if ax_series is not None:
        ax_series.plot(x, a, linewidth=2.0, color="#1f4e79", label=label_a)
        ax_series.plot(x, b, linewidth=2.0, color="#c00000", label=label_b)
        ax_series.legend(fontsize=9)
        if is_dates:
            _auto_date_format(ax_series, x)  # type: ignore[arg-type]
        apply_sdpy_style(ax_series)

    # Panel 2: spread
    ax_spread.plot(x, spread, linewidth=2.0, color="#375623", label=spread_label)
    ax_spread.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax_spread.set_ylabel(spread_label)
    ax_spread.legend(fontsize=9)
    if is_dates:
        _auto_date_format(ax_spread, x)  # type: ignore[arg-type]
    apply_sdpy_style(ax_spread)

    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold")

    return fig, ax_spread
