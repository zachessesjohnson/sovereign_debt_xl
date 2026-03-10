"""sovereign_debt_py.plotting.yield_curve

Yield-curve chart: ``plot_yield_curve``.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .core import to_1d_array, validate_same_length, apply_sdpy_style, _make_fig_ax

__all__ = ["plot_yield_curve"]

# Valid style tokens
_VALID_STYLES = {"line", "markers", "line+markers"}


def plot_yield_curve(
    tenors,
    yields,
    *,
    title: str | None = None,
    x_label: str = "Tenor",
    y_label: str = "Yield",
    style: str = "line",
    as_percent: bool = True,
    grid: bool = True,
    fig: Figure | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot a yield curve (tenors vs yields).

    Parameters
    ----------
    tenors:
        Array-like of numeric tenor values (e.g. years to maturity).
    yields:
        Array-like of corresponding yield values.  When *as_percent* is
        ``True`` the values are treated as decimals (0.045 → 4.5 %).
    title:
        Optional chart title.
    x_label:
        Label for the x-axis.  Defaults to ``"Tenor"``.
    y_label:
        Label for the y-axis.  Defaults to ``"Yield"``.
    style:
        One of ``"line"``, ``"markers"``, or ``"line+markers"``.
    as_percent:
        If ``True``, format the y-axis as percentages.
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
        If inputs have different lengths, or *style* is unrecognised.
    """
    t = to_1d_array(tenors)
    y = to_1d_array(yields)
    validate_same_length(t, y)

    if style not in _VALID_STYLES:
        raise ValueError(
            f"style must be one of {sorted(_VALID_STYLES)!r}; got {style!r}."
        )

    fig, ax = _make_fig_ax(fig, ax)

    # Build plot-kwargs
    line_kw: dict = {"linewidth": 2.0, "color": "#1f4e79"}
    marker_kw: dict = {"marker": "o", "markersize": 6, "markerfacecolor": "white",
                       "markeredgewidth": 1.5}

    if style == "line":
        ax.plot(t, y, **line_kw)
    elif style == "markers":
        ax.plot(t, y, linestyle="none", **marker_kw, color="#1f4e79")
    else:  # "line+markers"
        ax.plot(t, y, **line_kw, **marker_kw)

    if as_percent:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(
            lambda v, _pos: f"{v * 100:.2f}%"
        ))

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)

    apply_sdpy_style(ax, grid=grid)
    return fig, ax
