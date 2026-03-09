from __future__ import annotations

from typing import Any

import numpy as np
from pyxll import xl_func
import statsmodels.api as sm

from ._coerce import safe_err, to_1d_floats, to_2d_floats


@xl_func("float[] y_values, float[][] x_columns: object[][]", name="SOV_REGRESSION")
def xl_regression(y_values: Any, x_columns: Any) -> list[list[Any]] | str:
    """Multiple OLS regression; returns coefficients + R²."""
    try:
        y = np.array(to_1d_floats(y_values), dtype=float)
        X_grid = to_2d_floats(x_columns)
        if y.size == 0:
            return safe_err(ValueError("Empty y_values"))
        if len(X_grid) == 0 or len(X_grid[0]) == 0:
            return safe_err(ValueError("Empty x_columns"))
        X = np.array(X_grid, dtype=float)
        if X.shape[0] != y.shape[0]:
            return safe_err(ValueError("x_columns rows must match y_values length"))
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        params = model.params.tolist()
        out = [["term", "coef"]]
        out.append(["const", float(params[0])])
        for i, c in enumerate(params[1:], start=1):
            out.append([f"x{i}", float(c)])
        out.append(["R2", float(model.rsquared)])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func("float[][] data_range: object[][]", name="SOV_CORRELATION_MATRIX")
def xl_correlation_matrix(data_range: Any) -> list[list[Any]] | str:
    """Pairwise correlation table from a 2D range."""
    try:
        X = np.array(to_2d_floats(data_range), dtype=float)
        if X.size == 0:
            return safe_err(ValueError("Empty data_range"))
        # Correlation across columns
        corr = np.corrcoef(X, rowvar=False)
        n = corr.shape[0]
        out: list[list[Any]] = [[""] + [f"c{i+1}" for i in range(n)]]
        for i in range(n):
            out.append([f"c{i+1}"] + [float(corr[i, j]) for j in range(n)])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func("float mean, float std_dev, int n_simulations, int n_periods: object[][]", name="SOV_MONTE_CARLO")
def xl_monte_carlo(mean: float, std_dev: float, n_simulations: int, n_periods: int) -> list[list[Any]] | str:
    """Simulate N paths, return percentile summary of ending value (P5/P50/P95)."""
    try:
        if n_simulations <= 0 or n_periods <= 0:
            return safe_err(ValueError("n_simulations and n_periods must be > 0"))
        if std_dev < 0:
            return safe_err(ValueError("std_dev must be >= 0"))
        rng = np.random.default_rng()
        steps = rng.normal(loc=mean, scale=std_dev, size=(n_simulations, n_periods))
        paths = np.cumsum(steps, axis=1)
        ending = paths[:, -1]
        p5, p50, p95 = np.percentile(ending, [5, 50, 95]).tolist()
        return [
            ["stat", "value"],
            ["P5", float(p5)],
            ["P50", float(p50)],
            ["P95", float(p95)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func("float[] base_inputs, float low_pct, float high_pct, int steps: object[][]", name="SOV_SCENARIO_TABLE")
def xl_scenario_table(base_inputs: Any, low_pct: float, high_pct: float, steps: int) -> list[list[Any]] | str:
    """Sensitivity table across a range of inputs (scales each base input)."""
    try:
        base = np.array(to_1d_floats(base_inputs), dtype=float)
        if base.size == 0:
            return safe_err(ValueError("Empty base_inputs"))
        if steps <= 1:
            return safe_err(ValueError("steps must be > 1"))
        lo = 1.0 - float(low_pct)
        hi = 1.0 + float(high_pct)
        scales = np.linspace(lo, hi, steps)
        out: list[list[Any]] = [["scale"] + [f"input{i+1}" for i in range(base.size)]]
        for s in scales:
            out.append([float(s)] + [float(x * s) for x in base.tolist()])
        return out
    except Exception as e:
        return safe_err(e)
