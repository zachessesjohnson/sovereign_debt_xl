"""Pure-Python plotting helpers for sovereign debt analysis.

All functions return ``(fig, ax)`` tuples so callers can further customise
the chart before saving or displaying it.  Use :func:`fig_to_png_bytes` to
serialise a figure to PNG bytes.
"""
from __future__ import annotations

import datetime
import io
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless – must come before pyplot import
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from .core import coerce_dates, to_1d_array, validate_same_length

__all__ = [
    "plot_yield_curve",
    "plot_timeseries",
    "plot_rolling_average",
    "plot_spread",
    "plot_fan_chart",
    "fig_to_png_bytes",
]

_VALID_STYLES = ("line", "markers", "line+markers")


# ---------------------------------------------------------------------------
# plot_yield_curve
# ---------------------------------------------------------------------------

def plot_yield_curve(
    tenors: Any,
    yields: Any,
    title: str | None = None,
    style: str = "line",
    fig: Any = None,
    ax: Any = None,
) -> tuple[Any, Any]:
    """Plot a yield curve (tenors vs yields) and return ``(fig, ax)``.

    Parameters
    ----------
    tenors:
        Sequence of numeric tenor values (years).
    yields:
        Sequence of yield values matching *tenors* in length.
    title:
        Optional chart title.
    style:
        One of ``"line"``, ``"markers"``, or ``"line+markers"``.
    fig, ax:
        Optional existing Matplotlib figure and axes to plot into.

    Raises
    ------
    ValueError
        If *tenors* and *yields* have different lengths, or *style* is invalid.
    """
    t_arr = to_1d_array(tenors)
    y_arr = to_1d_array(yields)
    validate_same_length(t_arr, y_arr)
    if style not in _VALID_STYLES:
        raise ValueError(
            f"Invalid style {style!r}; must be one of {_VALID_STYLES}"
        )

    if fig is None or ax is None:
        fig, ax = plt.subplots()

    use_marker = style in ("markers", "line+markers")
    use_line = style in ("line", "line+markers")
    ax.plot(
        t_arr,
        y_arr,
        marker="o" if use_marker else None,
        linestyle="-" if use_line else "none",
        linewidth=2,
    )
    if title:
        ax.set_title(title)
    ax.set_xlabel("Tenor")
    ax.set_ylabel("Yield")
    ax.grid(True, linestyle="--", alpha=0.5)
    return fig, ax


# ---------------------------------------------------------------------------
# plot_timeseries
# ---------------------------------------------------------------------------

def plot_timeseries(
    dates: Any,
    values: Any,
    title: str | None = None,
) -> tuple[Any, Any]:
    """Plot a time-series (dates vs values) and return ``(fig, ax)``.

    Parameters
    ----------
    dates:
        Sequence of date-like values (:class:`datetime.date`,
        :class:`datetime.datetime`, or ISO-format strings).
    values:
        Sequence of numeric values matching *dates* in length.
    title:
        Optional chart title.

    Raises
    ------
    ValueError
        If *dates* and *values* have different lengths.
    """
    d_list = coerce_dates(dates)
    v_arr = to_1d_array(values)
    validate_same_length(np.array(d_list), v_arr)

    fig, ax = plt.subplots()
    x_dt = [datetime.datetime(d.year, d.month, d.day) for d in d_list]
    ax.plot(x_dt, v_arr, linewidth=1.5)
    if title:
        ax.set_title(title)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(
        mdates.AutoDateFormatter(mdates.AutoDateLocator())
    )
    fig.autofmt_xdate(rotation=30)
    ax.grid(True, linestyle="--", alpha=0.5)
    return fig, ax


# ---------------------------------------------------------------------------
# plot_rolling_average
# ---------------------------------------------------------------------------

def plot_rolling_average(
    dates: Any,
    values: Any,
    window: int,
    base_label: str = "Original",
    roll_label: str | None = None,
) -> tuple[Any, Any]:
    """Plot data with a rolling-average overlay and return ``(fig, ax)``.

    Parameters
    ----------
    dates:
        Sequence of date-like values.
    values:
        Sequence of numeric values matching *dates* in length.
    window:
        Rolling window size (number of periods).  Must be ≥ 1 and ≤
        ``len(values)``.
    base_label:
        Legend label for the raw series (default ``"Original"``).
    roll_label:
        Legend label for the rolling-average series.  Defaults to
        ``f"Rolling {window}"``.

    Raises
    ------
    ValueError
        If *dates* and *values* have different lengths, or *window* is larger
        than the data length.
    """
    d_list = coerce_dates(dates)
    v_arr = to_1d_array(values)
    validate_same_length(np.array(d_list), v_arr)
    window = int(window)
    if window < 1:
        raise ValueError(f"window must be >= 1 (got {window})")
    if window > len(v_arr):
        raise ValueError(
            f"window ({window}) is larger than the data length ({len(v_arr)})"
        )
    if roll_label is None:
        roll_label = f"Rolling {window}"

    rolling = np.full_like(v_arr, np.nan, dtype=float)
    for i in range(window - 1, len(v_arr)):
        rolling[i] = float(np.mean(v_arr[i - window + 1: i + 1]))

    fig, ax = plt.subplots()
    x_dt = [datetime.datetime(d.year, d.month, d.day) for d in d_list]
    ax.plot(x_dt, v_arr, color="lightsteelblue", linewidth=1.0, alpha=0.7, label=base_label)
    ax.plot(x_dt, rolling, color="steelblue", linewidth=2.0, label=roll_label)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(
        mdates.AutoDateFormatter(mdates.AutoDateLocator())
    )
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)
    return fig, ax


