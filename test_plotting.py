"""Tests for sovereign_debt_py.plotting"""

import datetime
import pytest
import matplotlib
matplotlib.use("Agg")  # headless – must be set before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

import sovereign_debt_py.plotting as sdp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _close(fig):
    plt.close(fig)


# ---------------------------------------------------------------------------
# plot_yield_curve
# ---------------------------------------------------------------------------

class TestPlotYieldCurve:
    TENORS = [1, 2, 5, 10]
    YIELDS = [0.04, 0.045, 0.05, 0.052]

    def test_returns_fig_ax(self):
        fig, ax = sdp.plot_yield_curve(self.TENORS, self.YIELDS)
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        _close(fig)

    def test_title_applied(self):
        fig, ax = sdp.plot_yield_curve(
            self.TENORS, self.YIELDS, title="Sovereign Curve"
        )
        assert ax.get_title() == "Sovereign Curve"
        _close(fig)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            sdp.plot_yield_curve([1, 2, 3], [0.04, 0.05])

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="style"):
            sdp.plot_yield_curve(self.TENORS, self.YIELDS, style="bad_style")

    def test_all_styles_run(self):
        for style in ("line", "markers", "line+markers"):
            fig, ax = sdp.plot_yield_curve(self.TENORS, self.YIELDS, style=style)
            _close(fig)

    def test_uses_supplied_axes(self):
        fig, ax = plt.subplots()
        fig2, ax2 = sdp.plot_yield_curve(self.TENORS, self.YIELDS, fig=fig, ax=ax)
        assert fig2 is fig
        assert ax2 is ax
        _close(fig)


# ---------------------------------------------------------------------------
# plot_timeseries
# ---------------------------------------------------------------------------

class TestPlotTimeseries:
    DATES = [
        datetime.date(2023, 1, 1),
        datetime.date(2023, 2, 1),
        datetime.date(2023, 3, 1),
        datetime.date(2023, 4, 1),
    ]
    VALUES = [0.04, 0.041, 0.042, 0.043]

    def test_returns_fig_ax(self):
        fig, ax = sdp.plot_timeseries(self.DATES, self.VALUES)
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        _close(fig)

    def test_iso_string_dates(self):
        dates = ["2023-01-01", "2023-02-01", "2023-03-01"]
        fig, ax = sdp.plot_timeseries(dates, [0.04, 0.041, 0.042])
        assert isinstance(fig, Figure)
        _close(fig)

    def test_datetime_objects(self):
        dates = [datetime.datetime(2023, 1, d) for d in [1, 15, 28]]
        fig, ax = sdp.plot_timeseries(dates, [1.0, 2.0, 3.0])
        assert isinstance(ax, Axes)
        _close(fig)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            sdp.plot_timeseries(self.DATES, [0.04, 0.05])


# ---------------------------------------------------------------------------
# plot_rolling_average
# ---------------------------------------------------------------------------

class TestPlotRollingAverage:
    DATES = [datetime.date(2023, m, 1) for m in range(1, 13)]
    VALUES = list(range(12))

    def test_returns_fig_ax(self):
        fig, ax = sdp.plot_rolling_average(self.DATES, self.VALUES, window=3)
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        _close(fig)

    def test_custom_labels(self):
        fig, ax = sdp.plot_rolling_average(
            self.DATES,
            self.VALUES,
            window=3,
            base_label="Raw",
            roll_label="3M MA",
        )
        legend_texts = [t.get_text() for t in ax.get_legend().get_texts()]
        assert "Raw" in legend_texts
        assert "3M MA" in legend_texts
        _close(fig)

    def test_window_too_large_raises(self):
        with pytest.raises(ValueError):
            sdp.plot_rolling_average(self.DATES, self.VALUES, window=100)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            sdp.plot_rolling_average(self.DATES, [0.1, 0.2], window=2)


# ---------------------------------------------------------------------------
# plot_spread
# ---------------------------------------------------------------------------

class TestPlotSpread:
    DATES = [datetime.date(2023, 1, d) for d in range(1, 7)]
    A = [0.05, 0.051, 0.052, 0.053, 0.054, 0.055]
    B = [0.03, 0.031, 0.032, 0.033, 0.034, 0.035]

    def test_returns_fig_ax(self):
        fig, ax = sdp.plot_spread(self.DATES, self.A, self.B)
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        _close(fig)

    def test_numeric_x_axis(self):
        tenors = [1, 2, 5, 10, 20, 30]
        fig, ax = sdp.plot_spread(tenors, self.A, self.B)
        assert isinstance(fig, Figure)
        _close(fig)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            sdp.plot_spread(self.DATES, self.A, [0.03, 0.04])


