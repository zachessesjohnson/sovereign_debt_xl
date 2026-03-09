from sovereign_debt_xl.forecasting import (
    xl_exp_smoothing,
    xl_linear_forecast,
    xl_moving_avg_forecast,
)


def test_linear_forecast_line():
    # y = 2x
    yhat = xl_linear_forecast([1, 2, 3], [2, 4, 6], 4)
    assert abs(yhat - 8.0) < 1e-6


def test_exp_smoothing_alpha_1_is_identity_for_non_nan():
    out = xl_exp_smoothing([1, 2, 3], 1.0)
    assert out == [1.0, 2.0, 3.0]


def test_moving_avg_forecast():
    out = xl_moving_avg_forecast([1, 2, 3, 4], 2, 3)
    assert out == [3.5, 3.5, 3.5]
