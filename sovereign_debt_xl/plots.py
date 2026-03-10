"""Plotting UDFs for sovereign debt analysis.

Exposes Excel-callable functions that render Matplotlib charts to PNG and
return them as PyXLL image objects so Excel displays them inline.

Example Excel formulas
----------------------
=SDXL_PLOT_YIELD_CURVE(A2:A20, B2:B20, "UST Curve")
=SDXL_PLOT_TIMESERIES(A2:A300, B2:B300, "10yr Yield")
=SDXL_PLOT_ROLLING_AVG(A2:A300, B2:B300, 20, "Rolling Avg (20)")
"""
from __future__ import annotations

import hashlib
import io
import pickle
from collections import OrderedDict
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless – must come before pyplot import
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from pyxll import xl_func

from ._coerce import flatten_2d, safe_err, to_1d_floats, to_date

# ---------------------------------------------------------------------------
# LRU image cache (bounded to avoid unbounded memory growth)
# ---------------------------------------------------------------------------

_CACHE_MAX = 128
_cache: OrderedDict[str, bytes] = OrderedDict()


def _cache_get(key: str) -> bytes | None:
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    return None


def _cache_put(key: str, data: bytes) -> None:
    if key in _cache:
        _cache.move_to_end(key)
    _cache[key] = data
    while len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)


# ---------------------------------------------------------------------------
# Cache-key helpers
# ---------------------------------------------------------------------------

def _make_cache_key(*args: Any) -> str:
    """Build a stable SHA-256 hex digest from arbitrary positional arguments."""

    def _normalize(v: Any) -> Any:
        if isinstance(v, np.ndarray):
            return (v.tobytes(), v.shape, str(v.dtype))
        if isinstance(v, list):
            return tuple(_normalize(i) for i in v)
        if isinstance(v, float):
            return round(v, 6)
        return v

    normalized = tuple(_normalize(a) for a in args)
    raw = pickle.dumps(normalized, protocol=4)
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Figure rendering
# ---------------------------------------------------------------------------

_DEFAULT_DPI = 100


def _render_png(fig: Any, width_px: int, height_px: int, dpi: int = _DEFAULT_DPI) -> bytes:
    """Render *fig* to PNG bytes, then close the figure to free memory."""
    fig.set_size_inches(width_px / dpi, height_px / dpi)
    buf = io.BytesIO()
    try:
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        return buf.getvalue()
    finally:
        plt.close(fig)


def _png_to_xl_image(png_bytes: bytes) -> Any:
    """Wrap PNG bytes in a PyXLL image object.

    PyXLL exposes ``pyxll.xl_image`` (or ``pyxll.Image``) for inline images.
    We try the documented API first; if unavailable (e.g. during unit-tests
    where pyxll is mocked) we fall back to returning the raw bytes.
    """
    try:
        from pyxll import xl_image  # type: ignore[attr-defined]
        return xl_image(data=io.BytesIO(png_bytes))
    except Exception:
        return png_bytes


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

_SDXL_PREFIX = "#SDXL: "


def _to_dates(raw: Any) -> list:
    """Flatten an Excel range and coerce each cell to a Python date."""
    flat = flatten_2d(raw)
    out = []
    for v in flat:
        if v is None:
            continue
        try:
            out.append(to_date(v))
        except Exception:
            pass
    return out


def _check_lengths(a: list, b: list, label_a: str = "x", label_b: str = "y") -> str | None:
    if len(a) == 0 or len(b) == 0:
        return f"{_SDXL_PREFIX}no data"
    if len(a) != len(b):
        return f"{_SDXL_PREFIX}length mismatch ({label_a}={len(a)}, {label_b}={len(b)})"
    return None


# ---------------------------------------------------------------------------
# UDF: SDXL_PLOT_YIELD_CURVE
# ---------------------------------------------------------------------------

@xl_func(
    "object[] tenors, object[] yields,"
    " str title, str x_label, str y_label,"
    " int width_px, int height_px, str style: object",
    name="SDXL_PLOT_YIELD_CURVE",
)
def sdxl_plot_yield_curve(
    tenors: Any,
    yields: Any,
    title: str = "Yield Curve",
    x_label: str = "Tenor",
    y_label: str = "Yield",
    width_px: int = 800,
    height_px: int = 450,
    style: str = "line",
) -> Any:
    """Plot a yield curve (tenors vs yields) and return a PyXLL inline image.

    Parameters
    ----------
    tenors:
        Excel range of tenor values (numeric years or labels).
    yields:
        Excel range of yield values (matching length to *tenors*).
    title:
        Chart title.
    x_label:
        X-axis label (default ``"Tenor"``).
    y_label:
        Y-axis label (default ``"Yield"``).
    width_px:
        Output image width in pixels (default 800).
    height_px:
        Output image height in pixels (default 450).
    style:
        ``"line"`` (default) or ``"markers"``.
    """
    try:
        x_vals = to_1d_floats(tenors)
        y_vals = to_1d_floats(yields)
        err = _check_lengths(x_vals, y_vals, "tenors", "yields")
        if err:
            return err

        title = title or "Yield Curve"
        x_label = x_label or "Tenor"
        y_label = y_label or "Yield"
        width_px = int(width_px) if width_px else 800
        height_px = int(height_px) if height_px else 450

        key = _make_cache_key(
            "SDXL_PLOT_YIELD_CURVE", x_vals, y_vals,
            title, x_label, y_label, width_px, height_px, style,
        )
        cached = _cache_get(key)
        if cached is not None:
            return _png_to_xl_image(cached)

        x_arr = np.array(x_vals)
        y_arr = np.array(y_vals)

        # Heuristic: if all yields < 1 treat as decimal fractions → display as %
        as_pct = bool(np.all(np.abs(y_arr) <= 1.0))

        fig, ax = plt.subplots()
        plot_kwargs: dict[str, Any] = {"marker": "o" if style == "markers" else None,
                                        "linewidth": 2}
        ax.plot(x_arr, y_arr * 100 if as_pct else y_arr, **plot_kwargs)
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(f"{y_label} (%)" if as_pct else y_label)
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()

        png = _render_png(fig, width_px, height_px)
        _cache_put(key, png)
        return _png_to_xl_image(png)
    except Exception as e:
        return safe_err(e)


