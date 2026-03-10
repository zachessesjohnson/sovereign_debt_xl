"""sovereign_debt_py.plotting.core

Internal helpers: validation, styling, figure creation, and the
fig_to_png_bytes rendering utility.
"""

from __future__ import annotations

import io
import datetime
from typing import Sequence, Any

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.axes import Axes


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def to_1d_array(x: Any) -> np.ndarray:
    """Convert list, tuple, numpy array, or pandas Series to a 1-D ndarray.

    Raises
    ------
    ValueError
        If *x* cannot be converted or is not 1-D after conversion.
    """
    try:
        # pandas Series / Index
        arr = np.asarray(x, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Cannot convert input to a numeric 1-D array: {exc}"
        ) from exc

    if arr.ndim != 1:
        raise ValueError(
            f"Expected a 1-D array-like, got shape {arr.shape}."
        )
    return arr


def validate_same_length(*arrays: np.ndarray) -> None:
    """Raise ValueError if any two arrays differ in length."""
    lengths = [len(a) for a in arrays]
    if len(set(lengths)) > 1:
        raise ValueError(
            f"All inputs must have the same length; got lengths: {lengths}."
        )


def coerce_dates(dates: Sequence[Any]) -> list[datetime.datetime]:
    """Convert a sequence of date-like objects to :class:`datetime.datetime`.

    Accepts ``datetime.date``, ``datetime.datetime``, ISO-format strings,
    and numpy / pandas timestamp-like objects.

    Raises
    ------
    ValueError
        If any element cannot be parsed.
    """
    result: list[datetime.datetime] = []
    for item in dates:
        if isinstance(item, datetime.datetime):
            result.append(item)
        elif isinstance(item, datetime.date):
            result.append(datetime.datetime(item.year, item.month, item.day))
        elif isinstance(item, str):
            try:
                result.append(datetime.datetime.fromisoformat(item))
            except ValueError as exc:
                raise ValueError(
                    f"Cannot parse date string {item!r}: {exc}"
                ) from exc
        else:
            # numpy datetime64, pandas Timestamp, etc.
            try:
                import pandas as pd  # optional
                ts = pd.Timestamp(item)
                result.append(ts.to_pydatetime())
            except Exception:
                # Last resort: try numpy datetime64 → Python datetime
                try:
                    ts_ms = np.datetime64(item, "ms")
                    epoch = np.datetime64(0, "ms")
                    ms = int((ts_ms - epoch) / np.timedelta64(1, "ms"))
                    result.append(
                        datetime.datetime(1970, 1, 1)
                        + datetime.timedelta(milliseconds=ms)
                    )
                except Exception as exc2:
                    raise ValueError(
                        f"Cannot coerce {item!r} to datetime: {exc2}"
                    ) from exc2
    return result


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

def apply_sdpy_style(ax: Axes, *, grid: bool = True) -> None:
    """Apply consistent sovereign_debt_py chart styling to *ax*.

    Adjusts spines, font sizes, line widths, and optionally adds a grid.
    Does **not** call ``plt.style.use`` globally.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)

    ax.tick_params(axis="both", labelsize=9, length=4, width=0.8)
    ax.xaxis.label.set_size(10)
    ax.yaxis.label.set_size(10)
    if ax.get_title():
        ax.title.set_size(11)
        ax.title.set_fontweight("bold")

    if grid:
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)


# ---------------------------------------------------------------------------
# Figure factory
# ---------------------------------------------------------------------------

def _make_fig_ax(
    fig: Figure | None,
    ax: Axes | None,
) -> tuple[Figure, Axes]:
    """Return *(fig, ax)*, creating new ones if not supplied."""
    if fig is None and ax is None:
        fig, ax = plt.subplots()
    elif fig is None:
        fig = ax.get_figure()
    elif ax is None:
        ax = fig.gca()
    return fig, ax  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Rendering helper
# ---------------------------------------------------------------------------

def fig_to_png_bytes(
    fig: Figure,
    *,
    width_px: int = 800,
    height_px: int = 450,
    dpi: int = 120,
    tight: bool = True,
    close: bool = False,
) -> bytes:
    """Render *fig* to PNG and return the raw bytes.

    The figure's size is set (in inches) based on ``width_px / dpi`` and
    ``height_px / dpi`` before saving, so the output is deterministic.

    Parameters
    ----------
    fig:
        A Matplotlib :class:`~matplotlib.figure.Figure`.
    width_px:
        Output width in pixels.
    height_px:
        Output height in pixels.
    dpi:
        Dots per inch for the PNG encoder.
    tight:
        If *True*, call ``tight_layout()`` before saving.
    close:
        If *True*, close *fig* after saving (useful for embedding workflows).

    Returns
    -------
    bytes
        Raw PNG bytes (starts with ``b'\\x89PNG'``).
    """
    fig.set_size_inches(width_px / dpi, height_px / dpi)
    if tight:
        fig.tight_layout()

    buf = io.BytesIO()
    # Use the Agg backend for headless rendering without touching the global
    # backend.  canvas.print_figure works regardless of the current backend.
    agg_canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)
    agg_canvas.print_figure(buf, format="png", dpi=dpi)
    png_bytes = buf.getvalue()

    if close:
        plt.close(fig)

    return png_bytes
