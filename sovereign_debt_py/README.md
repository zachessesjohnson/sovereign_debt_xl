# sovereign_debt_py

**sovereign_debt_py** is a pure-Python library for sovereign debt analysis. It is a PyXLL-free mirror of [sovereign_debt_xl](https://github.com/zachessesjohnson/sovereign_debt_xl): every Excel `@xl_func` decorator has been removed and every function is a plain, importable Python callable. Use it in Jupyter notebooks, data pipelines, scripts, Streamlit dashboards, or any Python environment without a Microsoft Excel licence.

The library covers the full workflow of a sovereign debt analyst: descriptive statistics, yield-curve fitting, debt-sustainability projections, contagion modelling, ESG scoring, IMF framework replication, crisis early-warning signals, and much more — 73 functions across 18 analytical modules.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [How Functions Return Data](#how-functions-return-data)
5. [Function Reference](#function-reference)
   - [Averaging & Descriptive Statistics](#averaging--descriptive-statistics)
   - [Indexing & Normalisation](#indexing--normalisation)
   - [Forecasting](#forecasting)
   - [Statistical Modelling](#statistical-modelling)
   - [Utilities](#utilities)
   - [Fiscal Sustainability](#fiscal-sustainability)
   - [Credit Risk](#credit-risk)
   - [Yield Curve](#yield-curve)
   - [Reserves & External Accounts](#reserves--external-accounts)
   - [Stress Testing](#stress-testing)
   - [Amortization & Debt Service](#amortization--debt-service)
   - [Political Risk & ESG](#political-risk--esg)
   - [Contagion & Linkages](#contagion--linkages)
   - [Debt Composition & Transparency](#debt-composition--transparency)
   - [Macro-Financial Vulnerabilities](#macro-financial-vulnerabilities)
   - [Market Microstructure](#market-microstructure)
   - [IMF Framework](#imf-framework)
   - [Event Studies & Early Warning](#event-studies--early-warning)
6. [Error Handling](#error-handling)

---

## Requirements

| Requirement | Version |
|---|---|
| Python | ≥ 3.11 |
| numpy | any recent |
| pandas | any recent |
| scipy | any recent |
| statsmodels | any recent |
| scikit-learn | any recent |

No Excel, no PyXLL, no Windows required.

---

## Installation

```bash
pip install sovereign-debt-py
```

Or install directly from source:

```bash
git clone https://github.com/zachessesjohnson/sovereign_debt_xl
pip install sovereign_debt_xl/sovereign_debt_py/
```

---

## Quick Start

```python
from sovereign_debt_py import (
    xl_weighted_average,
    debt_trajectory_forecast,
    nelson_siegel_fit,
    dsa_replication,
)

# Weighted average of bond yields
avg_yield = xl_weighted_average([5.2, 4.8, 6.1], [1000, 2000, 500])
print(f"Portfolio yield: {avg_yield:.2f}%")  # 5.06%

# 5-year debt trajectory
trajectory = debt_trajectory_forecast(
    gdp_growth_path=[0.03, 0.03, 0.025, 0.025, 0.02],
    primary_balance_path=[0.01, 0.015, 0.015, 0.02, 0.02],
    interest_rate_path=[0.045, 0.045, 0.04, 0.04, 0.04],
    initial_debt_gdp=0.65,
    years=5,
)
for row in trajectory:
    print(row)

# Fit Nelson-Siegel yield curve
ns = nelson_siegel_fit(
    maturities=[0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30],
    yields=[0.052, 0.053, 0.054, 0.055, 0.056, 0.058, 0.060, 0.063, 0.065, 0.066, 0.067],
)
for row in ns:
    print(row)
```

---

## How Functions Return Data

Functions return one of three types:

| Return type | Example functions |
|---|---|
| `float` | `xl_weighted_average`, `implicit_interest_rate`, `zspread` |
| `list[float]` | `xl_rolling_average`, `xl_zscore`, `xl_holt_forecast` |
| `list[list[Any]]` — 2D table | `xl_describe`, `debt_trajectory_forecast`, `dsa_replication` |

For 2D tables, the **first row is always a header** (list of strings). Data rows follow. Example:

```python
result = debt_trajectory_forecast([0.03], [0.01], [0.04], 0.60, 1)
# [['year', 'debt_gdp'], [1, 0.608678]]
header, *data_rows = result
```

On error, functions return a string beginning with `#ERR:` rather than raising an exception.

---

## Function Reference

### Averaging & Descriptive Statistics

---

#### `xl_weighted_average(values, weights) → float`

Computes the arithmetic weighted mean: **Σ(vᵢ × wᵢ) / Σwᵢ**.

| Parameter | Type | Description |
|---|---|---|
| `values` | list or array-like | The data values to average |
| `weights` | list or array-like | Non-negative weights (must be same length as values) |

**Returns:** `float` — the weighted mean. Returns `#ERR:` string on length mismatch or zero total weight.

```python
from sovereign_debt_py import xl_weighted_average

result = xl_weighted_average([5.0, 4.5, 6.2], [2000, 3000, 1000])
print(result)  # 5.033...
```

---

#### `xl_rolling_average(values, window) → list[float]`

Trailing moving average. For each index `i`, averages the `window` most recent non-NaN values. Returns a list the same length as `values`.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Time-series data (NaN values are skipped) |
| `window` | int | Rolling window size (≥ 1) |

**Returns:** `list[float]` — smoothed series.

```python
from sovereign_debt_py import xl_rolling_average

smoothed = xl_rolling_average([1.0, 2.0, 3.0, 4.0, 5.0], 3)
# [1.0, 1.5, 2.0, 3.0, 4.0]
```

---

#### `xl_trimmed_mean(values, trim_pct) → float`

Symmetric trimmed mean: removes the bottom and top `trim_pct` fraction of the sorted observations before averaging. Useful for reducing the influence of outlier spread prints.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Data values |
| `trim_pct` | float | Fraction to trim from each tail; must be in [0, 0.5) |

**Returns:** `float` — trimmed mean.

```python
from sovereign_debt_py import xl_trimmed_mean

result = xl_trimmed_mean([1, 2, 3, 4, 100], trim_pct=0.1)
# Trims the 10% tails, returns roughly 2.75
```

---

#### `xl_describe(values) → list[list]`

Returns an 8-statistic descriptive summary table.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Data values |

**Returns:** 9-row × 2-column table: `[["stat","value"], ["count",N], ["mean",…], ["std",…], ["min",…], ["max",…], ["median",…], ["skewness",…], ["kurtosis",…]]`

- `std` uses sample standard deviation (ddof=1)
- `skewness` and `kurtosis` are Fisher's unbiased estimates (normal kurtosis = 0)

```python
from sovereign_debt_py import xl_describe

stats = xl_describe([1.5, 2.3, 3.1, 2.8, 4.0, 1.9])
for row in stats:
    print(row)
# ['stat', 'value']
# ['count', 6]
# ['mean', 2.6]
# ...
```

---

### Indexing & Normalisation

---

#### `xl_rank_pct(value, values) → float`

Percentile rank of a single value within a reference dataset (0 to 1 scale), using the `"mean"` interpolation method.

| Parameter | Type | Description |
|---|---|---|
| `value` | float | The value to rank |
| `values` | list | The reference population |

**Returns:** `float` in [0, 1].

```python
from sovereign_debt_py import xl_rank_pct

rank = xl_rank_pct(3.0, [1, 2, 3, 4, 5])
# 0.5 (median)
```

---

#### `xl_zscore(values) → list[float]`

Standardises each value: **z = (x − μ) / σ** using sample standard deviation. NaN inputs produce NaN outputs.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Data to standardise |

**Returns:** `list[float]` — z-scores.

```python
from sovereign_debt_py import xl_zscore

zs = xl_zscore([2, 4, 4, 4, 5, 5, 7, 9])
```

---

#### `xl_normalize_minmax(values) → list[float]`

Min-max scaling to [0, 1]: **(x − min) / (max − min)**. Returns all NaN if all values are equal.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Data to normalise |

**Returns:** `list[float]` in [0, 1].

```python
from sovereign_debt_py import xl_normalize_minmax

normed = xl_normalize_minmax([10, 20, 30, 40, 50])
# [0.0, 0.25, 0.5, 0.75, 1.0]
```

---

#### `xl_index_to_base(values, base_period) → list[float]`

Rebases a time series so the value at `base_period` (1-based) equals 100.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Time-series data |
| `base_period` | int | 1-based position of the reference period (= 100) |

**Returns:** `list[float]` — rebased series.

```python
from sovereign_debt_py import xl_index_to_base

indexed = xl_index_to_base([80, 90, 100, 110, 120], base_period=3)
# [80.0, 90.0, 100.0, 110.0, 120.0]
```

---

### Forecasting

---

#### `xl_linear_forecast(x_values, y_values, forecast_x) → float`

Simple OLS linear regression forecast: fits `y = a + b·x` and returns the predicted `y` at `forecast_x`.

| Parameter | Type | Description |
|---|---|---|
| `x_values` | list | Independent variable (e.g. years: 2010, 2011, …) |
| `y_values` | list | Dependent variable (same length) |
| `forecast_x` | float | X value at which to predict |

**Returns:** `float` — predicted y.

```python
from sovereign_debt_py import xl_linear_forecast

pred = xl_linear_forecast(
    x_values=list(range(2010, 2023)),
    y_values=[60, 62, 65, 67, 70, 73, 75, 77, 79, 82, 84, 87, 90],
    forecast_x=2025
)
```

---

#### `xl_exp_smoothing(values, alpha) → list[float]`

Single exponential smoothing: **sₜ = α·xₜ + (1−α)·sₜ₋₁**. The first non-NaN value seeds the process. Handles NaN gaps gracefully.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Time-series data |
| `alpha` | float | Smoothing factor in (0, 1]; higher = reacts faster to new data |

**Returns:** `list[float]` — smoothed series.

```python
from sovereign_debt_py import xl_exp_smoothing

smoothed = xl_exp_smoothing([10, 12, 11, 13, 15, 14, 16], alpha=0.3)
```

---

#### `xl_holt_forecast(values, periods_ahead) → list[float]`

Holt's double exponential smoothing (trend model). Fits a level + additive trend and forecasts `periods_ahead` steps beyond the last observation. Requires ≥ 2 data points.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Historical data (≥ 2 observations) |
| `periods_ahead` | int | Number of future periods to return (≥ 1) |

**Returns:** `list[float]` — length equals `periods_ahead`.

```python
from sovereign_debt_py import xl_holt_forecast

forecast = xl_holt_forecast([60, 63, 66, 70, 74], periods_ahead=5)
# 5-step-ahead Holt forecast
```

---

#### `xl_moving_avg_forecast(values, window, periods_ahead) → list[float]`

Flat forecast using the trailing moving average of the last `window` observations. A simple but robust benchmark.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Historical data |
| `window` | int | Number of trailing periods to average |
| `periods_ahead` | int | Number of identical forecast steps to return |

**Returns:** `list[float]` — all elements equal the trailing average.

```python
from sovereign_debt_py import xl_moving_avg_forecast

forecast = xl_moving_avg_forecast([3.1, 3.2, 3.0, 2.9, 3.1], window=3, periods_ahead=4)
```

---

#### `xl_seasonal_decompose(values, period) → list[list]`

Additive seasonal decomposition using statsmodels. Separates the series into trend, seasonal, and residual components. Requires at least `2 × period` observations and `period > 1`.

| Parameter | Type | Description |
|---|---|---|
| `values` | list | Time-series data |
| `period` | int | Seasonal period (e.g. 4 = quarterly, 12 = monthly) |

**Returns:** Table with header `["trend", "seasonal", "residual"]` followed by T data rows.

```python
from sovereign_debt_py import xl_seasonal_decompose

result = xl_seasonal_decompose(list(range(1, 49)), period=4)
header, *rows = result
```

---

### Statistical Modelling

---

#### `xl_regression(y_values, x_columns) → list[list]`

Multiple OLS regression with automatic intercept. Returns estimated coefficients and R².

| Parameter | Type | Description |
|---|---|---|
| `y_values` | list | Dependent variable (T observations) |
| `x_columns` | 2D list | T × K matrix of regressors (rows = observations, columns = variables) |

**Returns:** Table: `[["term","coef"], ["const", …], ["x1", …], …, ["R2", …]]`

```python
from sovereign_debt_py import xl_regression
import numpy as np

# Regress spread on VIX and US 10Y
n = 100
vix = np.random.uniform(15, 40, n).tolist()
us10y = np.random.uniform(1, 5, n).tolist()
spread = [3 + 0.5*v - 10*r + np.random.normal() for v, r in zip(vix, us10y)]

result = xl_regression(spread, [[v, r] for v, r in zip(vix, us10y)])
for row in result:
    print(row)
```

---

#### `xl_correlation_matrix(data_range) → list[list]`

Pairwise Pearson correlation matrix across the columns of a 2D dataset.

| Parameter | Type | Description |
|---|---|---|
| `data_range` | 2D list | T × N matrix; each column is one variable |

**Returns:** (N+1) × (N+1) table with column/row labels `c1…cN`.

```python
from sovereign_debt_py import xl_correlation_matrix

data = [[1, 2, 3], [2, 2, 4], [3, 3, 3], [4, 5, 2], [5, 4, 1]]
corr = xl_correlation_matrix(data)
```

---

#### `xl_monte_carlo(mean, std_dev, n_simulations, n_periods) → list[list]`

Monte Carlo simulation of N independent paths with normally distributed shocks. Returns P5 / P50 / P95 of the terminal distribution after `n_periods` cumulative steps.

| Parameter | Type | Description |
|---|---|---|
| `mean` | float | Per-period mean shock |
| `std_dev` | float | Per-period standard deviation |
| `n_simulations` | int | Number of simulation paths |
| `n_periods` | int | Number of periods per path |

**Returns:** 4 × 2 table: `[["stat","value"], ["P5",…], ["P50",…], ["P95",…]]`

```python
from sovereign_debt_py import xl_monte_carlo

result = xl_monte_carlo(mean=0.02, std_dev=0.04, n_simulations=5000, n_periods=10)
for row in result:
    print(row)
```

---

#### `xl_scenario_table(base_inputs, low_pct, high_pct, steps) → list[list]`

Sensitivity table: uniformly scales all base inputs from `(1 − low_pct)×base` to `(1 + high_pct)×base` in `steps` steps.

| Parameter | Type | Description |
|---|---|---|
| `base_inputs` | list | Baseline parameter values (e.g. [growth, rate, PB]) |
| `low_pct` | float | Downside scaling (e.g. 0.2 = down to 80%) |
| `high_pct` | float | Upside scaling (e.g. 0.2 = up to 120%) |
| `steps` | int | Number of rows (≥ 2) |

**Returns:** (`steps` + 1) × (K + 1) table with `scale` in the first column.

```python
from sovereign_debt_py import xl_scenario_table

table = xl_scenario_table([0.03, 0.04, 0.01], low_pct=0.2, high_pct=0.2, steps=5)
```

---

### Utilities

---

#### `xl_array_shape(range) → list[list]`

Returns the number of rows and columns of any 2D list.

| Parameter | Type | Description |
|---|---|---|
| `range` | list or 2D list | Input to measure |

**Returns:** `[["rows","cols"], [row_count, col_count]]`

```python
from sovereign_debt_py import xl_array_shape

shape = xl_array_shape([[1,2,3],[4,5,6],[7,8,9]])
# [['rows', 'cols'], [3, 3]]
```

---

#### `xl_flatten(range) → list`

Flattens a 2D list to a 1D list in row-major order.

| Parameter | Type | Description |
|---|---|---|
| `range` | 2D list or scalar | Input to flatten |

**Returns:** `list` — single flat list.

```python
from sovereign_debt_py import xl_flatten

flat = xl_flatten([[1, 2, 3], [4, 5, 6]])
# [1, 2, 3, 4, 5, 6]
```

---

#### `xl_date_diff_bus(start_date, end_date) → int`

Business day count between two dates (inclusive, NETWORKDAYS-style). Accepts Excel serial numbers, ISO date strings, Python `date`, or `datetime` objects.

| Parameter | Type | Description |
|---|---|---|
| `start_date` | date / serial / str | Start date |
| `end_date` | date / serial / str | End date |

**Returns:** `int` — number of business days (negative if end < start).

```python
from sovereign_debt_py import xl_date_diff_bus
from datetime import date

days = xl_date_diff_bus(date(2024, 1, 1), date(2024, 1, 31))
# 23 business days in January 2024
```

---

### Fiscal Sustainability

---

#### `debt_trajectory_forecast(gdp_growth_path, primary_balance_path, interest_rate_path, initial_debt_gdp, years) → list[list]`

Projects debt-to-GDP forward using the standard debt dynamics equation:

> **dₜ = dₜ₋₁ × (1 + r) / (1 + g) − pbₜ**

| Parameter | Type | Description |
|---|---|---|
| `gdp_growth_path` | list | Annual nominal GDP growth rates (e.g. [0.03, 0.03, …]) |
| `primary_balance_path` | list | Annual primary balance as fraction of GDP |
| `interest_rate_path` | list | Annual nominal effective interest rate |
| `initial_debt_gdp` | float | Starting debt-to-GDP (e.g. 0.60 = 60%) |
| `years` | int | Projection horizon; each path must have ≥ `years` elements |

**Returns:** (`years` + 1) × 2 table: `[["year","debt_gdp"], [1, d1], …]`

```python
from sovereign_debt_py import debt_trajectory_forecast

traj = debt_trajectory_forecast(
    gdp_growth_path=[0.03, 0.03, 0.025, 0.025, 0.02],
    primary_balance_path=[0.01, 0.015, 0.015, 0.02, 0.02],
    interest_rate_path=[0.045, 0.045, 0.04, 0.04, 0.04],
    initial_debt_gdp=0.65,
    years=5,
)
for row in traj:
    print(row)
# ['year', 'debt_gdp']
# [1, 0.657...]
# [2, 0.659...]
# ...
```

---

#### `fiscal_reaction_function(primary_balance_history, debt_gdp_history, output_gap_history) → list[list]`

Estimates the Bohn (1998) fiscal reaction function by OLS:

> **pbₜ = α + β·dₜ₋₁ + γ·ogₜ + ε**

A positive `β` on lagged debt is the standard empirical test for fiscal sustainability. Requires ≥ 4 observations.

| Parameter | Type | Description |
|---|---|---|
| `primary_balance_history` | list | Historical primary balance series |
| `debt_gdp_history` | list | Historical debt-to-GDP series |
| `output_gap_history` | list | Historical output gap series |

**Returns:** 5 × 3 table: `[["term","coef","pvalue"], ["const",…], ["lagged_debt",…], ["output_gap",…], ["R2",…]]`

```python
from sovereign_debt_py import fiscal_reaction_function

result = fiscal_reaction_function(
    primary_balance_history=[0.01, 0.02, -0.01, 0.03, 0.02, 0.01],
    debt_gdp_history=[0.60, 0.62, 0.65, 0.64, 0.63, 0.61],
    output_gap_history=[0.01, -0.02, -0.03, 0.01, 0.02, 0.01],
)
```

---

#### `implicit_interest_rate(interest_payments, avg_debt_stock_start, avg_debt_stock_end) → float`

Effective cost of the debt portfolio:

> **r_implicit = interest_payments / ((debt_start + debt_end) / 2)**

| Parameter | Type | Description |
|---|---|---|
| `interest_payments` | float | Total interest paid during the period |
| `avg_debt_stock_start` | float | Debt outstanding at period start |
| `avg_debt_stock_end` | float | Debt outstanding at period end |

**Returns:** `float` — implicit interest rate.

```python
from sovereign_debt_py import implicit_interest_rate

r = implicit_interest_rate(4.5e9, 90e9, 95e9)
# 0.0490... (4.9%)
```

---

#### `debt_stabilizing_primary_balance(debt_gdp, real_interest_rate, real_gdp_growth) → float`

Primary balance required to stabilise the debt-to-GDP ratio:

> **pb\* = d × (r − g) / (1 + g)**

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Debt-to-GDP ratio |
| `real_interest_rate` | float | Real interest rate |
| `real_gdp_growth` | float | Real GDP growth rate |

**Returns:** `float` — debt-stabilising primary balance (positive = surplus needed).

```python
from sovereign_debt_py import debt_stabilizing_primary_balance

pb_star = debt_stabilizing_primary_balance(0.70, 0.025, 0.02)
# 0.034... (3.4% surplus required)
```

---

### Credit Risk

---

#### `merton_sovereign_default_prob(debt_face_value, asset_value, asset_volatility, risk_free_rate, maturity) → list[list]`

Merton (1974) structural model adapted for sovereigns. Treats sovereign assets as a stochastic process and computes the risk-neutral probability that asset value falls below debt face value at maturity.

| Parameter | Type | Description |
|---|---|---|
| `debt_face_value` | float | Par value of outstanding debt |
| `asset_value` | float | Current sovereign asset value |
| `asset_volatility` | float | Annual asset value volatility (e.g. 0.25) |
| `risk_free_rate` | float | Continuous risk-free rate |
| `maturity` | float | Debt maturity in years |

**Returns:** 4 × 2 table: `d1`, `d2_distance_to_default`, `default_probability`.

```python
from sovereign_debt_py import merton_sovereign_default_prob

result = merton_sovereign_default_prob(100, 130, 0.30, 0.04, 5)
for row in result:
    print(row)
# ['metric', 'value']
# ['d1', 1.05...]
# ['d2_distance_to_default', 0.38...]
# ['default_probability', 0.35...]
```

---

#### `cds_implied_default_prob(cds_spread_bps, recovery_rate, tenor_years) → list[list]`

Backs out risk-neutral default probability from a CDS spread using the hazard-rate model:

> **λ = spread / (1 − recovery)**, **P(default < T) = 1 − e^(−λT)**

| Parameter | Type | Description |
|---|---|---|
| `cds_spread_bps` | float | CDS spread in basis points |
| `recovery_rate` | float | Recovery rate in [0, 1) |
| `tenor_years` | float | CDS tenor |

**Returns:** 4 × 2 table: `hazard_rate`, `cumulative_pd`, `annual_pd`.

```python
from sovereign_debt_py import cds_implied_default_prob

result = cds_implied_default_prob(350, 0.40, 5)
# cumulative 5Y PD ≈ 29.7%
```

---

#### `zscore_sovereign(current_account_gdp, reserves_imports, debt_gdp, gdp_growth, inflation) → list[list]`

Composite early-warning z-score model. Standardises five macro indicators against approximate historical benchmarks and returns a composite z-score plus percentile risk rank (higher = more risky).

| Parameter | Type | Description |
|---|---|---|
| `current_account_gdp` | float | CA balance / GDP (negative = deficit) |
| `reserves_imports` | float | Reserves in months of imports |
| `debt_gdp` | float | Debt-to-GDP |
| `gdp_growth` | float | GDP growth rate |
| `inflation` | float | Annual CPI inflation |

**Returns:** Table with per-indicator z-scores, composite z-score, and percentile rank.

```python
from sovereign_debt_py import zscore_sovereign

score = zscore_sovereign(
    current_account_gdp=-0.06,
    reserves_imports=2.5,
    debt_gdp=0.90,
    gdp_growth=0.01,
    inflation=0.15
)
```

---

#### `spread_decomposition(embi_spread, us_vix, us_10y, commodity_index, country_fundamentals) → list[list]`

Decomposes sovereign spreads into global push factors vs. country-specific pull factors via OLS regression.

| Parameter | Type | Description |
|---|---|---|
| `embi_spread` | list | EMBI/CDS spread time series (≥ 5 obs.) |
| `us_vix` | list | VIX index series (same length) |
| `us_10y` | list | US 10-year Treasury yield (same length) |
| `commodity_index` | list | Commodity price index (same length) |
| `country_fundamentals` | list | Country-specific composite indicator (same length) |

**Returns:** Table: coefficients, p-values, R², global and idiosyncratic variance shares.

```python
from sovereign_debt_py import spread_decomposition
import numpy as np

n = 60
result = spread_decomposition(
    embi_spread=np.random.normal(300, 50, n).tolist(),
    us_vix=np.random.normal(20, 5, n).tolist(),
    us_10y=np.random.normal(2.5, 0.5, n).tolist(),
    commodity_index=np.random.normal(100, 10, n).tolist(),
    country_fundamentals=np.random.normal(0, 1, n).tolist(),
)
```

---

### Yield Curve

---

#### `nelson_siegel_fit(maturities, yields) → list[list]`

Fits the Nelson-Siegel (1987) parametric yield curve by minimising sum of squared residuals via L-BFGS-B. Returns the four model parameters and fitted yields. Requires ≥ 3 maturity/yield pairs.

> **y(τ) = β₀ + β₁·((1−e^(−τ/λ))/(τ/λ)) + β₂·((1−e^(−τ/λ))/(τ/λ) − e^(−τ/λ))**

| Parameter | Type | Description |
|---|---|---|
| `maturities` | list | Maturities in years (all > 0) |
| `yields` | list | Observed yields at each maturity |

**Returns:** Table: `beta0_level`, `beta1_slope`, `beta2_curvature`, `tau`, `rmse`, then `[maturity, fitted_yield]` pairs.

```python
from sovereign_debt_py import nelson_siegel_fit

result = nelson_siegel_fit(
    maturities=[0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30],
    yields=[0.052, 0.053, 0.054, 0.055, 0.056, 0.058, 0.060, 0.063, 0.065, 0.066, 0.067],
)
print(result[1])  # ['beta0_level', 0.067...]
print(result[2])  # ['beta1_slope', -0.015...]
print(result[5])  # ['rmse', 0.000...]
```

---

#### `zspread(bond_price, coupon, maturity, benchmark_curve_tenors, benchmark_curve_rates) → float`

Z-spread of a bond over a benchmark curve using continuous compounding and Brent's root-finding method. Face value is assumed to be 100.

| Parameter | Type | Description |
|---|---|---|
| `bond_price` | float | Dirty market price (face = 100) |
| `coupon` | float | Annual coupon in price terms (e.g. 5.0) |
| `maturity` | float | Years to maturity |
| `benchmark_curve_tenors` | list | Tenors of the benchmark curve in years |
| `benchmark_curve_rates` | list | Benchmark rates at each tenor |

**Returns:** `float` — z-spread in decimal (multiply by 10,000 for bps).

```python
from sovereign_debt_py import zspread

z = zspread(
    bond_price=97.5, coupon=4.5, maturity=7,
    benchmark_curve_tenors=[1, 2, 3, 5, 7, 10],
    benchmark_curve_rates=[0.035, 0.037, 0.039, 0.042, 0.044, 0.046],
)
print(f"Z-spread: {z*10000:.1f}bps")
```

---

#### `carry_rolldown(bond_tenor, yield_curve_tenors, yield_curve_rates, horizon_months) → list[list]`

Expected return assuming an unchanged yield curve over a holding period:

- **Carry** = coupon income over the horizon
- **Rolldown** = price gain as bond rolls down the curve

| Parameter | Type | Description |
|---|---|---|
| `bond_tenor` | float | Current years to maturity |
| `yield_curve_tenors` | list | Yield curve tenors in years |
| `yield_curve_rates` | list | Yield curve rates |
| `horizon_months` | int | Holding period in months |

**Returns:** 6 × 2 table: `initial_yield`, `rolled_yield`, `carry`, `rolldown`, `total_return`.

```python
from sovereign_debt_py import carry_rolldown

result = carry_rolldown(
    bond_tenor=10,
    yield_curve_tenors=[1, 2, 5, 10, 20, 30],
    yield_curve_rates=[0.030, 0.035, 0.042, 0.050, 0.055, 0.058],
    horizon_months=12,
)
total = result[-1][1]
print(f"12m carry+rolldown: {total*100:.2f}%")
```

---

#### `asm_spread(bond_price, coupon, maturity, ois_curve_tenors, ois_curve_rates) → float`

Asset-swap spread (ASW) over the OIS curve. Positive value = bond is cheap vs. swaps.

> **ASW = (PV_fixed_at_OIS − Price) / OIS_annuity**

| Parameter | Type | Description |
|---|---|---|
| `bond_price` | float | Dirty price (face = 100) |
| `coupon` | float | Annual coupon amount |
| `maturity` | float | Years to maturity |
| `ois_curve_tenors` | list | OIS curve tenors in years |
| `ois_curve_rates` | list | OIS rates at each tenor |

**Returns:** `float` — ASW in decimal (multiply by 10,000 for bps).

```python
from sovereign_debt_py import asm_spread

asw = asm_spread(
    bond_price=98.5, coupon=5.0, maturity=5,
    ois_curve_tenors=[1, 2, 3, 5, 7],
    ois_curve_rates=[0.029, 0.032, 0.035, 0.039, 0.042],
)
```

---

### Reserves & External Accounts

---

#### `reserves_adequacy_metrics(reserves_usd, short_term_debt, monthly_imports, broad_money, gdp) → list[list]`

Computes four standard reserve adequacy metrics simultaneously.

| Metric | Formula | Benchmark |
|---|---|---|
| Import cover (months) | Reserves / monthly imports | ≥ 3 |
| Greenspan-Guidotti | Reserves / short-term debt | ≥ 1.0 |
| Wijnholds-Kapteyn | Reserves / broad money | — |
| IMF ARA composite | Reserves / (0.3·STD + 0.6·annual_imports + 0.1·M2) | 1.0–1.5 |

| Parameter | Type | Description |
|---|---|---|
| `reserves_usd` | float | Total FX reserves |
| `short_term_debt` | float | Short-term external debt (residual maturity) |
| `monthly_imports` | float | Average monthly imports |
| `broad_money` | float | M2 / broad money |
| `gdp` | float | Annual GDP |

**Returns:** 5 × 2 table with all four metrics.

```python
from sovereign_debt_py import reserves_adequacy_metrics

metrics = reserves_adequacy_metrics(45e9, 20e9, 4e9, 80e9, 150e9)
for row in metrics:
    print(row)
```

---

#### `bop_financing_gap(current_account, fdi, portfolio_flows, debt_amortization, reserves) → float`

Residual BoP financing need:

> **gap = debt_amortization − (CA + FDI + portfolio + reserves_drawdown)**

Positive = unfunded gap that must be covered by new borrowing or IMF program.

| Parameter | Type | Description |
|---|---|---|
| `current_account` | float | Current account balance (positive = surplus) |
| `fdi` | float | Net FDI inflows |
| `portfolio_flows` | float | Net portfolio capital flows |
| `debt_amortization` | float | Scheduled principal repayments |
| `reserves` | float | Reserve change used to finance (positive = drawdown) |

**Returns:** `float` — financing gap.

```python
from sovereign_debt_py import bop_financing_gap

gap = bop_financing_gap(-5e9, 3e9, 1e9, 12e9, 2e9)
# 1e9 = $1bn unfunded
```

---

#### `exchange_rate_misalignment(reer_index, reer_history, terms_of_trade, nfa_gdp) → list[list]`

BEER (Behavioural Equilibrium Exchange Rate) misalignment estimate. Regresses historical REER on fundamentals and compares the current level to the fitted equilibrium.

| Parameter | Type | Description |
|---|---|---|
| `reer_index` | float | Current REER index level |
| `reer_history` | list | Historical REER series (≥ 3 obs.) |
| `terms_of_trade` | list | Terms of trade series (same length) |
| `nfa_gdp` | list | Net foreign assets / GDP series (same length) |

**Returns:** Table: `reer_observed`, `reer_equilibrium`, `misalignment`, `misalignment_pct`, `R2`.

```python
from sovereign_debt_py import exchange_rate_misalignment
import numpy as np

n = 30
result = exchange_rate_misalignment(
    reer_index=108.0,
    reer_history=np.random.normal(100, 5, n).tolist(),
    terms_of_trade=np.random.normal(100, 10, n).tolist(),
    nfa_gdp=np.random.normal(-0.2, 0.05, n).tolist(),
)
```

---

### Stress Testing

---

#### `fan_chart_debt(base_case_params, shock_distributions, num_simulations, years) → list[list]`

Monte Carlo debt fan chart. Simulates `num_simulations` stochastic debt paths, applying independent normal shocks each year to GDP growth, interest rates, and primary balance. Returns P10/P25/P50/P75/P90 paths.

**`base_case_params`:** `[gdp_growth, interest_rate, primary_balance, initial_debt_gdp]`
**`shock_distributions`:** `[gdp_std, rate_std, pb_std]`

| Parameter | Type | Description |
|---|---|---|
| `base_case_params` | list (4 values) | Baseline scenario |
| `shock_distributions` | list (3 values) | Annual shock standard deviations |
| `num_simulations` | int | Simulation paths (e.g. 1000) |
| `years` | int | Projection horizon |

**Returns:** (`years` + 1) × 6 table: `year, p10, p25, p50, p75, p90`.

```python
from sovereign_debt_py import fan_chart_debt

fan = fan_chart_debt(
    base_case_params=[0.03, 0.04, 0.01, 0.65],
    shock_distributions=[0.02, 0.01, 0.01],
    num_simulations=1000,
    years=5,
)
print(fan[0])  # ['year', 'p10', 'p25', 'p50', 'p75', 'p90']
print(fan[5])  # Year 5 distribution
```

---

#### `contingent_liability_shock(debt_gdp, banking_sector_assets_gdp, soe_debt_gdp, historical_realization_rate) → list[list]`

Estimates the debt increase if contingent liabilities crystallise. Applies `historical_realization_rate` to both banking-sector implicit guarantees and SOE debt.

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Baseline public debt-to-GDP |
| `banking_sector_assets_gdp` | float | Banking system assets / GDP |
| `soe_debt_gdp` | float | SOE debt / GDP |
| `historical_realization_rate` | float | Fraction realised in a crisis [0, 1] |

**Returns:** 6 × 2 table: pre/post-shock debt, banking/SOE shock components, total shock.

```python
from sovereign_debt_py import contingent_liability_shock

result = contingent_liability_shock(0.70, 1.20, 0.30, 0.15)
# Total shock ≈ 22.5pp of GDP
```

---

#### `exchange_rate_passthrough_to_debt(fx_denominated_share, debt_gdp, depreciation_pct) → float`

Mechanical increase in debt-to-GDP from currency depreciation:

> **Δd = fx_share × d × depreciation**

| Parameter | Type | Description |
|---|---|---|
| `fx_denominated_share` | float | FX debt / total debt [0, 1] |
| `debt_gdp` | float | Total debt-to-GDP |
| `depreciation_pct` | float | Depreciation magnitude (e.g. 0.30 = 30%) |

**Returns:** `float` — increase in debt-to-GDP ratio.

```python
from sovereign_debt_py import exchange_rate_passthrough_to_debt

delta = exchange_rate_passthrough_to_debt(0.55, 0.70, 0.30)
# 0.1155 → debt/GDP increases by 11.6pp
```

---

### Amortization & Debt Service

---

#### `amortization_profile(bonds_list) → list[list]`

Builds a redemption wall from individual bond records. Aggregates by maturity year and flags years with > 25% of total outstanding as `"HIGH"` concentration.

**Input:** 2-column list `[[maturity_year, face_value], …]`. Optional text header row is auto-skipped.

| Parameter | Type | Description |
|---|---|---|
| `bonds_list` | 2D list | Each row: `[maturity_year, face_value]` |

**Returns:** Table: `year`, `redemption`, `concentration_flag`.

```python
from sovereign_debt_py import amortization_profile

bonds = [
    ["year", "fv"],
    [2025, 5000], [2026, 8000], [2027, 3000],
    [2028, 6000], [2029, 4000], [2025, 2000],
]
profile = amortization_profile(bonds)
for row in profile:
    print(row)
# ['year', 'redemption', 'concentration_flag']
# [2025, 7000.0, 'HIGH']
# ...
```

---

#### `weighted_avg_maturity(bonds_outstanding) → float`

Weighted average maturity of a portfolio by face value:

> **WAM = Σ(maturityᵢ × faceᵢ) / Σfaceᵢ**

| Parameter | Type | Description |
|---|---|---|
| `bonds_outstanding` | 2D list | Each row: `[maturity_years, face_value]` |

**Returns:** `float` — WAM in years.

```python
from sovereign_debt_py import weighted_avg_maturity

wam = weighted_avg_maturity([[3, 1000], [5, 2000], [10, 500]])
# (3×1000 + 5×2000 + 10×500) / 3500 ≈ 5.57 years
```

---

#### `gross_financing_need(amortization_schedule, projected_deficit, year) → float`

Gross financing need for a given year:

> **GFN = amortization[year] + projected_deficit**

| Parameter | Type | Description |
|---|---|---|
| `amortization_schedule` | list | Annual amortization amounts |
| `projected_deficit` | float | Fiscal deficit for the year |
| `year` | int | 1-based year index |

**Returns:** `float` — gross financing need.

```python
from sovereign_debt_py import gross_financing_need

gfn = gross_financing_need([5, 8, 6, 4, 7], projected_deficit=3, year=2)
# 8 + 3 = 11
```

---

### Political Risk & ESG

---

#### `political_risk_score(polity_iv_score, wgi_governance_indicators, years_since_last_default, regime_change_dummy, election_proximity_months) → list[list]`

Composite political risk index (0–100, higher = more risk). Weights: Polity IV 30%, WGI governance 30%, default history 20%, regime change 10%, election proximity 10%.

| Parameter | Type | Description |
|---|---|---|
| `polity_iv_score` | float | Polity IV in [−10, +10] |
| `wgi_governance_indicators` | list | 1–6 WGI scores in [−2.5, +2.5] |
| `years_since_last_default` | float | 0 = currently in default |
| `regime_change_dummy` | float | 1 = recent regime change, 0 = stable |
| `election_proximity_months` | float | Months to next election |

**Returns:** Table with composite score and each component's value and weight.

```python
from sovereign_debt_py import political_risk_score

score = political_risk_score(
    polity_iv_score=4,
    wgi_governance_indicators=[0.5, 0.3, 0.6, 0.4, 0.2, 0.5],
    years_since_last_default=10,
    regime_change_dummy=0,
    election_proximity_months=18,
)
print(score[1])  # ['composite_score_0_100', 38.5]
```

---

#### `esg_sovereign_score(co2_per_capita, renewable_energy_share, gini_coefficient, rule_of_law_index, education_spending_gdp, health_spending_gdp) → list[list]`

Composite sovereign ESG score (0–100, higher = better). Weights: Environmental 20%, Social 35%, Governance 45%.

| Parameter | Type | Description |
|---|---|---|
| `co2_per_capita` | float | CO₂ in tonnes per person |
| `renewable_energy_share` | float | Renewables share [0, 1] |
| `gini_coefficient` | float | Gini [0, 1] or [0, 100] |
| `rule_of_law_index` | float | WB Rule of Law [−2.5, +2.5] |
| `education_spending_gdp` | float | Education spend / GDP |
| `health_spending_gdp` | float | Health spend / GDP |

**Returns:** Table: composite + E/S/G pillar scores + each sub-component.

```python
from sovereign_debt_py import esg_sovereign_score

esg = esg_sovereign_score(4.5, 0.35, 0.32, 0.8, 0.05, 0.06)
print(esg[1])  # ['composite_esg_score', 67.4]
```

---

#### `sanctions_exposure_index(trade_partner_shares, fx_reserves_by_currency_share, swift_dependency_pct, energy_export_share) → list[list]`

Composite sanctions vulnerability score (0–100, equal-weighted). Covers trade concentration, FX reserve concentration, SWIFT payment dependency, and energy export share.

| Parameter | Type | Description |
|---|---|---|
| `trade_partner_shares` | list | Trade share with each partner |
| `fx_reserves_by_currency_share` | list | Reserve allocation by currency |
| `swift_dependency_pct` | float | SWIFT payment share |
| `energy_export_share` | float | Energy / total exports |

**Returns:** 6 × 2 table: composite index and four sub-scores.

```python
from sovereign_debt_py import sanctions_exposure_index

exposure = sanctions_exposure_index(
    trade_partner_shares=[0.4, 0.3, 0.2, 0.1],
    fx_reserves_by_currency_share=[0.5, 0.3, 0.2],
    swift_dependency_pct=0.85,
    energy_export_share=0.60,
)
```

---

### Contagion & Linkages

---

#### `sovereign_contagion_beta(target_country_spreads, source_country_spreads, global_factor_series, window_days) → list[list]`

Rolling bilateral contagion beta. Regresses first-differenced target spread changes on source spread changes and a global factor (e.g. VIX). The rolling coefficient on the source is the contagion beta after controlling for common shocks.

| Parameter | Type | Description |
|---|---|---|
| `target_country_spreads` | list | Daily spread series — the "infected" country (≥ 10 obs.) |
| `source_country_spreads` | list | Daily spread series — the contagion source |
| `global_factor_series` | list | Global risk factor to control for |
| `window_days` | int | Rolling window (≥ 5, < n) |

**Returns:** Summary stats (mean/median/std of beta) + full rolling beta time series.

```python
from sovereign_debt_py import sovereign_contagion_beta
import numpy as np

n = 200
result = sovereign_contagion_beta(
    target_country_spreads=np.cumsum(np.random.normal(0, 5, n)).tolist(),
    source_country_spreads=np.cumsum(np.random.normal(0, 5, n)).tolist(),
    global_factor_series=np.cumsum(np.random.normal(0, 1, n)).tolist(),
    window_days=60,
)
```

---

#### `dcc_garch_correlation(spread_series_a, spread_series_b, window) → list[list]`

Rolling DCC-GARCH approximation between two spread series. Uses RiskMetrics EWMA (λ=0.94) to standardise each series, then computes the rolling correlation of the standardised residuals.

| Parameter | Type | Description |
|---|---|---|
| `spread_series_a` | list | First spread time series (≥ 10 obs.) |
| `spread_series_b` | list | Second spread time series (same length) |
| `window` | int | Rolling correlation window (≥ 5, < n) |

**Returns:** Summary stats (mean/min/max DCC) + full rolling DCC series.

```python
from sovereign_debt_py import dcc_garch_correlation
import numpy as np

n = 150
result = dcc_garch_correlation(
    spread_series_a=np.random.normal(300, 30, n).tolist(),
    spread_series_b=np.random.normal(200, 20, n).tolist(),
    window=40,
)
print(result[1])  # ['mean_dcc', 0.45...]
```

---

#### `granger_causality_spreads(spread_matrix, lags, significance_level) → list[list]`

Pairwise Granger causality test across N sovereign spread series. Entry [i, j] = 1 if country i Granger-causes country j at `significance_level`, using the F-test at the chosen lag.

| Parameter | Type | Description |
|---|---|---|
| `spread_matrix` | 2D list | T × N matrix of spread series (columns = countries; ≥ 10 rows) |
| `lags` | int | VAR lag order |
| `significance_level` | float | p-value threshold (e.g. 0.05) |

**Returns:** (N+1) × (N+1) adjacency matrix.

```python
from sovereign_debt_py import granger_causality_spreads
import numpy as np

spreads = np.random.normal(200, 20, (50, 4)).tolist()
adj = granger_causality_spreads(spreads, lags=2, significance_level=0.05)
```

---

#### `trade_linkage_matrix(bilateral_trade_flows, gdp_values) → list[list]`

Normalised trade exposure matrix. Entry [i, j] = trade(i→j) / GDP(j) — the real-economy vulnerability of country j to stress in country i.

| Parameter | Type | Description |
|---|---|---|
| `bilateral_trade_flows` | 2D list | N × N matrix (rows = exporters, cols = importers) |
| `gdp_values` | list | Length-N GDP vector |

**Returns:** (N+1) × (N+1) table with `exporter\importer` headers.

```python
from sovereign_debt_py import trade_linkage_matrix

flows = [[0, 5, 3], [4, 0, 2], [2, 1, 0]]  # 3-country trade matrix
gdp = [100, 80, 60]
matrix = trade_linkage_matrix(flows, gdp)
```

---

### Debt Composition & Transparency

---

#### `original_sin_index(fx_denominated_debt, total_debt, local_currency_debt_held_by_nonresidents) → list[list]`

Eichengreen-Hausmann currency composition vulnerability metrics.

- **OSin:** FX-denominated / total debt
- **OSin Redux:** LC debt held by non-residents / total LC debt
- **Composite:** simple average

| Parameter | Type | Description |
|---|---|---|
| `fx_denominated_debt` | float | FX-denominated face value |
| `total_debt` | float | Total public debt |
| `local_currency_debt_held_by_nonresidents` | float | LC debt held by foreign investors |

**Returns:** 6 × 2 table.

```python
from sovereign_debt_py import original_sin_index

result = original_sin_index(40e9, 80e9, 15e9)
# OSin = 0.50, OSin_redux = 0.375
```

---

#### `hidden_debt_estimator(reported_public_debt, soe_guaranteed_debt, ppp_commitments, central_bank_quasi_fiscal, local_govt_off_budget) → list[list]`

Augments official debt with off-balance-sheet and contingent exposures (Kose/Nagle/Ohnsorge 2021 framework).

| Parameter | Type | Description |
|---|---|---|
| `reported_public_debt` | float | Official public debt (e.g. as fraction of GDP) |
| `soe_guaranteed_debt` | float | SOE debt with government guarantee |
| `ppp_commitments` | float | PPP payment obligations |
| `central_bank_quasi_fiscal` | float | CB quasi-fiscal losses |
| `local_govt_off_budget` | float | Sub-national off-budget liabilities |

**Returns:** Table: each component, off-balance-sheet total, augmented debt, and hidden debt as % of reported.

```python
from sovereign_debt_py import hidden_debt_estimator

result = hidden_debt_estimator(0.65, 0.10, 0.05, 0.03, 0.08)
# Augmented debt = 0.91 = 91% of GDP
```

---

#### `debt_transparency_score(imf_sdds_subscriber, debt_reporting_frequency, coverage_of_soe, coverage_of_subnational, arrears_reporting) → list[list]`

Data quality score (0–100) for public debt statistics. Flags specific weaknesses.

| Parameter | Type | Description |
|---|---|---|
| `imf_sdds_subscriber` | float | 1 = SDDS subscriber |
| `debt_reporting_frequency` | float | 1 = quarterly; 0.5 = annual; 0 = none |
| `coverage_of_soe` | float | SOE debt coverage [0, 1] |
| `coverage_of_subnational` | float | Sub-national coverage [0, 1] |
| `arrears_reporting` | float | 1 = arrears reported |

**Returns:** Table with composite score, sub-scores, and a `flags` field.

```python
from sovereign_debt_py import debt_transparency_score

score = debt_transparency_score(1, 0.5, 0.7, 0.4, 1)
for row in score:
    print(row)
```

---

#### `collateralized_debt_flag(resource_backed_loans, total_debt, export_revenues, resource_type) → list[list]`

Identifies resource-collateralised borrowing and flags concentration risk (LOW / MEDIUM / HIGH, HIGH if > 25% of debt is resource-backed).

| Parameter | Type | Description |
|---|---|---|
| `resource_backed_loans` | float | Face value of resource-backed loans |
| `total_debt` | float | Total public debt |
| `export_revenues` | float | Annual export revenues |
| `resource_type` | str | Commodity label (e.g. `"oil"`) |

**Returns:** 6 × 2 table: shares, risk flag.

```python
from sovereign_debt_py import collateralized_debt_flag

result = collateralized_debt_flag(8e9, 25e9, 12e9, "oil")
# resource_backed_share = 0.32 → HIGH
```

---

### Macro-Financial Vulnerabilities

---

#### `sovereign_bank_nexus_score(bank_holdings_of_govt_debt, govt_ownership_of_banks, bank_capital_ratio, sovereign_spread_bps) → list[list]`

Doom-loop risk score (0–100, higher = stronger loop). Weights: bank holdings 35%, state ownership 20%, capital resilience 30%, spread stress 15%.

| Parameter | Type | Description |
|---|---|---|
| `bank_holdings_of_govt_debt` | float | Banks' govt bonds / bank assets [0, 1] |
| `govt_ownership_of_banks` | float | State share of banking assets [0, 1] |
| `bank_capital_ratio` | float | Tier-1 capital [0, 1] |
| `sovereign_spread_bps` | float | CDS/EMBI spread in bps |

**Returns:** Table: composite score, `LOW/MEDIUM/HIGH` flag, four sub-scores.

```python
from sovereign_debt_py import sovereign_bank_nexus_score

result = sovereign_bank_nexus_score(0.15, 0.30, 0.12, 280)
print(result[1])  # ['nexus_score_0_100', 49.2]
print(result[2])  # ['doom_loop_flag', 'MEDIUM']
```

---

#### `monetary_financing_risk(central_bank_claims_on_govt, reserve_money_growth, inflation_rate, cb_independence_index) → list[list]`

Monetization risk score (0–100). CB independence mitigates the raw risk score.

| Parameter | Type | Description |
|---|---|---|
| `central_bank_claims_on_govt` | float | CB claims on govt / GDP |
| `reserve_money_growth` | float | Annual M0 growth rate |
| `inflation_rate` | float | Annual CPI inflation |
| `cb_independence_index` | float | CB independence [0, 1] |

**Returns:** Table: score, `LOW/MEDIUM/HIGH` flag, sub-scores.

```python
from sovereign_debt_py import monetary_financing_risk

result = monetary_financing_risk(0.05, 0.20, 0.15, 0.7)
```

---

#### `real_interest_rate_growth_differential(nominal_rate, inflation, real_gdp_growth, years) → list[list]`

Computes the r−g differential time series — the single most important driver of long-run debt dynamics — along with a cumulative rolling average.

| Parameter | Type | Description |
|---|---|---|
| `nominal_rate` | list | Nominal interest rate series |
| `inflation` | list | CPI inflation series (same length) |
| `real_gdp_growth` | list | Real GDP growth series (same length) |
| `years` | int | Number of periods to compute (≤ series length) |

**Returns:** (`years` + 1) × 5 table: `year, r, g, r_minus_g, rolling_avg_rg`.

```python
from sovereign_debt_py import real_interest_rate_growth_differential

result = real_interest_rate_growth_differential(
    nominal_rate=[0.045]*10,
    inflation=[0.025]*10,
    real_gdp_growth=[0.030]*10,
    years=10,
)
# r = 0.02, g = 0.03 → r-g = -0.01 (favourable debt dynamics)
```

---

#### `dollarization_vulnerability(deposit_dollarization_pct, loan_dollarization_pct, fx_reserves_to_fx_deposits) → list[list]`

Balance-sheet mismatch vulnerability for highly dollarized economies (0–100).

| Parameter | Type | Description |
|---|---|---|
| `deposit_dollarization_pct` | float | FX deposits / total deposits [0, 1] |
| `loan_dollarization_pct` | float | FX loans / total loans [0, 1] |
| `fx_reserves_to_fx_deposits` | float | FX reserves / FX deposits coverage ratio |

**Returns:** Table: composite score, `LOW/MEDIUM/HIGH` flag, three sub-scores.

```python
from sovereign_debt_py import dollarization_vulnerability

result = dollarization_vulnerability(0.55, 0.45, 0.80)
```

---

### Market Microstructure

---

#### `bid_ask_liquidity_score(bid_ask_spreads, turnover_ratios, issue_sizes) → list[list]`

Composite sovereign bond curve liquidity score (0–100). Scores each bond on bid-ask tightness (40%), turnover (35%), and issue size (25%), then averages across the curve.

| Parameter | Type | Description |
|---|---|---|
| `bid_ask_spreads` | list | Bid-ask spread per bond in bps (all > 0) |
| `turnover_ratios` | list | Daily turnover / outstanding per bond |
| `issue_sizes` | list | Outstanding face value per bond (USD bn) |

**Returns:** Table: composite score, mean sub-scores, per-bond scores.

```python
from sovereign_debt_py import bid_ask_liquidity_score

result = bid_ask_liquidity_score(
    bid_ask_spreads=[5, 8, 12, 20, 30],
    turnover_ratios=[0.8, 0.6, 0.4, 0.3, 0.2],
    issue_sizes=[15, 12, 8, 5, 3],
)
print(result[1])  # ['composite_liquidity_score', 72.4]
```

---

#### `local_vs_external_curve_basis(local_currency_yields, cross_currency_swap_rates, usd_yields, tenors) → list[list]`

Hedged local-vs-external basis spread across the yield curve.

> **basis = (local_yield − xccy_swap) − USD_yield**

A positive basis indicates local bonds are cheap on a fully hedged basis.

| Parameter | Type | Description |
|---|---|---|
| `local_currency_yields` | list | Local-currency sovereign yield curve |
| `cross_currency_swap_rates` | list | Cross-currency basis swap rates (same length) |
| `usd_yields` | list | USD benchmark yields (same length) |
| `tenors` | list | Tenor vector in years |

**Returns:** Table per tenor + mean basis and relative-value recommendation.

```python
from sovereign_debt_py import local_vs_external_curve_basis

result = local_vs_external_curve_basis(
    local_currency_yields=[0.060, 0.062, 0.065, 0.068, 0.070],
    cross_currency_swap_rates=[0.015, 0.015, 0.014, 0.013, 0.012],
    usd_yields=[0.040, 0.042, 0.044, 0.046, 0.048],
    tenors=[1, 2, 5, 10, 20],
)
```

---

#### `auction_tail_analysis(auction_results, bid_cover_ratios, cutoff_vs_when_issued) → list[list]`

Trend analysis of primary auction demand. OLS trend on tail bps and bid-cover ratios across a series of auctions. Flags `DETERIORATING` if rising tail or falling bid-cover is statistically significant (p < 0.10).

**`auction_results`:** 2-column list `[[date_serial, tail_bps], …]` (≥ 3 rows).

| Parameter | Type | Description |
|---|---|---|
| `auction_results` | 2D list | `[date, tail_bps]` per auction |
| `bid_cover_ratios` | list | Bid-to-cover per auction |
| `cutoff_vs_when_issued` | list | Cutoff minus WI yield in bps |

**Returns:** Summary: means, trend slopes, p-values, `STABLE/DETERIORATING` flag.

```python
from sovereign_debt_py import auction_tail_analysis

result = auction_tail_analysis(
    auction_results=[[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]],
    bid_cover_ratios=[3.5, 3.2, 3.0, 2.8, 2.6],
    cutoff_vs_when_issued=[1, 2, 3, 4, 5],
)
print(result[-1])  # ['demand_flag', 'DETERIORATING']
```

---

#### `investor_base_concentration(holdings_by_type) → list[list]`

Herfindahl-Hirschman Index (HHI) over investor holder categories. A concentrated base raises rollover risk.

| Parameter | Type | Description |
|---|---|---|
| `holdings_by_type` | list | Holdings share or absolute amount per investor type |

**Returns:** Table: `hhi_raw`, `hhi_normalised`, `equivalent_n_holders`, `LOW/MEDIUM/HIGH` flag, per-holder shares.

```python
from sovereign_debt_py import investor_base_concentration

# Domestic banks, foreign real-money, CBs, retail, other
result = investor_base_concentration([0.40, 0.25, 0.15, 0.12, 0.08])
print(result[1])  # ['hhi_raw', 0.258]
print(result[4])  # ['concentration_flag', 'HIGH']
```

---

### IMF Framework

---

#### `dsa_replication(gdp_path, fiscal_path, interest_path, exchange_rate_path, financing_assumptions) → list[list]`

IMF Debt Sustainability Analysis (DSA) replication. Runs the baseline trajectory plus five standardised stress tests simultaneously.

**Input layout:**
- `gdp_path`: `[d₀, g₁, g₂, …]` (initial debt + annual growth)
- `fiscal_path`: `[pb₁, pb₂, …]`
- `interest_path`: `[r₁, r₂, …]`
- `exchange_rate_path`: `[fx_share, dep₁, dep₂, …]`
- `financing_assumptions`: `[std_g, std_pb, std_r]`

| Stress | Shock description |
|---|---|
| Growth | −1 std dev on g each year |
| Primary balance | −1 std dev on pb each year |
| Interest rate | +1 std dev on r each year |
| FX | 30% depreciation in year 1 only |
| Combined | All four at 50% magnitude |

**Returns:** (`years` + 1) × 7 table: `year, baseline, growth_shock, pb_shock, rate_shock, fx_shock, combined`.

```python
from sovereign_debt_py import dsa_replication

result = dsa_replication(
    gdp_path=[0.65, 0.03, 0.03, 0.03, 0.025, 0.025],
    fiscal_path=[0.01, 0.015, 0.015, 0.02, 0.02],
    interest_path=[0.045, 0.045, 0.04, 0.04, 0.04],
    exchange_rate_path=[0.45, 0.0, 0.0, 0.0, 0.0, 0.0],
    financing_assumptions=[0.02, 0.01, 0.01],
)
print(result[0])  # ['year', 'baseline', 'growth_shock', ...]
for row in result[1:]:
    print(row)
```

---

#### `imf_program_probability(reserves_months_imports, debt_gdp, current_account_gdp, inflation, exchange_rate_regime, political_stability) → float`

Logistic regression model for the 24-month probability of IMF program entry, calibrated on literature estimates.

| Parameter | Type | Description |
|---|---|---|
| `reserves_months_imports` | float | Import cover in months |
| `debt_gdp` | float | Debt-to-GDP |
| `current_account_gdp` | float | CA / GDP (negative = deficit) |
| `inflation` | float | Annual CPI inflation |
| `exchange_rate_regime` | float | 1 = fixed peg; 0 = flexible |
| `political_stability` | float | WB Political Stability [−2.5, +2.5] |

**Returns:** `float` — probability in [0, 1].

```python
from sovereign_debt_py import imf_program_probability

prob = imf_program_probability(
    reserves_months_imports=2.0,
    debt_gdp=0.90,
    current_account_gdp=-0.07,
    inflation=0.12,
    exchange_rate_regime=1.0,
    political_stability=-0.8,
)
print(f"IMF program probability: {prob*100:.1f}%")
```

---

#### `exceptional_access_criteria_check(debt_gdp, gross_financing_need_gdp, market_access_boolean, debt_sustainability_assessment) → list[list]`

Evaluates the IMF's four exceptional access criteria (2016 framework).

| Criterion | Test |
|---|---|
| 1. BoP need | GFN/GDP > 15% |
| 2. Debt sustainability | DSA assessment is "SUSTAINABLE" |
| 3. Market access | `market_access_boolean` ≥ 0.5 |
| 4. Program success | Debt/GDP < 150% |

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Debt-to-GDP |
| `gross_financing_need_gdp` | float | GFN as fraction of GDP |
| `market_access_boolean` | float | 1 = market access; 0 = no access |
| `debt_sustainability_assessment` | str | `"SUSTAINABLE"`, `"YES"`, `"TRUE"`, or `"1"` |

**Returns:** 6 × 3 table: criterion, `PASS/FAIL`, description, and overall row.

```python
from sovereign_debt_py import exceptional_access_criteria_check

result = exceptional_access_criteria_check(1.20, 0.22, 0, "SUSTAINABLE")
for row in result:
    print(row)
```

---

#### `sdrs_allocation_impact(sdr_allocation, gdp, reserves, import_cover_pre) → list[list]`

Measures the improvement in reserve adequacy from a new SDR allocation.

| Parameter | Type | Description |
|---|---|---|
| `sdr_allocation` | float | New SDR allocation (same currency as reserves/GDP) |
| `gdp` | float | GDP |
| `reserves` | float | Pre-allocation reserves |
| `import_cover_pre` | float | Pre-allocation import cover (months) |

**Returns:** 4-row table: reserves, reserves/GDP %, import cover — pre-allocation, post-allocation, and change.

```python
from sovereign_debt_py import sdrs_allocation_impact

result = sdrs_allocation_impact(2e9, 50e9, 8e9, 2.1)
for row in result:
    print(row)
```

---

### Event Studies & Early Warning

---

#### `restructuring_comparables(debt_gdp, spread_bps, reserves_months, haircut_comparables) → list[list]`

Nearest-neighbour matching against 15 canonical historical restructuring episodes (Argentina 2001, Greece 2012, Ecuador 1999, Russia 1998, Ukraine 2015, etc.) using normalised Euclidean distance on pre-crisis fundamentals. Returns the top-5 closest matches and distance-weighted average outcomes.

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Current debt-to-GDP |
| `spread_bps` | float | Current sovereign spread in bps |
| `reserves_months` | float | Current import cover in months |
| `haircut_comparables` | float | (Reserved for future use; pass 0) |

**Returns:** Table of top-5 episodes with haircut %, recovery %, months to resolution, and distance, plus weighted-average summary row.

```python
from sovereign_debt_py import restructuring_comparables

result = restructuring_comparables(
    debt_gdp=1.10,
    spread_bps=3200,
    reserves_months=1.5,
    haircut_comparables=0,
)
print(result[0])  # Header
for row in result[1:6]:
    print(row)
print(result[-1])  # Weighted averages
```

---

#### `event_study_spread_reaction(spread_series, event_dates_serial, window_before, window_after) → list[list]`

Computes the average abnormal spread change around a set of events with 95% confidence bands. For each event, the pre-event mean is used as a baseline; abnormal changes are averaged across all usable events.

| Parameter | Type | Description |
|---|---|---|
| `spread_series` | list | Daily spread time series |
| `event_dates_serial` | list | 0-based indices of event days within the spread series |
| `window_before` | int | Pre-event baseline window length in days (≥ 1) |
| `window_after` | int | Post-event tracking window in days (≥ 1) |

**Returns:** Table: `day_rel_event`, `mean_abnormal_spread`, `ci95_lower`, `ci95_upper` + `n_events_used`.

```python
from sovereign_debt_py import event_study_spread_reaction
import numpy as np

spreads = np.random.normal(300, 20, 500).tolist()
events = [100, 200, 300, 400]

result = event_study_spread_reaction(spreads, events, window_before=20, window_after=10)
for row in result:
    print(row)
```

---

#### `crisis_early_warning_signal(indicator_values, thresholds) → list[list]`

Kaminsky-Lizondo-Reinhart (1999) signal extraction. Issues a binary signal for each indicator that breaches its threshold. Returns a composite traffic-light assessment.

| Signal ratio | Traffic light |
|---|---|
| ≥ 60% | 🔴 RED |
| 30–59% | 🟡 AMBER |
| < 30% | 🟢 GREEN |

| Parameter | Type | Description |
|---|---|---|
| `indicator_values` | list | Current values for each indicator |
| `thresholds` | list | Crisis threshold per indicator (same length) |

**Returns:** Table: n_indicators, n_signals, signal_ratio, noise-to-signal ratio, traffic light, then per-indicator flag rows.

```python
from sovereign_debt_py import crisis_early_warning_signal

# 7 standard KLR indicators vs. their thresholds
indicators = [0.06, 2.5, 0.90, 0.01, 0.15, 0.55, 0.80]
thresholds = [0.04, 3.0, 0.80, 0.03, 0.10, 0.50, 0.60]

result = crisis_early_warning_signal(indicators, thresholds)
print(result[5])  # ['traffic_light', 'RED']
```

---

## Error Handling

All functions return an error string beginning with `#ERR:` rather than raising an exception. Check for errors like this:

```python
from sovereign_debt_py import xl_weighted_average

result = xl_weighted_average([1, 2, 3], [1, 2])  # mismatched lengths
if isinstance(result, str) and result.startswith("#ERR"):
    print(f"Input error: {result}")
else:
    print(f"Result: {result}")
```

Common error messages:

| Error | Cause |
|---|---|
| `#ERR: Empty values` | Input list is empty or all NaN |
| `#ERR: values and weights must have same length` | Mismatched array lengths |
| `#ERR: window must be > 0` | Non-positive window |
| `#ERR: All maturities must be positive` | Zero/negative tenor |
| `#ERR: …must be in [0, 1]` | Probability or share out of range |
| `#ERR: Need at least N observations` | Insufficient data for the method |

