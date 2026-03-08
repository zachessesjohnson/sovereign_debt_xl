from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from pyxll import xl_func
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm

from ._coerce import safe_err, to_1d_floats


@xl_func("float[] x_values, float[] y_values, float forecast_x: float", name="SOV_LINEAR_FORECAST")
def xl_linear_forecast(x_values: Any, y_values: Any, forecast_x: float) -> float | str:
    """Simple OLS linear regression forecast y at forecast_x."""
    try:
        x = np.array(to_1d_floats(x_values), dtype=float)
        y = np.array(to_1d_floats(y_values), dtype=float)
        if x.size == 0 or y.size == 0:
            return safe_err(ValueError("Empty x_values/y_values"))
        if x.size != y.size:
            return safe_err(ValueError("x_values and y_values must have same length"))
        X = sm.add_constant(x)
        model = sm.OLS(y, X).fit()
        yhat = float(model.predict([1.0, float(forecast_x)])[0])
        return yhat
    except Exception as e:
        return safe_err(e)


@xl_func("float[] values, float alpha: float[]", name="SOV_EXP_SMOOTHING")
def xl_exp_smoothing(values: Any, alpha: float) -> list[float] | str:
    """Single exponential smoothing (returns smoothed series as column array)."""
    try:
        v = np.array(to_1d_floats(values, drop_nan=False), dtype=float)
        if v.size == 0:
            return []
        if not (0 < alpha <= 1):
            return safe_err(ValueError("alpha must be in (0, 1]"))
        s = []
        last = np.nan
        for i, x in enumerate(v):
            if np.isnan(x):
                s.append(float("nan"))
                continue
            if i == 0 or np.isnan(last):
                last = x
            else:
                last = alpha * x + (1 - alpha) * last
            s.append(float(last))
        return s
    except Exception as e:
        return safe_err(e)


@xl_func("float[] values, int periods_ahead: float[]", name="SOV_HOLT_FORECAST")
def xl_holt_forecast(values: Any, periods_ahead: int) -> list[float] | str:
    """Holt's double exponential smoothing (trend) forecast (returns forecast values)."""
    try:
        v = to_1d_floats(values)
        if len(v) < 2:
            return safe_err(ValueError("Need at least 2 values"))
        if periods_ahead <= 0:
            return safe_err(ValueError("periods_ahead must be > 0"))
        series = pd.Series(v)
        fit = ExponentialSmoothing(series, trend="add", seasonal=None).fit()
        fc = fit.forecast(periods_ahead)
        return [float(x) for x in fc.tolist()]
    except Exception as e:
        return safe_err(e)


@xl_func("float[] values, int window, int periods_ahead: float[]", name="SOV_MOVING_AVG_FORECAST")
def xl_moving_avg_forecast(values: Any, window: int, periods_ahead: int) -> list[float] | str:
    """Forecast using trailing moving average (flat forecast)."""
    try:
        v = to_1d_floats(values)
        if len(v) == 0:
            return safe_err(ValueError("Empty values"))
        if window <= 0:
            return safe_err(ValueError("window must be > 0"))
        if periods_ahead <= 0:
            return safe_err(ValueError("periods_ahead must be > 0"))
        tail = v[-window:] if len(v) >= window else v[:]
        avg = float(np.mean(tail))
        return [avg for _ in range(periods_ahead)]
    except Exception as e:
        return safe_err(e)


@xl_func("float[] values, int period: object[][]", name="SOV_SEASONAL_DECOMPOSE")
def xl_seasonal_decompose(values: Any, period: int) -> list[list[Any]] | str:
    """Returns trend, seasonal, residual as a 3-column array."""
    try:
        v = to_1d_floats(values)
        if len(v) < max(2 * period, period + 1):
            return safe_err(ValueError("Not enough data for decomposition"))
        if period <= 1:
            return safe_err(ValueError("period must be > 1"))
        s = pd.Series(v)
        res = seasonal_decompose(s, model="additive", period=period, extrapolate_trend="freq")
        out = [["trend", "seasonal", "residual"]]
        for t, se, r in zip(res.trend.tolist(), res.seasonal.tolist(), res.resid.tolist()):
            out.append(
                [
                    float(t) if t is not None and not np.isnan(t) else float("nan"),
                    float(se) if se is not None and not np.isnan(se) else float("nan"),
                    float(r) if r is not None and not np.isnan(r) else float("nan"),
                ]
            )
        return out
    except Exception as e:
        return safe_err(e)
