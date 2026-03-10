"""Tests for sovereign_debt_xl.plots plotting UDFs."""
from __future__ import annotations

import datetime

import pytest

from sovereign_debt_xl.plots import (
    sdxl_plot_rolling_avg,
    sdxl_plot_timeseries,
    sdxl_plot_yield_curve,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_dates(n: int, start: str = "2020-01-01") -> list[datetime.date]:
    base = datetime.date.fromisoformat(start)
    return [base + datetime.timedelta(days=i) for i in range(n)]


# ---------------------------------------------------------------------------
# SDXL_PLOT_YIELD_CURVE
# ---------------------------------------------------------------------------

class TestPlotYieldCurve:
    def test_returns_bytes_for_valid_input(self):
        tenors = [1.0, 2.0, 5.0, 10.0, 30.0]
        yields = [0.02, 0.025, 0.03, 0.035, 0.04]
        result = sdxl_plot_yield_curve(tenors, yields)
        # In tests pyxll is mocked, so xl_image falls back to raw bytes
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_length_mismatch_returns_error(self):
        result = sdxl_plot_yield_curve([1.0, 2.0], [0.02])
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_empty_input_returns_error(self):
        result = sdxl_plot_yield_curve([], [])
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_markers_style(self):
        tenors = [1.0, 2.0, 5.0, 10.0]
        yields = [0.02, 0.025, 0.03, 0.035]
        result = sdxl_plot_yield_curve(tenors, yields, style="markers")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_cache_returns_same_bytes(self):
        tenors = [1.0, 5.0, 10.0]
        yields = [0.02, 0.03, 0.04]
        r1 = sdxl_plot_yield_curve(tenors, yields, title="Cache Test")
        r2 = sdxl_plot_yield_curve(tenors, yields, title="Cache Test")
        assert r1 == r2

    def test_large_yields_no_pct_axis(self):
        # Yields > 1 should not be multiplied by 100
        tenors = [1.0, 2.0, 5.0]
        yields = [2.0, 3.0, 4.0]
        result = sdxl_plot_yield_curve(tenors, yields)
        assert isinstance(result, bytes)

    def test_2d_list_input(self):
        # Simulate Excel 2D range input
        tenors = [[1.0], [2.0], [5.0], [10.0]]
        yields = [[0.02], [0.025], [0.03], [0.035]]
        result = sdxl_plot_yield_curve(tenors, yields)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_custom_labels(self):
        tenors = [1.0, 5.0, 10.0]
        yields = [0.02, 0.03, 0.04]
        result = sdxl_plot_yield_curve(
            tenors, yields,
            title="My Curve", x_label="Maturity", y_label="Rate",
        )
        assert isinstance(result, bytes)


# ---------------------------------------------------------------------------
# SDXL_PLOT_TIMESERIES
# ---------------------------------------------------------------------------

class TestPlotTimeseries:
    def test_returns_bytes_for_valid_input(self):
        dates = _make_dates(30)
        values = [float(i) for i in range(30)]
        result = sdxl_plot_timeseries(dates, values, "Test Series")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_length_mismatch_returns_error(self):
        dates = _make_dates(5)
        values = [1.0, 2.0]
        result = sdxl_plot_timeseries(dates, values)
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_empty_input_returns_error(self):
        result = sdxl_plot_timeseries([], [])
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_excel_serial_dates(self):
        # Excel serial: 1 = 1900-01-01; use a range starting around 2020
        # 2020-01-01 is serial 43831
        serials = [43831 + i for i in range(10)]
        values = [float(i) for i in range(10)]
        result = sdxl_plot_timeseries(serials, values)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_iso_string_dates(self):
        dates = ["2020-01-01", "2020-02-01", "2020-03-01"]
        values = [1.0, 2.0, 3.0]
        result = sdxl_plot_timeseries(dates, values)
        assert isinstance(result, bytes)

    def test_cache_consistent(self):
        dates = _make_dates(20)
        values = list(range(20))
        r1 = sdxl_plot_timeseries(dates, values, "TS Cache")
        r2 = sdxl_plot_timeseries(dates, values, "TS Cache")
        assert r1 == r2

    def test_custom_dimensions(self):
        dates = _make_dates(15)
        values = [float(i) for i in range(15)]
        result = sdxl_plot_timeseries(dates, values, width_px=400, height_px=300)
        assert isinstance(result, bytes)


# ---------------------------------------------------------------------------
# SDXL_PLOT_ROLLING_AVG
# ---------------------------------------------------------------------------

class TestPlotRollingAvg:
    def test_returns_bytes_for_valid_input(self):
        dates = _make_dates(60)
        values = [float(i % 10) for i in range(60)]
        result = sdxl_plot_rolling_avg(dates, values, window=10, title="Rolling 10")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_length_mismatch_returns_error(self):
        dates = _make_dates(5)
        values = [1.0, 2.0]
        result = sdxl_plot_rolling_avg(dates, values, window=3)
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_empty_input_returns_error(self):
        result = sdxl_plot_rolling_avg([], [], window=5)
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_invalid_window_returns_error(self):
        dates = _make_dates(10)
        values = list(range(10))
        result = sdxl_plot_rolling_avg(dates, values, window=0)
        assert isinstance(result, str)
        assert "#SDXL:" in result

    def test_window_larger_than_data(self):
        # Still valid; just almost all rolling values will be NaN (only one computed at end)
        dates = _make_dates(5)
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = sdxl_plot_rolling_avg(dates, values, window=10)
        assert isinstance(result, bytes)

    def test_cache_consistent(self):
        dates = _make_dates(30)
        values = list(range(30))
        r1 = sdxl_plot_rolling_avg(dates, values, window=5, title="RA Cache")
        r2 = sdxl_plot_rolling_avg(dates, values, window=5, title="RA Cache")
        assert r1 == r2

    def test_different_windows_produce_different_images(self):
        dates = _make_dates(50)
        values = list(range(50))
        r5 = sdxl_plot_rolling_avg(dates, values, window=5)
        r20 = sdxl_plot_rolling_avg(dates, values, window=20)
        assert r5 != r20