# ---------------------------------------------------------------------------
# UDF: SDXL_PLOT_TIMESERIES
# ---------------------------------------------------------------------------

@xl_func(
    "object[] dates, object[] values,"
    " str title, int width_px, int height_px: object",
    name="SDXL_PLOT_TIMESERIES",
)
def sdxl_plot_timeseries(
    dates: Any,
    values: Any,
    title: str = "Time Series",
    width_px: int = 800,
    height_px: int = 450,
) -> Any:
    """Plot a time-series (dates vs values) and return a PyXLL inline image.

    Parameters
    ----------
    dates:
        Excel range of date values (datetime, Excel serial, or ISO string).
    values:
        Excel range of numeric values (matching length to *dates*).
    title:
        Chart title.
    width_px:
        Output image width in pixels (default 800).
    height_px:
        Output image height in pixels (default 450).
    """
    try:
        d_list = _to_dates(dates)
        v_list = to_1d_floats(values)
        err = _check_lengths(d_list, v_list, "dates", "values")
        if err:
            return err

        title = title or "Time Series"
        width_px = int(width_px) if width_px else 800
        height_px = int(height_px) if height_px else 450

        # Cache key uses ISO string representations of dates for stability
        d_strs = [str(d) for d in d_list]
        key = _make_cache_key(
            "SDXL_PLOT_TIMESERIES", d_strs, v_list, title, width_px, height_px,
        )
        cached = _cache_get(key)
        if cached is not None:
            return _png_to_xl_image(cached)

        import datetime as _dt
        x_arr = [_dt.datetime(d.year, d.month, d.day) for d in d_list]
        y_arr = np.array(v_list)

        fig, ax = plt.subplots()
        ax.plot(x_arr, y_arr, linewidth=1.5)
        ax.set_title(title)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.AutoDateLocator()))
        fig.autofmt_xdate(rotation=30)
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()

        png = _render_png(fig, width_px, height_px)
        _cache_put(key, png)
        return _png_to_xl_image(png)
    except Exception as e:
        return safe_err(e)


# ---------------------------------------------------------------------------
# UDF: SDXL_PLOT_ROLLING_AVG
# ---------------------------------------------------------------------------

@xl_func(
    "object[] dates, object[] values,"
    " int window, str title,"
    " int width_px, int height_px: object",
    name="SDXL_PLOT_ROLLING_AVG",
)
def sdxl_plot_rolling_avg(
    dates: Any,
    values: Any,
    window: int = 20,
    title: str = "Rolling Average",
    width_px: int = 800,
    height_px: int = 450,
) -> Any:
    """Plot original data with a rolling average overlay and return a PyXLL inline image.

    Parameters
    ----------
    dates:
        Excel range of date values.
    values:
        Excel range of numeric values (matching length to *dates*).
    window:
        Rolling window size (number of periods).
    title:
        Chart title.
    width_px:
        Output image width in pixels (default 800).
    height_px:
        Output image height in pixels (default 450).
    """
    try:
        d_list = _to_dates(dates)
        v_list = to_1d_floats(values)
        err = _check_lengths(d_list, v_list, "dates", "values")
        if err:
            return err

        window = int(window) if window is not None else 20
        if window < 1:
            return f"{_SDXL_PREFIX}window must be >= 1"

        title = title or "Rolling Average"
        width_px = int(width_px) if width_px else 800
        height_px = int(height_px) if height_px else 450

        d_strs = [str(d) for d in d_list]
        key = _make_cache_key(
            "SDXL_PLOT_ROLLING_AVG", d_strs, v_list, window, title, width_px, height_px,
        )
        cached = _cache_get(key)
        if cached is not None:
            return _png_to_xl_image(cached)

        import datetime as _dt
        x_arr = [_dt.datetime(d.year, d.month, d.day) for d in d_list]
        y_arr = np.array(v_list, dtype=float)

        # Compute rolling mean (NaN-padded for the first window-1 positions)
        rolling = np.full_like(y_arr, np.nan)
        for i in range(window - 1, len(y_arr)):
            rolling[i] = float(np.mean(y_arr[i - window + 1: i + 1]))

        fig, ax = plt.subplots()
        ax.plot(x_arr, y_arr, color="lightsteelblue", linewidth=1.0,
                alpha=0.7, label="Original")
        ax.plot(x_arr, rolling, color="steelblue", linewidth=2.0,
                label=f"Rolling {window}")
        ax.set_title(title)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.AutoDateLocator()))
        fig.autofmt_xdate(rotation=30)
        ax.legend(loc="best")
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()

        png = _render_png(fig, width_px, height_px)
        _cache_put(key, png)
        return _png_to_xl_image(png)
    except Exception as e:
        return safe_err(e)
