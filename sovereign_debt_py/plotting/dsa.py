"""sovereign_debt_py.plotting.dsa

Debt-sustainability fan chart: ``plot_fan_chart``.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .core import to_1d_array, validate_same_length, apply_sdpy_style, _make_fig_ax

__all__ = ["plot_fan_chart"]


def plot_fan_chart(
    x,
    p50,
    bands: dict,
    *,
    title: str | None = None,
    y_label: str | None = None,
    cmap: str = "Blues",
    fig: Figure | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot a debt-sustainability fan chart with percentile bands.

    Parameters
    ----------
    x:
        Numeric array-like (e.g. years on the x-axis).
    p50:
        Numeric array-like representing the median/central projection.
    bands:
        Dict mapping a ``(lower_prob, upper_prob)`` tuple to a
        ``(lower_series, upper_series)`` pair.  Example::

            {
                (0.10, 0.90): (p10_array, p90_array),
                (0.25, 0.75): (p25_array, p75_array),
            }

        Bands are drawn from widest (lowest alpha) to narrowest (highest
        alpha) so inner bands are visually on top.
    title:
        Optional chart title.
    y_label:
        Optional y-axis label.
    cmap:
        Name of the Matplotlib colormap to use for shading the bands.
        Defaults to ``"Blues"``.
    fig, ax:
        Optional existing Figure/Axes to draw onto.

    Returns
    -------
    (fig, ax) :
        The Matplotlib Figure and Axes objects.

    Raises
    ------
    ValueError
        If *x*, *p50*, or any band series have mismatched lengths.
    """
    xarr = to_1d_array(x)
    p50arr = to_1d_array(p50)
    validate_same_length(xarr, p50arr)

    # Sort bands from widest interval to narrowest so narrower bands are
    # painted on top.
    sorted_bands = sorted(
        bands.items(),
        key=lambda kv: kv[0][1] - kv[0][0],
        reverse=True,
    )

    colormap = plt.get_cmap(cmap)

    fig, ax = _make_fig_ax(fig, ax)

    n_bands = len(sorted_bands)
    for idx, ((lo_prob, hi_prob), (lo_series, hi_series)) in enumerate(sorted_bands):
        lo_arr = to_1d_array(lo_series)
        hi_arr = to_1d_array(hi_series)
        validate_same_length(xarr, lo_arr)
        validate_same_length(xarr, hi_arr)

        # Map band index to a colour intensity: wider bands → lighter shade
        alpha_val = 0.25 + 0.50 * (idx / max(n_bands - 1, 1))
        color = colormap(alpha_val)

        label = f"{int(lo_prob * 100)}th–{int(hi_prob * 100)}th pct."
        ax.fill_between(xarr, lo_arr, hi_arr, color=color, alpha=0.7, label=label)

    # Median line on top
    ax.plot(xarr, p50arr, color="black", linewidth=2.0, label="Median (p50)")

    ax.legend(fontsize=9)

    if y_label:
        ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)

    apply_sdpy_style(ax)
    return fig, ax