# ---------------------------------------------------------------------------
# plot_spread
# ---------------------------------------------------------------------------

def plot_spread(
    x: Any,
    series_a: Any,
    series_b: Any,
    label_a: str = "Series A",
    label_b: str = "Series B",
    title: str | None = None,
) -> tuple[Any, Any]:
    """Plot two series and their spread and return ``(fig, ax)``.

    Parameters
    ----------
    x:
        Sequence of x-axis values (dates or numerics).
    series_a, series_b:
        Sequences of numeric values, each matching *x* in length.
    label_a, label_b:
        Legend labels.
    title:
        Optional chart title.

    Raises
    ------
    ValueError
        If any of the three sequences have different lengths.
    """
    a_arr = to_1d_array(series_a)
    b_arr = to_1d_array(series_b)

    # x may be dates or numerics
    try:
        x_vals: Any = coerce_dates(x)
        x_plot = [datetime.datetime(d.year, d.month, d.day) for d in x_vals]
        use_dates = True
    except (ValueError, TypeError):
        x_plot = list(x)
        use_dates = False

    validate_same_length(np.array(x_plot), a_arr)
    validate_same_length(a_arr, b_arr)

    fig, ax = plt.subplots()
    ax.plot(x_plot, a_arr, label=label_a, linewidth=1.5)
    ax.plot(x_plot, b_arr, label=label_b, linewidth=1.5)
    if use_dates:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(
            mdates.AutoDateFormatter(mdates.AutoDateLocator())
        )
        fig.autofmt_xdate(rotation=30)
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)
    return fig, ax


# ---------------------------------------------------------------------------
# plot_fan_chart
# ---------------------------------------------------------------------------

def plot_fan_chart(
    x: Any,
    p50: Any,
    bands: dict[tuple[float, float], tuple[Any, Any]],
    title: str | None = None,
) -> tuple[Any, Any]:
    """Plot a fan chart with confidence bands and return ``(fig, ax)``.

    Parameters
    ----------
    x:
        Sequence of x-axis values (e.g. years).
    p50:
        Sequence of median values matching *x* in length.
    bands:
        Mapping of ``(low_prob, high_prob)`` → ``(lower_series, upper_series)``
        where each series matches *x* in length.
    title:
        Optional chart title.

    Raises
    ------
    ValueError
        If *x* and *p50* (or any band series) have different lengths.
    """
    x_arr = to_1d_array(x)
    p50_arr = to_1d_array(p50)
    validate_same_length(x_arr, p50_arr)

    fig, ax = plt.subplots()
    for (lo_prob, hi_prob), (lower, upper) in bands.items():
        lo_arr = to_1d_array(lower)
        hi_arr = to_1d_array(upper)
        validate_same_length(x_arr, lo_arr)
        validate_same_length(x_arr, hi_arr)
        label = f"{int(lo_prob * 100)}–{int(hi_prob * 100)}%"
        ax.fill_between(x_arr, lo_arr, hi_arr, alpha=0.3, label=label)
    ax.plot(x_arr, p50_arr, linewidth=2, label="Median", color="steelblue")
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)
    return fig, ax


# ---------------------------------------------------------------------------
# fig_to_png_bytes
# ---------------------------------------------------------------------------

def fig_to_png_bytes(
    fig: Any,
    width_px: int | None = None,
    height_px: int | None = None,
    dpi: int = 100,
    close: bool = False,
) -> bytes:
    """Render *fig* to PNG bytes.

    Parameters
    ----------
    fig:
        Matplotlib figure to render.
    width_px, height_px:
        Optional output dimensions in pixels.  When provided the figure size
        is adjusted before rendering.
    dpi:
        Dots per inch for the output PNG (default 100).
    close:
        If ``True``, close *fig* after rendering to free memory.

    Returns
    -------
    bytes
        PNG-encoded image bytes.
    """
    if width_px is not None and height_px is not None:
        fig.set_size_inches(width_px / dpi, height_px / dpi)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    if close:
        plt.close(fig)
    return buf.getvalue()