# ---------------------------------------------------------------------------
# plot_fan_chart
# ---------------------------------------------------------------------------

class TestPlotFanChart:
    X = list(range(2024, 2031))
    P50 = [60.0, 62.0, 64.0, 63.0, 61.0, 60.0, 59.0]
    BANDS = {
        (0.10, 0.90): ([55.0] * 7, [70.0] * 7),
        (0.25, 0.75): ([58.0] * 7, [66.0] * 7),
    }

    def test_returns_fig_ax(self):
        fig, ax = sdp.plot_fan_chart(self.X, self.P50, self.BANDS)
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        _close(fig)

    def test_title_applied(self):
        fig, ax = sdp.plot_fan_chart(
            self.X, self.P50, self.BANDS, title="DSA Fan"
        )
        assert ax.get_title() == "DSA Fan"
        _close(fig)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            sdp.plot_fan_chart(
                self.X,
                [60.0] * 5,  # wrong length
                {},
            )


# ---------------------------------------------------------------------------
# fig_to_png_bytes
# ---------------------------------------------------------------------------

class TestFigToPngBytes:
    PNG_MAGIC = b"\x89PNG"

    def test_returns_png_bytes(self):
        fig, ax = sdp.plot_yield_curve([1, 2, 5, 10], [0.04, 0.045, 0.05, 0.052])
        png = sdp.fig_to_png_bytes(fig)
        assert isinstance(png, bytes)
        assert len(png) > 0
        assert png[:4] == self.PNG_MAGIC
        _close(fig)

    def test_custom_dimensions(self):
        fig, _ = sdp.plot_yield_curve([1, 2, 5], [0.03, 0.04, 0.05])
        png = sdp.fig_to_png_bytes(fig, width_px=400, height_px=300, dpi=72)
        assert png[:4] == self.PNG_MAGIC
        _close(fig)

    def test_close_flag_closes_figure(self):
        fig, _ = sdp.plot_yield_curve([1, 2, 5], [0.03, 0.04, 0.05])
        sdp.fig_to_png_bytes(fig, close=True)
        # After close=True the figure should no longer be in plt.get_fignums()
        assert fig.number not in plt.get_fignums()

    def test_timeseries_to_png(self):
        dates = ["2023-01-01", "2023-06-01", "2023-12-01"]
        fig, _ = sdp.plot_timeseries(dates, [0.04, 0.05, 0.045])
        png = sdp.fig_to_png_bytes(fig)
        assert png[:4] == self.PNG_MAGIC
        _close(fig)


# ---------------------------------------------------------------------------
# Input validation utilities (direct)
# ---------------------------------------------------------------------------

class TestCoreValidation:
    def test_to_1d_array_list(self):
        from sovereign_debt_py.plotting.core import to_1d_array
        import numpy as np
        arr = to_1d_array([1.0, 2.0, 3.0])
        assert arr.shape == (3,)

    def test_to_1d_array_2d_raises(self):
        from sovereign_debt_py.plotting.core import to_1d_array
        import numpy as np
        with pytest.raises(ValueError, match="1-D"):
            to_1d_array(np.array([[1, 2], [3, 4]]))

    def test_validate_same_length_ok(self):
        from sovereign_debt_py.plotting.core import validate_same_length
        import numpy as np
        validate_same_length(np.array([1, 2, 3]), np.array([4, 5, 6]))  # no error

    def test_validate_same_length_fail(self):
        from sovereign_debt_py.plotting.core import validate_same_length
        import numpy as np
        with pytest.raises(ValueError, match="same length"):
            validate_same_length(np.array([1, 2, 3]), np.array([4, 5]))

    def test_coerce_dates_iso_string(self):
        from sovereign_debt_py.plotting.core import coerce_dates
        result = coerce_dates(["2023-01-15", "2023-06-30"])
        assert result[0].year == 2023
        assert result[0].month == 1
        assert result[0].day == 15

    def test_coerce_dates_invalid_raises(self):
        from sovereign_debt_py.plotting.core import coerce_dates
        with pytest.raises(ValueError):
            coerce_dates(["not-a-date"])
