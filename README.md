# sovereign_debt_xl

**sovereign_debt_xl** is a [PyXLL](https://www.pyxll.com/) add-in that exposes a suite of sovereign debt analysis functions directly inside Microsoft Excel as User-Defined Functions (UDFs). Write `=SOV_DEBT_TRAJECTORY(...)` in a cell and get a live, recalculating debt-sustainability table — no VBA, no copy-pasting from Python, no context switching.

The library covers the full workflow of a sovereign debt analyst: from descriptive statistics and yield-curve fitting through IMF DSA replication, contagion modelling, ESG scoring, and crisis early-warning.

---

## Table of Contents

- [Project layout](#project-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [PyXLL configuration](#pyxll-configuration)
- [Function reference](#function-reference)
  - [Averaging & statistics](#averaging--statistics)
  - [Indexing & normalisation](#indexing--normalisation)
  - [Forecasting](#forecasting)
  - [Modelling utilities](#modelling-utilities)
  - [Utilities](#utilities)
  - [Fiscal sustainability](#fiscal-sustainability)
  - [Credit risk](#credit-risk)
  - [Yield curve](#yield-curve)
  - [Reserves & external sector](#reserves--external-sector)
  - [Stress testing](#stress-testing)
  - [Amortisation & financing](#amortisation--financing)
  - [Political risk & ESG](#political-risk--esg)
  - [Contagion](#contagion)
  - [Debt composition](#debt-composition)
  - [Macro-financial linkages](#macro-financial-linkages)
  - [Market microstructure](#market-microstructure)
  - [IMF framework](#imf-framework)
  - [Event studies](#event-studies)
  - [Plotting (inline charts)](#plotting-inline-charts)
- [Running tests](#running-tests)

---

## Project layout

```
sovereign_debt_xl/           ← repo root
├── sovereign_debt_xl/       ← installable Python package
│   ├── __init__.py          ← re-exports every submodule
│   ├── _coerce.py           ← internal input-coercion helpers
│   ├── amortization.py
│   ├── averaging.py
│   ├── contagion.py
│   ├── credit_risk.py
│   ├── debt_composition.py
│   ├── event_studies.py
│   ├── fiscal.py
│   ├── forecasting.py
│   ├── imf_framework.py
│   ├── indexing.py
│   ├── macro_financial.py
│   ├── market_microstructure.py
│   ├── modeling.py
│   ├── plots.py             ← inline Matplotlib chart UDFs
│   ├── political_esg.py
│   ├── reserves.py
│   ├── stress.py
│   ├── utils.py
│   └── yield_curve.py
├── test_*.py                ← pytest test suite (repo root)
├── conftest.py              ← pyxll mock for tests
├── pyproject.toml
├── pyxll.cfg
└── requirements.txt
```

All source code lives inside `sovereign_debt_xl/` so that `pip install -e .` correctly packages the module.  Tests remain at the repo root so pytest discovers them automatically.
1. [Requirements](#requirements)
2. [Installation & PyXLL Setup](#installation--pyxll-setup)
3. [How Excel Array Formulas Work Here](#how-excel-array-formulas-work-here)
4. [Function Reference](#function-reference)
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
   - [Inline Charts (Plotting)](#inline-charts-plotting)
5. [Error Handling](#error-handling)
6. [Running the Tests](#running-the-tests)
7. [sovereign\_debt\_py plotting](#sovereign_debt_py-plotting)
8. [Extracting sovereign\_debt\_py](#extracting-sovereign_debt_py)

---

## Requirements

- Python ≥ 3.11
- [PyXLL](https://www.pyxll.com/) (Excel add-in runtime; not required for running tests)
- Python dependencies (installed automatically via `pip install`):
  - `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`

---

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install the package in editable mode
pip install -e .
```

`pyproject.toml` declares `sovereign_debt_xl` as the package root so setuptools will find and install everything under `sovereign_debt_xl/`.

---

## PyXLL configuration

`pyxll.cfg` loads the entire package through a single entry:

```ini
[PYXLL]
modules=
    sovereign_debt_xl
```

`sovereign_debt_xl/__init__.py` re-exports every submodule, so PyXLL discovers all UDFs automatically when the add-in loads.

---

## Function reference

All UDFs follow two naming conventions:

| Prefix | Scope |
|--------|-------|
| `SOV_` | Analytic / numerical functions that return values or arrays |
| `SDXL_PLOT_` | Plotting functions that return an inline PNG image |

### Averaging & statistics

| Function | Description |
|----------|-------------|
| `SOV_WEIGHTED_AVERAGE(values, weights)` | Weighted arithmetic mean |
| `SOV_ROLLING_AVERAGE(values, window)` | Rolling / moving average |
| `SOV_TRIMMED_MEAN(values, trim_pct)` | Mean after trimming extreme percentiles |
| `SOV_DESCRIBE(values)` | Descriptive statistics table (count, mean, std, min, max, …) |

### Indexing & normalisation

| Function | Description |
|----------|-------------|
| `SOV_RANK_PCT(values)` | Rank each value as a percentile |
| `SOV_ZSCORE(values)` | Z-score standardisation |
| `SOV_NORMALIZE_MINMAX(values)` | Min-max normalisation to [0, 1] |
| `SOV_INDEX_TO_BASE(values, base_period)` | Rebase a series to a chosen base period = 100 |

### Forecasting

| Function | Description |
|----------|-------------|
| `SOV_LINEAR_FORECAST(x, y, x_new)` | OLS linear regression forecast |
| `SOV_EXP_SMOOTHING(values, alpha)` | Simple exponential smoothing |
| `SOV_HOLT_FORECAST(values, periods_ahead)` | Holt double-exponential smoothing forecast (α and β fitted automatically) |
| `SOV_MOVING_AVG_FORECAST(values, window, periods)` | Moving-average extrapolation |
| `SOV_SEASONAL_DECOMPOSE(values, period)` | Seasonal decomposition (trend + seasonal + residual) |

### Modelling utilities

| Function | Description |
|----------|-------------|
| `SOV_REGRESSION(y, x_matrix)` | OLS regression; returns coefficients and R² |
| `SOV_CORRELATION_MATRIX(data_matrix)` | Pairwise correlation matrix |
| `SOV_MONTE_CARLO(mean, std, n_sims, n_steps)` | Monte Carlo path simulation |
| `SOV_SCENARIO_TABLE(base, shocks)` | Scenario analysis table |

### Utilities

| Function | Description |
|----------|-------------|
| `SOV_ARRAY_SHAPE(range)` | Return `{rows, cols}` of an Excel range |
| `SOV_FLATTEN(range)` | Flatten a 2-D range to a single column |
| `SOV_DATE_DIFF_BUS(start_date, end_date)` | Business-day count between two dates |

### Fiscal sustainability

| Function | Description |
|----------|-------------|
| `SOV_DEBT_TRAJECTORY(debt_gdp, r, g, primary_balance, years)` | Simulate debt-to-GDP path under r–g and primary balance assumptions |
| `SOV_FISCAL_REACTION(debt_gdp, output_gap)` | Estimate fiscal reaction function coefficient |
| `SOV_IMPLICIT_INTEREST_RATE(interest_payments, debt_stock)` | Implicit (effective) interest rate on public debt |
| `SOV_DEBT_STABILIZING_PB(debt_gdp, r, g)` | Primary balance required to stabilise debt ratio |

### Credit risk

| Function | Description |
|----------|-------------|
| `SOV_MERTON_DEFAULT_PROB(asset_value, debt, volatility, r, T)` | Merton structural probability of default |
| `SOV_CDS_DEFAULT_PROB(cds_spread, recovery_rate)` | Risk-neutral default probability from CDS spread |
| `SOV_ZSCORE_SOVEREIGN(financials)` | Altman-style Z-score adapted for sovereign issuers |
| `SOV_SPREAD_DECOMPOSITION(spread, risk_free, liquidity_premium)` | Decompose spread into credit, liquidity, and other components |

### Yield curve

| Function | Description |
|----------|-------------|
| `SOV_NELSON_SIEGEL(tenors, beta0, beta1, beta2, tau)` | Nelson-Siegel yield curve fit |
| `SOV_ZSPREAD(cashflows, schedule, price, risk_free_curve)` | Z-spread to the risk-free curve |
| `SOV_CARRY_ROLLDOWN(tenors, yields, holding_period)` | Carry-and-roll-down return estimate |
| `SOV_ASW_SPREAD(coupon, maturity, price, swap_curve)` | Asset-swap spread calculation |

### Reserves & external sector

| Function | Description |
|----------|-------------|
| `SOV_RESERVES_ADEQUACY(reserves, imports, st_debt, m2)` | IMF ARA metric — composite reserve adequacy ratio |
| `SOV_BOP_FINANCING_GAP(current_account, fdi, portfolio, amortisation)` | Balance-of-payments financing gap |
| `SOV_FX_MISALIGNMENT(real_exchange_rate, fundamentals)` | REER misalignment from estimated equilibrium |

### Stress testing

| Function | Description |
|----------|-------------|
| `SOV_FAN_CHART_DEBT(baseline, shocks, periods, n_sims)` | Monte Carlo fan chart for debt trajectory |
| `SOV_CONTINGENT_LIABILITY_SHOCK(debt_gdp, shock_size, gdp_impact)` | One-off shock to debt ratio from contingent liabilities |
| `SOV_FX_PASSTHROUGH_DEBT(fx_debt_share, depreciation, debt_gdp)` | Debt ratio impact of exchange-rate depreciation |

### Amortisation & financing

| Function | Description |
|----------|-------------|
| `SOV_AMORTIZATION_PROFILE(bonds_list)` | Amortisation schedule from a list of bond maturities and amounts |
| `SOV_WEIGHTED_AVG_MATURITY(bonds_outstanding)` | Weighted average maturity of debt portfolio |
| `SOV_GROSS_FINANCING_NEED(deficit, amortisation)` | Annual gross financing need |

### Political risk & ESG

| Function | Description |
|----------|-------------|
| `SOV_POLITICAL_RISK_SCORE(indicators)` | Composite political-risk score |
| `SOV_ESG_SOVEREIGN_SCORE(e, s, g, weights)` | Weighted ESG score for a sovereign |
| `SOV_SANCTIONS_EXPOSURE(trade_matrix, sanctioned_countries)` | Bilateral trade-weighted sanctions-exposure index |

### Contagion

| Function | Description |
|----------|-------------|
| `SOV_CONTAGION_BETA(target_spreads, peer_spreads)` | OLS contagion beta of target vs peer spreads |
| `SOV_DCC_GARCH_CORR(series_a, series_b)` | DCC-GARCH dynamic conditional correlation |
| `SOV_GRANGER_CAUSALITY(y, x, max_lags)` | Granger-causality p-value between spread series |
| `SOV_TRADE_LINKAGE_MATRIX(trade_flows)` | Normalised bilateral trade-linkage matrix |

### Debt composition

| Function | Description |
|----------|-------------|
| `SOV_ORIGINAL_SIN_INDEX(fx_debt, local_debt)` | Original-sin index (share of FX-denominated debt) |
| `SOV_HIDDEN_DEBT_ESTIMATOR(reported, off_balance)` | Estimate of unreported / hidden debt obligations |
| `SOV_DEBT_TRANSPARENCY_SCORE(disclosure_flags)` | Debt-transparency score from creditor-disclosure indicators |
| `SOV_COLLATERALIZED_DEBT_FLAG(collateral_value, debt_amount)` | Flag bonds with collateralised structures |

### Macro-financial linkages

| Function | Description |
|----------|-------------|
| `SOV_BANK_NEXUS_SCORE(bank_holdings, total_assets)` | Sovereign-bank nexus concentration score |
| `SOV_MONETARY_FINANCING_RISK(central_bank_claims, gdp)` | Monetary-financing-risk ratio |
| `SOV_RG_DIFFERENTIAL(real_rate, real_growth)` | r–g differential driving debt dynamics |
| `SOV_DOLLARIZATION_VULNERABILITY(fx_liabilities, total_liabilities)` | Dollarisation vulnerability index |

### Market microstructure

| Function | Description |
|----------|-------------|
| `SOV_BID_ASK_LIQUIDITY_SCORE(bid, ask, mid)` | Normalised bid-ask liquidity score |
| `SOV_LOCAL_VS_EXTERNAL_BASIS(local_yield, external_yield, fx_forward)` | Local-vs-external basis after FX hedging |
| `SOV_AUCTION_TAIL_ANALYSIS(bids, allotment)` | Auction tail (yield spread between average and cut-off) |
| `SOV_INVESTOR_BASE_CONCENTRATION(holdings_by_type)` | Herfindahl–Hirschman investor-base concentration index |

### IMF framework

| Function | Description |
|----------|-------------|
| `SOV_DSA_REPLICATION(debt_gdp, r, g, pb_path)` | Replicate IMF debt sustainability analysis (DSA) projection |
| `SOV_IMF_PROGRAM_PROBABILITY(macro_indicators)` | Probability of an IMF programme request |
| `SOV_EXCEPTIONAL_ACCESS_CHECK(debt_gdp, financing_gap, market_access)` | IMF exceptional-access criteria checklist |
| `SOV_SDRS_ALLOCATION_IMPACT(quota_share, sdr_allocation)` | Impact of SDR allocation on reserve adequacy |

### Event studies

| Function | Description |
|----------|-------------|
| `SOV_RESTRUCTURING_COMPARABLES(debt_gdp, gdp_growth, comparables)` | Comparable restructuring case analysis |
| `SOV_EVENT_STUDY_SPREAD(spreads, event_date, window)` | Abnormal spread reaction around an event date |
| `SOV_CRISIS_EARLY_WARNING(macro_panel)` | Early-warning signal from macro vulnerability indicators |

### Plotting (inline charts)

These functions render a Matplotlib chart to PNG and return it as a **PyXLL inline image** — the chart appears directly inside the Excel cell that holds the formula.  Outputs are LRU-cached (up to 128 entries) so recalculation is fast.

| Function | Description |
|----------|-------------|
| `SDXL_PLOT_YIELD_CURVE(tenors, yields, [title], [x_label], [y_label], [width_px], [height_px], [style])` | Plot a yield curve; `style` is `"line"` (default) or `"markers"` |
| `SDXL_PLOT_TIMESERIES(dates, values, [title], [width_px], [height_px])` | Plot a time series; dates accept Excel serials, ISO strings, or date objects |
| `SDXL_PLOT_ROLLING_AVG(dates, values, window, [title], [width_px], [height_px])` | Plot raw data with a rolling-average overlay; `window` is the number of periods (default 20) |

**Example formulas:**

```excel
=SDXL_PLOT_YIELD_CURVE(A2:A10, B2:B10, "UST Curve")
=SDXL_PLOT_TIMESERIES(A2:A300, B2:B300, "10yr UST Yield")
=SDXL_PLOT_ROLLING_AVG(A2:A300, B2:B300, 20, "Rolling Avg (20d)")
```

Error conditions (mismatched lengths, empty input) return an `#SDXL:` prefixed string so Excel can display a readable error in the cell.

---

## Running tests

The test suite uses [pytest](https://pytest.org/) and mocks the `pyxll` runtime via `conftest.py`, so no Excel or PyXLL installation is required.

```bash
# Install dependencies and the package
pip install -r requirements.txt
pip install -e ".[dev]"

# Run all tests from the repo root
python -m pytest
```

Test files mirror the module they cover (`test_averaging.py` → `averaging.py`, `test_plots.py` → `plots.py`, etc.) and live at the repo root alongside `conftest.py`.
| Requirement | Version |
|---|---|
| Python | ≥ 3.11 |
| PyXLL | ≥ 5.9 |
| Microsoft Excel | 2016+ or Microsoft 365 |
| numpy | any recent |
| pandas | any recent |
| scipy | any recent |
| statsmodels | any recent |
| scikit-learn | any recent |
| matplotlib | any recent |

---

## Installation & PyXLL Setup

```bash
# 1. Install Python dependencies
pip install numpy pandas scipy statsmodels scikit-learn matplotlib pyxll

# 2. Install this package
pip install -e .

# 3. Point pyxll.cfg at the package
```

Edit `pyxll.cfg` (typically `%APPDATA%\PyXLL\pyxll.cfg`) to include the module paths:

```ini
[PYXLL]
modules =
    sovereign_debt_xl.averaging
    sovereign_debt_xl.indexing
    sovereign_debt_xl.forecasting
    sovereign_debt_xl.modeling
    sovereign_debt_xl.utils
    sovereign_debt_xl.fiscal
    sovereign_debt_xl.credit_risk
    sovereign_debt_xl.yield_curve
    sovereign_debt_xl.reserves
    sovereign_debt_xl.stress
    sovereign_debt_xl.amortization
    sovereign_debt_xl.political_esg
    sovereign_debt_xl.contagion
    sovereign_debt_xl.debt_composition
    sovereign_debt_xl.macro_financial
    sovereign_debt_xl.market_microstructure
    sovereign_debt_xl.imf_framework
    sovereign_debt_xl.event_studies
    sovereign_debt_xl.plots
```

Restart Excel. All `SOV_*` functions will appear in the function wizard.

---

## How Excel Array Formulas Work Here

Functions that return a **table** (multi-row, multi-column result) must be entered as a **dynamic array** or legacy **Ctrl+Shift+Enter** array formula:

- **Microsoft 365 / Excel 2019+:** Just press **Enter** — the result spills automatically.
- **Excel 2016:** Select the destination range first, type the formula, then press **Ctrl+Shift+Enter**.

Functions that return a **single number** or a **1-D column** can be entered normally or as array formulas.

---

## Function Reference

### Averaging & Descriptive Statistics

---

#### `SOV_WEIGHTED_AVERAGE`
**Python:** `xl_weighted_average(values, weights)`

Computes the arithmetic weighted mean: `Σ(vᵢ × wᵢ) / Σwᵢ`.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | The data values to average |
| `weights` | float range | Corresponding weights (must be same length as values) |

**Returns:** A single `float` — the weighted mean.

**Excel example:**
```
=SOV_WEIGHTED_AVERAGE(B2:B10, C2:C10)
```
where column B holds yield spreads and column C holds face-value weights.

---

#### `SOV_ROLLING_AVERAGE`
**Python:** `xl_rolling_average(values, window)`

Computes a trailing moving average. For each position `i`, averages the `window` most recent non-NaN values ending at `i`. Returns a column array the same length as `values`.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Time-series data |
| `window` | integer | Number of periods in the rolling window (must be ≥ 1) |

**Returns:** A column of `float` — smoothed values.

**Excel example (array, spills into E2:E13):**
```
=SOV_ROLLING_AVERAGE(D2:D13, 3)
```

---

#### `SOV_TRIMMED_MEAN`
**Python:** `xl_trimmed_mean(values, trim_pct)`

Computes the mean after symmetrically removing the bottom and top `trim_pct` fraction of observations — useful for reducing the influence of outlier spreads.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Data values |
| `trim_pct` | float | Fraction to trim from each tail; must be in [0, 0.5) |

**Returns:** A single `float` — the trimmed mean.

**Excel example:**
```
=SOV_TRIMMED_MEAN(B2:B50, 0.1)
```
Trims the bottom 10% and top 10% before averaging.

---

#### `SOV_DESCRIBE`
**Python:** `xl_describe(values)`

Returns an 9-row × 2-column descriptive statistics table: count, mean, standard deviation, min, max, median, skewness, and excess kurtosis.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Data values |

**Returns:** A 2D table with headers `["stat", "value"]`.

| Row | Statistic | Notes |
|---|---|---|
| 1 | count | Number of non-NaN values |
| 2 | mean | Arithmetic mean |
| 3 | std | Sample standard deviation (ddof=1) |
| 4 | min | Minimum |
| 5 | max | Maximum |
| 6 | median | 50th percentile |
| 7 | skewness | Fisher's unbiased skew |
| 8 | kurtosis | Excess kurtosis (normal = 0) |

**Excel example (select 9 × 2 cells, Ctrl+Shift+Enter):**
```
=SOV_DESCRIBE(B2:B100)
```

---

### Indexing & Normalisation

---

#### `SOV_RANK_PCT`
**Python:** `xl_rank_pct(value, values)`

Returns the percentile rank (0 to 1) of a single value within a reference dataset, using the `"mean"` interpolation method (equivalent to Excel's PERCENTRANK.INC).

| Parameter | Type | Description |
|---|---|---|
| `value` | float | The value to rank |
| `values` | float range | The reference population |

**Returns:** A single `float` in [0, 1].

**Excel example:**
```
=SOV_RANK_PCT(B2, $B$2:$B$50)
```
Returns where B2 sits in the distribution of B2:B50.

---

#### `SOV_ZSCORE`
**Python:** `xl_zscore(values)`

Standardises each value in a range: `z = (x − μ) / σ` using sample standard deviation. NaN inputs produce NaN outputs. Returns a column array the same length as the input.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Data values to standardise |

**Returns:** Column of `float` — z-scores.

**Excel example:**
```
=SOV_ZSCORE(B2:B50)
```

---

#### `SOV_NORMALIZE_MINMAX`
**Python:** `xl_normalize_minmax(values)`

Scales values to [0, 1] using min-max normalisation: `(x − min) / (max − min)`. If all values are equal, returns NaN for all.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Data values to normalise |

**Returns:** Column of `float` in [0, 1].

**Excel example:**
```
=SOV_NORMALIZE_MINMAX(B2:B50)
```

---

#### `SOV_INDEX_TO_BASE`
**Python:** `xl_index_to_base(values, base_period)`

Rebases a time series so that the value at `base_period` equals 100. Useful for comparing GDP growth paths, yield levels, or debt ratios across countries from a common starting point.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Time-series data |
| `base_period` | integer | 1-based index of the period that becomes 100 |

**Returns:** Column of `float` — rebased index values.

**Excel example:**
```
=SOV_INDEX_TO_BASE(B2:B20, 1)
```
Sets B2 = 100 and scales all others accordingly.

---

### Forecasting

---

#### `SOV_LINEAR_FORECAST`
**Python:** `xl_linear_forecast(x_values, y_values, forecast_x)`

Fits a simple OLS regression of `y` on `x` and returns the predicted `y` at `forecast_x`. Equivalent to Excel's `FORECAST.LINEAR` but computed via statsmodels for consistency with the rest of the library.

| Parameter | Type | Description |
|---|---|---|
| `x_values` | float range | Independent variable (e.g. time periods) |
| `y_values` | float range | Dependent variable (e.g. debt ratios) |
| `forecast_x` | float | The x value at which to forecast |

**Returns:** A single `float` — predicted y.

**Excel example:**
```
=SOV_LINEAR_FORECAST(A2:A10, B2:B10, 2030)
```

---

#### `SOV_EXP_SMOOTHING`
**Python:** `xl_exp_smoothing(values, alpha)`

Single exponential smoothing. Each smoothed value is `α × xₜ + (1 − α) × sₜ₋₁`. The first non-NaN observation seeds the smoother. Handles NaN gaps in the input.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Time-series data |
| `alpha` | float | Smoothing factor in (0, 1]; higher = less smoothing |

**Returns:** Column of `float` — smoothed series.

**Excel example:**
```
=SOV_EXP_SMOOTHING(B2:B36, 0.3)
```

---

#### `SOV_HOLT_FORECAST`
**Python:** `xl_holt_forecast(values, periods_ahead)`

Holt's double exponential smoothing (additive trend model). Fits a trend + level model on the historical series and forecasts `periods_ahead` steps into the future. Requires at least 2 observations.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Historical time-series data (≥ 2 points) |
| `periods_ahead` | integer | Number of future periods to forecast (≥ 1) |

**Returns:** Column of `float` — forecast values (length = `periods_ahead`).

**Excel example (spill into 5 cells):**
```
=SOV_HOLT_FORECAST(B2:B20, 5)
```
Returns a 5-year Holt forecast.

---

#### `SOV_MOVING_AVG_FORECAST`
**Python:** `xl_moving_avg_forecast(values, window, periods_ahead)`

Forecasts by repeating the trailing moving average of the last `window` observations. A simple but robust naïve forecast baseline.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Historical data |
| `window` | integer | Number of periods in the trailing average |
| `periods_ahead` | integer | How many identical flat forecast steps to return |

**Returns:** Column of `float` — identical forecast values (length = `periods_ahead`).

**Excel example:**
```
=SOV_MOVING_AVG_FORECAST(B2:B20, 4, 8)
```
Averages the last 4 observations and projects it flat for 8 quarters.

---

#### `SOV_SEASONAL_DECOMPOSE`
**Python:** `xl_seasonal_decompose(values, period)`

Additive seasonal decomposition (STL-style via statsmodels). Separates a time series into trend, seasonal, and residual components. The series must have at least `2 × period` observations.

| Parameter | Type | Description |
|---|---|---|
| `values` | float range | Time-series data |
| `period` | integer | Seasonality period (e.g. 4 for quarterly, 12 for monthly; must be > 1) |

**Returns:** A table with header row `["trend", "seasonal", "residual"]` followed by T data rows.

**Excel example (select (T+1) × 3 cells):**
```
=SOV_SEASONAL_DECOMPOSE(B2:B49, 4)
```
Decomposes 48 quarters (12 years) of data.

---

### Statistical Modelling

---

#### `SOV_REGRESSION`
**Python:** `xl_regression(y_values, x_columns)`

Multiple OLS regression with automatic constant. Returns a coefficient table including R².

| Parameter | Type | Description |
|---|---|---|
| `y_values` | float range | Dependent variable (T × 1) |
| `x_columns` | float 2D range | Regressors (T × K; each column is one variable) |

**Returns:** Table with columns `["term", "coef"]`. Rows: `const`, `x1`, `x2`, …, `R2`.

**Excel example (select (K+3) × 2 cells):**
```
=SOV_REGRESSION(D2:D21, B2:C21)
```
Regresses D on two columns B and C.

---

#### `SOV_CORRELATION_MATRIX`
**Python:** `xl_correlation_matrix(data_range)`

Pairwise Pearson correlation matrix across columns of a 2D range. Useful for exploring co-movements among sovereign spreads.

| Parameter | Type | Description |
|---|---|---|
| `data_range` | float 2D range | T × N matrix; each column is one variable |

**Returns:** (N+1) × (N+1) table with row/column headers `c1, c2, …, cN`.

**Excel example (select (N+1)² cells):**
```
=SOV_CORRELATION_MATRIX(B2:E100)
```

---

#### `SOV_MONTE_CARLO`
**Python:** `xl_monte_carlo(mean, std_dev, n_simulations, n_periods)`

Simulates `n_simulations` paths of `n_periods` i.i.d. normal shocks with the given mean and standard deviation, computes cumulative sums, and returns the P5 / P50 / P95 percentiles of the terminal distribution.

| Parameter | Type | Description |
|---|---|---|
| `mean` | float | Per-period mean shock (e.g. expected GDP growth) |
| `std_dev` | float | Per-period standard deviation |
| `n_simulations` | integer | Number of Monte Carlo paths (e.g. 5000) |
| `n_periods` | integer | Number of periods per path |

**Returns:** 4 × 2 table: header + `P5`, `P50`, `P95` of the terminal cumulative value.

**Excel example:**
```
=SOV_MONTE_CARLO(0.02, 0.04, 5000, 10)
```
Models a 10-year cumulative GDP growth fan.

---

#### `SOV_SCENARIO_TABLE`
**Python:** `xl_scenario_table(base_inputs, low_pct, high_pct, steps)`

Generates a multi-dimensional sensitivity table by scaling a vector of base inputs from `1 − low_pct` to `1 + high_pct` in `steps` steps. Every input is scaled by the same factor simultaneously.

| Parameter | Type | Description |
|---|---|---|
| `base_inputs` | float range | Vector of baseline values (e.g. growth, rate, PB) |
| `low_pct` | float | Downside scaling (e.g. 0.20 = scale down to 80%) |
| `high_pct` | float | Upside scaling (e.g. 0.20 = scale up to 120%) |
| `steps` | integer | Number of rows in the scenario table (≥ 2) |

**Returns:** (`steps` + 1) × (K + 1) table — header row plus one row per scaling step.

**Excel example (select (steps+1) × (K+1) cells):**
```
=SOV_SCENARIO_TABLE(B2:D2, 0.2, 0.2, 9)
```
Sweeps 3 base inputs from 80% to 120% in 9 steps.

---

### Utilities

---

#### `SOV_ARRAY_SHAPE`
**Python:** `xl_array_shape(range)`

Returns the number of rows and columns of any Excel range. Useful for debugging array formula dimensions.

| Parameter | Type | Description |
|---|---|---|
| `range` | any range | Any Excel range |

**Returns:** 2 × 2 table: `["rows", "cols"]` header + `[rowCount, colCount]`.

**Excel example:**
```
=SOV_ARRAY_SHAPE(B2:E50)
```
Returns `49` rows, `4` cols.

---

#### `SOV_FLATTEN`
**Python:** `xl_flatten(range)`

Flattens a 2D range into a 1D column by reading row-by-row. Useful for passing multi-column ranges into functions that expect a 1D vector.

| Parameter | Type | Description |
|---|---|---|
| `range` | any 2D range | Multi-column range to flatten |

**Returns:** Column array of all values in row-major order.

**Excel example:**
```
=SOV_FLATTEN(B2:D10)
```
Produces 27 values in a single column.

---

#### `SOV_DATE_DIFF_BUS`
**Python:** `xl_date_diff_bus(start_date, end_date)`

Business day count between two dates, inclusive on both ends (equivalent to Excel's `NETWORKDAYS`). Accepts Excel serial numbers, ISO date strings (`"2024-01-15"`), Python `date` or `datetime` objects.

| Parameter | Type | Description |
|---|---|---|
| `start_date` | date / serial / string | Start date |
| `end_date` | date / serial / string | End date |

**Returns:** An integer — number of business days (negative if end < start).

**Excel example:**
```
=SOV_DATE_DIFF_BUS(A2, B2)
```

---

### Fiscal Sustainability

---

#### `SOV_DEBT_TRAJECTORY`
**Python:** `debt_trajectory_forecast(gdp_growth_path, primary_balance_path, interest_rate_path, initial_debt_gdp, years)`

Projects debt-to-GDP forward `years` periods using the standard debt dynamics equation:

> **dₜ = dₜ₋₁ × (1 + r) / (1 + g) − pbₜ**

where `r` is the nominal interest rate, `g` is nominal GDP growth, and `pb` is the primary balance (positive = surplus). This is the core formula used by the IMF, World Bank, and most MoF debt offices.

| Parameter | Type | Description |
|---|---|---|
| `gdp_growth_path` | float range | Nominal GDP growth rates, one per year (e.g. 0.03 = 3%) |
| `primary_balance_path` | float range | Primary balance as share of GDP, one per year |
| `interest_rate_path` | float range | Nominal effective interest rate, one per year |
| `initial_debt_gdp` | float | Starting debt-to-GDP ratio (e.g. 0.60 = 60%) |
| `years` | integer | Projection horizon (each path must have ≥ `years` elements) |

**Returns:** (`years` + 1) × 2 table with header `["year", "debt_gdp"]`.

**Excel example (select (years+1) × 2 cells):**
```
=SOV_DEBT_TRAJECTORY(B2:B6, C2:C6, D2:D6, 0.60, 5)
```
5-year debt trajectory starting at 60% of GDP.

---

#### `SOV_FISCAL_REACTION`
**Python:** `fiscal_reaction_function(primary_balance_history, debt_gdp_history, output_gap_history)`

Estimates the Bohn (1998) fiscal reaction function via OLS. Regresses the primary balance on lagged debt-to-GDP and the contemporaneous output gap:

> **pbₜ = α + β·dₜ₋₁ + γ·ogₜ + εₜ**

A positive and statistically significant `β` (coefficient on lagged debt) is the standard empirical test for intertemporal fiscal solvency. Requires at least 4 observations.

| Parameter | Type | Description |
|---|---|---|
| `primary_balance_history` | float range | Historical primary balance series |
| `debt_gdp_history` | float range | Historical debt-to-GDP series (same length) |
| `output_gap_history` | float range | Historical output gap series (same length) |

**Returns:** 5 × 3 table with columns `["term", "coef", "pvalue"]`. Rows: `const`, `lagged_debt`, `output_gap`, `R2`.

**Excel example (select 5 × 3 cells):**
```
=SOV_FISCAL_REACTION(B2:B25, C2:C25, D2:D25)
```

---

#### `SOV_IMPLICIT_INTEREST_RATE`
**Python:** `implicit_interest_rate(interest_payments, avg_debt_stock_start, avg_debt_stock_end)`

Computes the effective (implicit) cost of the debt portfolio as:

> **r_implicit = interest_payments / ((debt_start + debt_end) / 2)**

This backward-looking measure is useful for comparing the realised cost of a debt portfolio against new marginal borrowing costs.

| Parameter | Type | Description |
|---|---|---|
| `interest_payments` | float | Total interest paid in the period |
| `avg_debt_stock_start` | float | Debt stock at beginning of period |
| `avg_debt_stock_end` | float | Debt stock at end of period |

**Returns:** A single `float` — the implicit interest rate (e.g. 0.045 = 4.5%).

**Excel example:**
```
=SOV_IMPLICIT_INTEREST_RATE(B2, C2, D2)
```

---

#### `SOV_DEBT_STABILIZING_PB`
**Python:** `debt_stabilizing_primary_balance(debt_gdp, real_interest_rate, real_gdp_growth)`

Calculates the primary balance that would keep the debt-to-GDP ratio constant:

> **pb\* = d × (r − g) / (1 + g)**

When `r > g`, a positive primary balance is required; when `r < g`, the country can run a deficit and still be on a declining debt path.

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Current debt-to-GDP ratio |
| `real_interest_rate` | float | Real interest rate (e.g. 0.02 = 2%) |
| `real_gdp_growth` | float | Real GDP growth rate |

**Returns:** A single `float` — the debt-stabilising primary balance as a share of GDP.

**Excel example:**
```
=SOV_DEBT_STABILIZING_PB(0.70, 0.025, 0.02)
```
At 70% debt, r=2.5%, g=2%: pb\* ≈ 0.034 (3.4% of GDP surplus needed).

---

### Credit Risk

---

#### `SOV_MERTON_DEFAULT_PROB`
**Python:** `merton_sovereign_default_prob(debt_face_value, asset_value, asset_volatility, risk_free_rate, maturity)`

Adapts the Merton (1974) structural model to sovereigns. Treats the sovereign's tax base / resource endowment as a stochastic asset and public debt as a put option on that asset. Returns the two distance-to-default metrics (d1, d2) and the risk-neutral probability of default.

| Parameter | Type | Description |
|---|---|---|
| `debt_face_value` | float | Par value of outstanding debt (e.g. in USD bn) |
| `asset_value` | float | Estimated sovereign asset value (e.g. PV of future revenues) |
| `asset_volatility` | float | Asset value volatility (annual, e.g. 0.25 = 25%) |
| `risk_free_rate` | float | Risk-free rate (e.g. 0.05 = 5%) |
| `maturity` | float | Debt maturity in years |

**Returns:** 4 × 2 table: `d1`, `d2_distance_to_default`, `default_probability`.

**Excel example:**
```
=SOV_MERTON_DEFAULT_PROB(100, 130, 0.30, 0.04, 5)
```

---

#### `SOV_CDS_DEFAULT_PROB`
**Python:** `cds_implied_default_prob(cds_spread_bps, recovery_rate, tenor_years)`

Back-calculates the risk-neutral default probability implied by a CDS spread using the standard hazard-rate approximation:

> **λ = spread / LGD**, where **LGD = 1 − recovery_rate**
> **P(default before T) = 1 − e^(−λT)**

| Parameter | Type | Description |
|---|---|---|
| `cds_spread_bps` | float | CDS spread in basis points (e.g. 250) |
| `recovery_rate` | float | Expected recovery rate in [0, 1) (e.g. 0.40 = 40%) |
| `tenor_years` | float | CDS tenor in years (e.g. 5) |

**Returns:** 4 × 2 table: `hazard_rate`, `cumulative_pd`, `annual_pd`.

**Excel example:**
```
=SOV_CDS_DEFAULT_PROB(350, 0.40, 5)
```
350bps 5Y CDS with 40% recovery → cumulative PD ≈ 30%.

---

#### `SOV_ZSCORE_SOVEREIGN`
**Python:** `zscore_sovereign(current_account_gdp, reserves_imports, debt_gdp, gdp_growth, inflation)`

A composite early-warning scoring model in the spirit of Reinhart & Rogoff / Kaminsky-Lizondo-Reinhart. Standardises five macro indicators against approximate historical benchmarks, weights them by risk direction, and returns a composite z-score plus percentile rank.

| Parameter | Type | Description |
|---|---|---|
| `current_account_gdp` | float | Current account balance as % of GDP (negative = deficit) |
| `reserves_imports` | float | Reserves in months of imports |
| `debt_gdp` | float | Debt-to-GDP ratio |
| `gdp_growth` | float | GDP growth rate |
| `inflation` | float | Annual CPI inflation rate |

**Returns:** Table with z-score for each indicator, composite z-score, and percentile rank (higher percentile = higher risk).

**Excel example:**
```
=SOV_ZSCORE_SOVEREIGN(-0.05, 3.5, 0.85, 0.02, 0.12)
```

---

#### `SOV_SPREAD_DECOMPOSITION`
**Python:** `spread_decomposition(embi_spread, us_vix, us_10y, commodity_index, country_fundamentals)`

Decomposes sovereign bond spreads into global push factors (VIX, US 10-year yield, commodity price index) and a country-specific pull factor. Runs OLS and reports coefficients, p-values, R², and the share of fitted variance attributable to global vs. idiosyncratic factors.

| Parameter | Type | Description |
|---|---|---|
| `embi_spread` | float range | EMBI/CDS spread time series |
| `us_vix` | float range | VIX index time series (same length) |
| `us_10y` | float range | US 10-year Treasury yield (same length) |
| `commodity_index` | float range | Commodity price index (same length) |
| `country_fundamentals` | float range | Country-specific composite (same length) |

**Returns:** Table: coefficients, p-values, R², and global/idiosyncratic variance shares.

**Excel example:**
```
=SOV_SPREAD_DECOMPOSITION(B2:B100, C2:C100, D2:D100, E2:E100, F2:F100)
```

---

### Yield Curve

---

#### `SOV_NELSON_SIEGEL`
**Python:** `nelson_siegel_fit(maturities, yields)`

Fits the Nelson-Siegel (1987) parametric yield curve:

> **y(τ) = β₀ + β₁ · ((1−e^(−τ/λ))/(τ/λ)) + β₂ · ((1−e^(−τ/λ))/(τ/λ) − e^(−τ/λ))**

Minimises sum of squared errors via L-BFGS-B. Returns the four parameters (level, slope, curvature, decay), RMSE, and fitted yields at each input maturity. Requires at least 3 maturity/yield pairs.

| Parameter | Type | Description |
|---|---|---|
| `maturities` | float range | Maturities in years (all must be > 0; e.g. 0.25, 0.5, 1, 2, 5, 10, 30) |
| `yields` | float range | Observed yields at each maturity (same length) |

**Returns:** Table with β₀ (level), β₁ (slope), β₂ (curvature), τ (decay), RMSE, then fitted yields.

**Excel example:**
```
=SOV_NELSON_SIEGEL(A2:A8, B2:B8)
```

---

#### `SOV_ZSPREAD`
**Python:** `zspread(bond_price, coupon, maturity, benchmark_curve_tenors, benchmark_curve_rates)`

Computes the Z-spread — the constant spread added to each benchmark discount rate such that the sum of discounted cash flows equals the market price. Uses continuous compounding and Brent's root-finding method.

> **Price = Σ CF_t · e^(−(r_bench(t) + z) · t)**

| Parameter | Type | Description |
|---|---|---|
| `bond_price` | float | Dirty market price (face = 100) |
| `coupon` | float | Annual coupon in price terms (e.g. 5.0 for a 5% coupon) |
| `maturity` | float | Years to maturity |
| `benchmark_curve_tenors` | float range | Tenors of the benchmark curve (years) |
| `benchmark_curve_rates` | float range | Benchmark rates at each tenor |

**Returns:** A single `float` — z-spread in decimal (e.g. 0.0245 = 245bps). Multiply by 10,000 for bps.

**Excel example:**
```
=SOV_ZSPREAD(97.5, 4.5, 7, E2:E8, F2:F8)
```

---

#### `SOV_CARRY_ROLLDOWN`
**Python:** `carry_rolldown(bond_tenor, yield_curve_tenors, yield_curve_rates, horizon_months)`

Estimates the expected return from holding a bond over a horizon assuming the yield curve remains unchanged. Decomposes into:

- **Carry:** yield income earned over the horizon period
- **Rolldown:** price gain as the bond rolls down to a shorter tenor (usually lower yield)

Uses modified duration approximation for price change.

| Parameter | Type | Description |
|---|---|---|
| `bond_tenor` | float | Current tenor in years |
| `yield_curve_tenors` | float range | Yield curve tenors |
| `yield_curve_rates` | float range | Yield curve rates |
| `horizon_months` | integer | Investment horizon in months |

**Returns:** 6 × 2 table: `initial_yield`, `rolled_yield`, `carry`, `rolldown`, `total_return`.

**Excel example:**
```
=SOV_CARRY_ROLLDOWN(10, E2:E8, F2:F8, 12)
```
1-year carry + rolldown on a 10-year bond.

---

#### `SOV_ASW_SPREAD`
**Python:** `asm_spread(bond_price, coupon, maturity, ois_curve_tenors, ois_curve_rates)`

Asset-swap spread (ASW) over the OIS curve. Measures the bond's relative value on a swap-hedged basis:

> **ASW = (PV_fixed_at_OIS − Price) / OIS_annuity**

A positive ASW means the bond is cheap relative to OIS (offers excess yield after hedging). Face value is assumed to be 100.

| Parameter | Type | Description |
|---|---|---|
| `bond_price` | float | Dirty price (face = 100) |
| `coupon` | float | Annual coupon amount |
| `maturity` | float | Years to maturity |
| `ois_curve_tenors` | float range | OIS curve tenors in years |
| `ois_curve_rates` | float range | OIS rates at each tenor |

**Returns:** A single `float` — ASW in decimal.

**Excel example:**
```
=SOV_ASW_SPREAD(98.5, 5.0, 5, G2:G6, H2:H6)
```

---

### Reserves & External Accounts

---

#### `SOV_RESERVES_ADEQUACY`
**Python:** `reserves_adequacy_metrics(reserves_usd, short_term_debt, monthly_imports, broad_money, gdp)`

Computes four standard reserve adequacy metrics in one call:

| Metric | Formula | Threshold |
|---|---|---|
| Import cover | Reserves / monthly imports | ≥ 3 months |
| Greenspan-Guidotti | Reserves / short-term debt | ≥ 1.0 |
| Wijnholds-Kapteyn | Reserves / broad money | — |
| IMF ARA composite | Reserves / (0.3×STD + 0.6×annual_imports + 0.1×M2) | 1.0–1.5 |

| Parameter | Type | Description |
|---|---|---|
| `reserves_usd` | float | Total FX reserves (must be ≥ 0) |
| `short_term_debt` | float | Residual maturity short-term external debt |
| `monthly_imports` | float | Average monthly import bill |
| `broad_money` | float | M2 / broad money aggregate |
| `gdp` | float | Annual GDP (not used directly, included for scaling) |

**Returns:** 5 × 2 table with all four metrics.

**Excel example:**
```
=SOV_RESERVES_ADEQUACY(45e9, 20e9, 4e9, 80e9, 150e9)
```

---

#### `SOV_BOP_FINANCING_GAP`
**Python:** `bop_financing_gap(current_account, fdi, portfolio_flows, debt_amortization, reserves)`

Residual balance-of-payments financing need:

> **gap = debt_amortization − (current_account + FDI + portfolio_flows + reserve_drawdown)**

A positive result means a financing gap exists that must be covered by new borrowing, IMF program, or further reserve sales.

| Parameter | Type | Description |
|---|---|---|
| `current_account` | float | Current account balance (positive = surplus) |
| `fdi` | float | Net FDI inflows |
| `portfolio_flows` | float | Net portfolio capital inflows |
| `debt_amortization` | float | Scheduled principal repayments |
| `reserves` | float | Change in reserves (positive = drawdown used to finance) |

**Returns:** A single `float` — the financing gap (positive = unfunded).

**Excel example:**
```
=SOV_BOP_FINANCING_GAP(-5e9, 3e9, 1e9, 12e9, 2e9)
```

---

#### `SOV_FX_MISALIGNMENT`
**Python:** `exchange_rate_misalignment(reer_index, reer_history, terms_of_trade, nfa_gdp)`

Estimates REER over/undervaluation using a BEER (Behavioural Equilibrium Exchange Rate) regression. Regresses historical REER on terms of trade and net foreign assets/GDP, then compares the current REER to the regression-implied equilibrium.

| Parameter | Type | Description |
|---|---|---|
| `reer_index` | float | Current REER index level |
| `reer_history` | float range | Historical REER series (≥ 3 observations) |
| `terms_of_trade` | float range | Terms of trade series (same length) |
| `nfa_gdp` | float range | Net foreign assets as % of GDP (same length) |

**Returns:** Table: `reer_observed`, `reer_equilibrium`, `misalignment`, `misalignment_pct`, `R2`.

**Excel example:**
```
=SOV_FX_MISALIGNMENT(105, B2:B40, C2:C40, D2:D40)
```

---

### Stress Testing

---

#### `SOV_FAN_CHART_DEBT`
**Python:** `fan_chart_debt(base_case_params, shock_distributions, num_simulations, years)`

Monte Carlo debt fan chart. Simulates `num_simulations` stochastic debt paths by applying normally distributed annual shocks to GDP growth, interest rates, and primary balance simultaneously. Returns the P10/P25/P50/P75/P90 percentile paths by year.

**base_case_params layout:** `[gdp_growth, interest_rate, primary_balance, initial_debt_gdp]`
**shock_distributions layout:** `[gdp_growth_std, interest_rate_std, primary_balance_std]`

| Parameter | Type | Description |
|---|---|---|
| `base_case_params` | float range (4 values) | Baseline scenario parameters |
| `shock_distributions` | float range (3 values) | Standard deviations for each shock |
| `num_simulations` | integer | Number of paths (e.g. 1000) |
| `years` | integer | Projection horizon |

**Returns:** (`years` + 1) × 6 table: `year, p10, p25, p50, p75, p90`.

**Excel example (select (years+1) × 6 cells):**
```
=SOV_FAN_CHART_DEBT(B2:B5, C2:C4, 1000, 5)
```

---

#### `SOV_CONTINGENT_LIABILITY_SHOCK`
**Python:** `contingent_liability_shock(debt_gdp, banking_sector_assets_gdp, soe_debt_gdp, historical_realization_rate)`

Estimates the public-sector debt increase if contingent liabilities (banking-sector implicit guarantees and SOE debt) crystallise. Applies a `historical_realization_rate` to each contingent exposure.

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Current public debt-to-GDP |
| `banking_sector_assets_gdp` | float | Banking system assets as % of GDP |
| `soe_debt_gdp` | float | State-owned enterprise debt as % of GDP |
| `historical_realization_rate` | float | Fraction of contingent liabilities typically realised in crises (e.g. 0.10 for 10%) |

**Returns:** 6 × 2 table with pre- and post-shock debt ratios and component breakdowns.

**Excel example:**
```
=SOV_CONTINGENT_LIABILITY_SHOCK(0.70, 1.20, 0.30, 0.15)
```

---

#### `SOV_FX_PASSTHROUGH_DEBT`
**Python:** `exchange_rate_passthrough_to_debt(fx_denominated_share, debt_gdp, depreciation_pct)`

Mechanical increase in debt-to-GDP from a currency depreciation on the FX-denominated portion of the debt:

> **Δd = fx_share × d × depreciation_pct**

| Parameter | Type | Description |
|---|---|---|
| `fx_denominated_share` | float | Share of total debt in foreign currency [0, 1] |
| `debt_gdp` | float | Total debt-to-GDP ratio |
| `depreciation_pct` | float | Currency depreciation (e.g. 0.30 = 30% devaluation) |

**Returns:** A single `float` — the increase in debt-to-GDP.

**Excel example:**
```
=SOV_FX_PASSTHROUGH_DEBT(0.55, 0.70, 0.30)
```
A 30% depreciation with 55% FX debt at 70% debt/GDP adds ≈ 11.6pp to the ratio.

---

### Amortization & Debt Service

---

#### `SOV_AMORTIZATION_PROFILE`
**Python:** `amortization_profile(bonds_list)`

Builds a redemption wall from a list of individual bonds, aggregating face values by maturity year. Flags any year where a single year's redemption exceeds 25% of total outstanding as `"HIGH"` concentration.

**Input layout:** 2-column range `[maturity_year, face_value]`. An optional text header row is auto-skipped.

| Parameter | Type | Description |
|---|---|---|
| `bonds_list` | 2-column range | Each row: `[maturity_year, face_value]` |

**Returns:** Table: `year`, `redemption`, `concentration_flag`.

**Excel example:**
```
=SOV_AMORTIZATION_PROFILE(A2:B25)
```

---

#### `SOV_WEIGHTED_AVG_MATURITY`
**Python:** `weighted_avg_maturity(bonds_outstanding)`

Weighted average maturity (WAM) of a debt portfolio, weighted by face value:

> **WAM = Σ(maturityᵢ × face_valueᵢ) / Σface_valueᵢ**

| Parameter | Type | Description |
|---|---|---|
| `bonds_outstanding` | 2-column range | Each row: `[maturity_years, face_value]` |

**Returns:** A single `float` — WAM in years.

**Excel example:**
```
=SOV_WEIGHTED_AVG_MATURITY(A2:B25)
```

---

#### `SOV_GROSS_FINANCING_NEED`
**Python:** `gross_financing_need(amortization_schedule, projected_deficit, year)`

Gross financing need for a specific year:

> **GFN = amortization_due_in_year + projected_fiscal_deficit**

| Parameter | Type | Description |
|---|---|---|
| `amortization_schedule` | float range | Vector of annual amortization amounts |
| `projected_deficit` | float | Projected fiscal deficit for the year |
| `year` | integer | 1-based index into the amortization schedule |

**Returns:** A single `float` — GFN for that year.

**Excel example:**
```
=SOV_GROSS_FINANCING_NEED(B2:B10, C2, 3)
```
Year 3 GFN = amortization[3] + deficit.

---

### Political Risk & ESG

---

#### `SOV_POLITICAL_RISK_SCORE`
**Python:** `political_risk_score(polity_iv_score, wgi_governance_indicators, years_since_last_default, regime_change_dummy, election_proximity_months)`

Composite political risk index (0–100, higher = more risk) based on PCA-inspired weighting of:
- Polity IV democracy score (weight 30%)
- World Bank Governance Indicators mean (weight 30%)
- Default history (weight 20%)
- Recent regime change (weight 10%)
- Election cycle proximity (weight 10%)

| Parameter | Type | Description |
|---|---|---|
| `polity_iv_score` | float | Polity IV score in [−10, +10] (−10 = autocracy) |
| `wgi_governance_indicators` | float range | 1–6 WGI scores in [−2.5, +2.5] |
| `years_since_last_default` | float | Years since most recent default (0 if in default) |
| `regime_change_dummy` | float | 1 if regime change occurred in past 2 years, else 0 |
| `election_proximity_months` | float | Months to next scheduled election |

**Returns:** Table with composite score plus each sub-component and its weight.

**Excel example:**
```
=SOV_POLITICAL_RISK_SCORE(6, B2:G2, 15, 0, 18)
```

---

#### `SOV_ESG_SOVEREIGN_SCORE`
**Python:** `esg_sovereign_score(co2_per_capita, renewable_energy_share, gini_coefficient, rule_of_law_index, education_spending_gdp, health_spending_gdp)`

Weighted composite ESG score (0–100, higher = better ESG) using weights calibrated to sovereign spread regressions in academic literature: E 20%, S 35%, G 45%.

| Pillar | Inputs | Weight |
|---|---|---|
| Environmental | CO₂ per capita, renewable energy share | 20% |
| Social | Gini coefficient, education spend, health spend | 35% |
| Governance | World Bank Rule of Law index | 45% |

| Parameter | Type | Description |
|---|---|---|
| `co2_per_capita` | float | CO₂ emissions in tonnes per person |
| `renewable_energy_share` | float | Share of renewables in energy mix [0, 1] |
| `gini_coefficient` | float | Gini index [0, 1] or [0, 100] (auto-detected) |
| `rule_of_law_index` | float | WB Rule of Law [−2.5, +2.5] |
| `education_spending_gdp` | float | Education spending as % of GDP |
| `health_spending_gdp` | float | Health spending as % of GDP |

**Returns:** Table with composite ESG score and each pillar/sub-component.

**Excel example:**
```
=SOV_ESG_SOVEREIGN_SCORE(4.5, 0.35, 0.32, 0.8, 0.05, 0.06)
```

---

#### `SOV_SANCTIONS_EXPOSURE`
**Python:** `sanctions_exposure_index(trade_partner_shares, fx_reserves_by_currency_share, swift_dependency_pct, energy_export_share)`

Quantifies a sovereign's vulnerability to financial sanctions (0–100 composite, equal-weighted across four dimensions):

1. **Trade concentration** — Herfindahl index of trade partner shares
2. **FX reserve concentration** — HHI of reserve currency composition
3. **SWIFT dependency** — share of cross-border payments on SWIFT
4. **Energy export concentration** — energy as % of total exports

| Parameter | Type | Description |
|---|---|---|
| `trade_partner_shares` | float range | Share of trade with each partner (sums to ≤ 1) |
| `fx_reserves_by_currency_share` | float range | Reserve allocation by currency |
| `swift_dependency_pct` | float | SWIFT payment share [0, 1] or [0, 100] |
| `energy_export_share` | float | Energy exports / total exports |

**Returns:** 6 × 2 table: composite index and four sub-scores.

**Excel example:**
```
=SOV_SANCTIONS_EXPOSURE(B2:B5, C2:C4, 0.85, 0.60)
```

---

### Contagion & Linkages

---

#### `SOV_CONTAGION_BETA`
**Python:** `sovereign_contagion_beta(target_country_spreads, source_country_spreads, global_factor_series, window_days)`

Rolling bivariate contagion beta: regresses first-differences of the target country's spread on first-differences of the source country's spread and a global factor (e.g. VIX). The rolling coefficient on the source country's spread is the contagion beta, controlling for common global shocks. Requires ≥ 10 observations and window ≥ 5.

| Parameter | Type | Description |
|---|---|---|
| `target_country_spreads` | float range | Daily spread series for the country being infected |
| `source_country_spreads` | float range | Daily spread series for the contagion source |
| `global_factor_series` | float range | Global risk factor (e.g. VIX) to control for |
| `window_days` | integer | Rolling window length in days |

**Returns:** Summary statistics (mean, median, std of beta) plus the full time series of rolling betas.

**Excel example:**
```
=SOV_CONTAGION_BETA(B2:B250, C2:C250, D2:D250, 60)
```

---

#### `SOV_DCC_GARCH_CORR`
**Python:** `dcc_garch_correlation(spread_series_a, spread_series_b, window)`

Dynamic conditional correlation (DCC-GARCH approximation) between two spread series. Standardises each series by its rolling EWMA volatility (RiskMetrics λ=0.94), then computes the rolling correlation of standardised residuals. This proxy for full DCC-GARCH is computationally tractable in Excel.

| Parameter | Type | Description |
|---|---|---|
| `spread_series_a` | float range | First spread time series |
| `spread_series_b` | float range | Second spread time series (same length) |
| `window` | integer | Rolling window for the DCC correlation step |

**Returns:** Summary stats (mean, min, max DCC) plus the full rolling correlation series.

**Excel example:**
```
=SOV_DCC_GARCH_CORR(B2:B200, C2:C200, 60)
```

---

#### `SOV_GRANGER_CAUSALITY`
**Python:** `granger_causality_spreads(spread_matrix, lags, significance_level)`

Pairwise Granger causality test across N sovereign spread series. Returns an N×N adjacency matrix where entry [i, j] = 1 if country i Granger-causes country j at the specified significance level, using the F-test at the chosen lag length.

| Parameter | Type | Description |
|---|---|---|
| `spread_matrix` | 2D range | T × N matrix of spread series (columns = countries) |
| `lags` | integer | VAR lag order for the Granger test |
| `significance_level` | float | p-value threshold (e.g. 0.05) |

**Returns:** (N+1) × (N+1) adjacency matrix with row/column labels.

**Excel example (select (N+1)² cells):**
```
=SOV_GRANGER_CAUSALITY(B2:F100, 2, 0.05)
```

---

#### `SOV_TRADE_LINKAGE_MATRIX`
**Python:** `trade_linkage_matrix(bilateral_trade_flows, gdp_values)`

Constructs a trade-weighted real-economy exposure matrix. Entry [i, j] equals the bilateral trade flow from country i to j divided by country j's GDP — measuring j's real-economy vulnerability to stress in i.

| Parameter | Type | Description |
|---|---|---|
| `bilateral_trade_flows` | square 2D range | N × N matrix of bilateral trade flows (rows = exporters) |
| `gdp_values` | float range | Length-N GDP vector in the same currency as trade flows |

**Returns:** (N+1) × (N+1) table with `exporter\importer` headers.

**Excel example:**
```
=SOV_TRADE_LINKAGE_MATRIX(B2:F6, H2:H6)
```

---

### Debt Composition & Transparency

---

#### `SOV_ORIGINAL_SIN_INDEX`
**Python:** `original_sin_index(fx_denominated_debt, total_debt, local_currency_debt_held_by_nonresidents)`

Computes two Eichengreen-Hausmann metrics of currency composition vulnerability:

- **Original Sin (OSin):** share of debt in foreign currency
- **Original Sin Redux:** share of local-currency debt held by non-residents (captures FX risk hidden in domestic balance sheets)
- **Composite:** simple average of both

| Parameter | Type | Description |
|---|---|---|
| `fx_denominated_debt` | float | Face value of FX-denominated debt |
| `total_debt` | float | Total public debt outstanding |
| `local_currency_debt_held_by_nonresidents` | float | LC debt held by foreign investors |

**Returns:** 6 × 2 table with both indices and the composite.

**Excel example:**
```
=SOV_ORIGINAL_SIN_INDEX(40e9, 80e9, 15e9)
```

---

#### `SOV_HIDDEN_DEBT_ESTIMATOR`
**Python:** `hidden_debt_estimator(reported_public_debt, soe_guaranteed_debt, ppp_commitments, central_bank_quasi_fiscal, local_govt_off_budget)`

Augments the official debt figure with off-balance-sheet and contingent exposures following the Kose/Nagle/Ohnsorge (2021) comprehensive public-sector debt framework.

| Parameter | Type | Description |
|---|---|---|
| `reported_public_debt` | float | Official/reported public debt |
| `soe_guaranteed_debt` | float | State-owned enterprise debt with government guarantee |
| `ppp_commitments` | float | Public-private partnership payment obligations |
| `central_bank_quasi_fiscal` | float | Central bank losses / quasi-fiscal deficit exposure |
| `local_govt_off_budget` | float | Sub-national government off-budget liabilities |

**Returns:** Table showing each component, total off-balance-sheet, augmented debt, and hidden debt as % of reported.

**Excel example:**
```
=SOV_HIDDEN_DEBT_ESTIMATOR(0.65, 0.10, 0.05, 0.03, 0.08)
```
All values as fraction of GDP.

---

#### `SOV_DEBT_TRANSPARENCY_SCORE`
**Python:** `debt_transparency_score(imf_sdds_subscriber, debt_reporting_frequency, coverage_of_soe, coverage_of_subnational, arrears_reporting)`

Scores data quality and reporting completeness (0–100, higher = more transparent). Flags specific weaknesses where published figures may understate actual liabilities.

| Parameter | Type | Description |
|---|---|---|
| `imf_sdds_subscriber` | float | 1 = IMF SDDS subscriber, 0 = not |
| `debt_reporting_frequency` | float | 1 = quarterly or better; 0.5 = annual; 0 = none |
| `coverage_of_soe` | float | Share of SOE debt covered in official statistics [0, 1] |
| `coverage_of_subnational` | float | Share of sub-national debt covered [0, 1] |
| `arrears_reporting` | float | 1 = arrears reported; 0 = not |

**Returns:** Table with composite score, sub-scores, and a `flags` field listing active data quality warnings.

**Excel example:**
```
=SOV_DEBT_TRANSPARENCY_SCORE(1, 0.5, 0.7, 0.4, 1)
```

---

#### `SOV_COLLATERALIZED_DEBT_FLAG`
**Python:** `collateralized_debt_flag(resource_backed_loans, total_debt, export_revenues, resource_type)`

Identifies and quantifies resource-collateralised borrowing. Returns the share of total debt that is resource-backed, the share of annual export revenues pre-committed to debt service, and a `LOW / MEDIUM / HIGH` risk flag (HIGH if > 25% of total debt is resource-backed).

| Parameter | Type | Description |
|---|---|---|
| `resource_backed_loans` | float | Face value of resource-collateralised loans |
| `total_debt` | float | Total public debt |
| `export_revenues` | float | Annual export revenues |
| `resource_type` | string | Commodity type (e.g. `"oil"`, `"copper"`) — label only |

**Returns:** 6 × 2 table with shares and the risk flag.

**Excel example:**
```
=SOV_COLLATERALIZED_DEBT_FLAG(8e9, 25e9, 12e9, "oil")
```

---

### Macro-Financial Vulnerabilities

---

#### `SOV_BANK_NEXUS_SCORE`
**Python:** `sovereign_bank_nexus_score(bank_holdings_of_govt_debt, govt_ownership_of_banks, bank_capital_ratio, sovereign_spread_bps)`

Quantifies the sovereign–bank "doom loop" risk (0–100, higher = stronger loop). Weights four channels:
- Bank holdings of government bonds (35%)
- Government ownership of banks (20%)
- Bank capital resilience (30%) — low capital = high score
- Sovereign spread stress (15%)

| Parameter | Type | Description |
|---|---|---|
| `bank_holdings_of_govt_debt` | float | Banks' govt bond holdings / bank assets [0, 1] |
| `govt_ownership_of_banks` | float | State-owned share of banking assets [0, 1] |
| `bank_capital_ratio` | float | Tier-1 capital ratio [0, 1] |
| `sovereign_spread_bps` | float | Current CDS/EMBI spread in basis points |

**Returns:** Table with composite nexus score, `LOW/MEDIUM/HIGH` flag, and four sub-scores.

**Excel example:**
```
=SOV_BANK_NEXUS_SCORE(0.15, 0.30, 0.12, 280)
```

---

#### `SOV_MONETARY_FINANCING_RISK`
**Python:** `monetary_financing_risk(central_bank_claims_on_govt, reserve_money_growth, inflation_rate, cb_independence_index)`

Scores the probability of debt monetization (0–100). High CB claims, rapid reserve money growth, and high inflation all increase the score; central bank independence partially mitigates it.

| Parameter | Type | Description |
|---|---|---|
| `central_bank_claims_on_govt` | float | CB claims on government as fraction of GDP |
| `reserve_money_growth` | float | Annual reserve money (M0) growth rate |
| `inflation_rate` | float | Annual CPI inflation |
| `cb_independence_index` | float | CB independence [0, 1] (e.g. CBI index) |

**Returns:** Table with composite score, `LOW/MEDIUM/HIGH` flag, and sub-scores.

**Excel example:**
```
=SOV_MONETARY_FINANCING_RISK(0.05, 0.20, 0.15, 0.7)
```

---

#### `SOV_RG_DIFFERENTIAL`
**Python:** `real_interest_rate_growth_differential(nominal_rate, inflation, real_gdp_growth, years)`

Computes the r−g differential time series over `years` periods, where:

> **r = nominal_rate − inflation** (Fisher approximation)
> **r−g = real interest rate − real GDP growth**

Returns each period's r, g, r−g, and a cumulative rolling average of r−g. The sign of r−g is the single most important driver of long-run debt dynamics.

| Parameter | Type | Description |
|---|---|---|
| `nominal_rate` | float range | Nominal interest rate series |
| `inflation` | float range | CPI inflation series (same length) |
| `real_gdp_growth` | float range | Real GDP growth series (same length) |
| `years` | integer | Number of periods to compute (≤ length of each series) |

**Returns:** (`years` + 1) × 5 table: `year, r, g, r_minus_g, rolling_avg_rg`.

**Excel example:**
```
=SOV_RG_DIFFERENTIAL(B2:B20, C2:C20, D2:D20, 15)
```

---

#### `SOV_DOLLARIZATION_VULNERABILITY`
**Python:** `dollarization_vulnerability(deposit_dollarization_pct, loan_dollarization_pct, fx_reserves_to_fx_deposits)`

Assesses the severity of balance-sheet mismatches in highly dollarized banking systems. A large depreciation is amplified when banks hold FX-denominated loans but have insufficient FX reserves to cover FX deposits.

| Parameter | Type | Description |
|---|---|---|
| `deposit_dollarization_pct` | float | Share of bank deposits in foreign currency [0, 1] |
| `loan_dollarization_pct` | float | Share of bank loans in foreign currency [0, 1] |
| `fx_reserves_to_fx_deposits` | float | FX reserves / total FX deposits (coverage ratio) |

**Returns:** Table with composite vulnerability score (0–100), `LOW/MEDIUM/HIGH` flag, and three sub-scores.

**Excel example:**
```
=SOV_DOLLARIZATION_VULNERABILITY(0.55, 0.45, 0.80)
```

---

### Market Microstructure

---

#### `SOV_BID_ASK_LIQUIDITY_SCORE`
**Python:** `bid_ask_liquidity_score(bid_ask_spreads, turnover_ratios, issue_sizes)`

Composite sovereign bond curve liquidity score (0–100, higher = more liquid). Scores each bond on three dimensions — bid-ask tightness (40%), turnover ratio (35%), issue size (25%) — then averages across the bond curve.

| Parameter | Type | Description |
|---|---|---|
| `bid_ask_spreads` | float range | Bid-ask spread per bond in bps (caps at 200bps) |
| `turnover_ratios` | float range | Daily turnover as fraction of outstanding (caps at 2×) |
| `issue_sizes` | float range | Outstanding face value per bond in USD bn (caps at 20bn) |

**Returns:** Table: composite score, mean sub-scores, then per-bond scores.

**Excel example:**
```
=SOV_BID_ASK_LIQUIDITY_SCORE(B2:B8, C2:C8, D2:D8)
```

---

#### `SOV_LOCAL_VS_EXTERNAL_BASIS`
**Python:** `local_vs_external_curve_basis(local_currency_yields, cross_currency_swap_rates, usd_yields, tenors)`

Cross-currency basis-adjusted spread: compares local-currency sovereign yields to external USD yields on a fully hedged basis.

> **hedged_local_yield = local_yield − xccy_swap_rate**
> **basis = hedged_local_yield − USD_yield**

A positive basis means local bonds are cheaper (higher yield) than external bonds after hedging FX risk.

| Parameter | Type | Description |
|---|---|---|
| `local_currency_yields` | float range | LC sovereign yield curve |
| `cross_currency_swap_rates` | float range | Cross-currency basis swap rates at each tenor |
| `usd_yields` | float range | USD benchmark yields at each tenor |
| `tenors` | float range | Shared tenor vector in years |

**Returns:** Table per tenor + mean basis and a `local_cheaper / external_cheaper` recommendation.

**Excel example:**
```
=SOV_LOCAL_VS_EXTERNAL_BASIS(B2:B8, C2:C8, D2:D8, E2:E8)
```

---

#### `SOV_AUCTION_TAIL_ANALYSIS`
**Python:** `auction_tail_analysis(auction_results, bid_cover_ratios, cutoff_vs_when_issued)`

Trend analysis of primary market reception across a series of bond auctions. Uses OLS to detect deteriorating demand (rising tail, falling bid-cover). Flags `DETERIORATING` if either trend is significant at the 10% level.

**auction_results layout:** 2-column range `[auction_date_serial, tail_bps]`.

| Parameter | Type | Description |
|---|---|---|
| `auction_results` | 2-column range | `[date, tail_bps]` per auction (≥ 3 rows) |
| `bid_cover_ratios` | float range | Bid-to-cover ratio per auction (same length) |
| `cutoff_vs_when_issued` | float range | Cutoff yield minus when-issued yield in bps |

**Returns:** Summary statistics (mean tail, mean bid-cover, trend slopes, p-values) and a `STABLE/DETERIORATING` flag.

**Excel example:**
```
=SOV_AUCTION_TAIL_ANALYSIS(A2:B25, C2:C25, D2:D25)
```

---

#### `SOV_INVESTOR_BASE_CONCENTRATION`
**Python:** `investor_base_concentration(holdings_by_type)`

Herfindahl-Hirschman Index (HHI) over investor holder categories. A concentrated investor base (e.g. dominated by domestic banks or one class of foreign investors) increases roll-over and contagion risk.

| Parameter | Type | Description |
|---|---|---|
| `holdings_by_type` | float range | Holdings share (or absolute amounts) per investor class |

**Returns:** Table: `hhi_raw`, `hhi_normalised`, `equivalent_n_holders`, `LOW/MEDIUM/HIGH` flag, and share per holder type.

**Excel example:**
```
=SOV_INVESTOR_BASE_CONCENTRATION(B2:B6)
```
B2:B6 might be: domestic banks, foreign real-money, central banks, retail, other.

---

### IMF Framework

---

#### `SOV_DSA_REPLICATION`
**Python:** `dsa_replication(gdp_path, fiscal_path, interest_path, exchange_rate_path, financing_assumptions)`

Replicates the IMF Debt Sustainability Analysis framework. Runs the baseline debt trajectory plus five standardised stress tests:

| Stress Test | Shock |
|---|---|
| Growth shock | −1 std dev on GDP growth |
| PB shock | −1 std dev on primary balance |
| Rate shock | +1 std dev on interest rate |
| FX shock | 30% exchange rate depreciation in year 1 |
| Combined | All four shocks at 50% magnitude simultaneously |

**Input layouts:**
- `gdp_path`: `[initial_debt_gdp, g_y1, g_y2, …]`
- `fiscal_path`: `[pb_y1, pb_y2, …]`
- `interest_path`: `[r_y1, r_y2, …]`
- `exchange_rate_path`: `[fx_debt_share, dep_y1, dep_y2, …]`
- `financing_assumptions`: `[std_g, std_pb, std_r, (optional) fx_share_override]`

| Parameter | Type | Description |
|---|---|---|
| `gdp_path` | float range | Initial debt + annual growth path |
| `fiscal_path` | float range | Annual primary balance path |
| `interest_path` | float range | Annual interest rate path |
| `exchange_rate_path` | float range | FX debt share + annual depreciation |
| `financing_assumptions` | float range | Shock standard deviations |

**Returns:** (`years` + 1) × 7 table: `year, baseline, growth_shock, pb_shock, rate_shock, fx_shock, combined`.

**Excel example:**
```
=SOV_DSA_REPLICATION(B2:B7, C2:C6, D2:D6, E2:E7, F2:F4)
```

---

#### `SOV_IMF_PROGRAM_PROBABILITY`
**Python:** `imf_program_probability(reserves_months_imports, debt_gdp, current_account_gdp, inflation, exchange_rate_regime, political_stability)`

Logistic regression model for the probability of IMF program entry within 24 months, calibrated on stylised coefficients from Bird & Rowlands (2004) and Bal Gunduz et al. (2013).

| Parameter | Type | Description |
|---|---|---|
| `reserves_months_imports` | float | Import cover in months (lower → more likely) |
| `debt_gdp` | float | Debt-to-GDP (higher → more likely) |
| `current_account_gdp` | float | CA balance / GDP (more negative → more likely) |
| `inflation` | float | Annual CPI inflation (higher → more likely) |
| `exchange_rate_regime` | float | 1 = fixed; 0 = flexible (fixed → more likely) |
| `political_stability` | float | WB Political Stability [−2.5, +2.5] (lower → more likely) |

**Returns:** A single `float` — probability in [0, 1].

**Excel example:**
```
=SOV_IMF_PROGRAM_PROBABILITY(2.5, 0.85, -0.06, 0.12, 1, -0.5)
```

---

#### `SOV_EXCEPTIONAL_ACCESS_CHECK`
**Python:** `exceptional_access_criteria_check(debt_gdp, gross_financing_need_gdp, market_access_boolean, debt_sustainability_assessment)`

Evaluates the four IMF exceptional access criteria (2016 framework):

1. Balance-of-payments need (GFN/GDP > 15%)
2. Debt sustainability with high probability
3. Market access
4. Prospects for program success (debt/GDP < 150%)

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Debt-to-GDP ratio |
| `gross_financing_need_gdp` | float | GFN as fraction of GDP |
| `market_access_boolean` | float | 1 = has market access; 0 = does not |
| `debt_sustainability_assessment` | string | `"SUSTAINABLE"`, `"YES"`, `"TRUE"`, or `"1"` to pass criterion 2 |

**Returns:** 6 × 3 table: criterion name, `PASS/FAIL`, description, and overall result.

**Excel example:**
```
=SOV_EXCEPTIONAL_ACCESS_CHECK(1.20, 0.22, 0, "SUSTAINABLE")
```

---

#### `SOV_SDRS_ALLOCATION_IMPACT`
**Python:** `sdrs_allocation_impact(sdr_allocation, gdp, reserves, import_cover_pre)`

Calculates the marginal improvement to reserve adequacy from a new SDR allocation, assuming full pass-through to usable reserves.

| Parameter | Type | Description |
|---|---|---|
| `sdr_allocation` | float | SDR allocation amount (same currency as reserves/GDP) |
| `gdp` | float | GDP (for reserves/GDP calculation) |
| `reserves` | float | Pre-allocation FX reserves |
| `import_cover_pre` | float | Pre-allocation import cover in months |

**Returns:** 4-row table: reserves, reserves/GDP, import cover — pre, post, and change.

**Excel example:**
```
=SOV_SDRS_ALLOCATION_IMPACT(2e9, 50e9, 8e9, 2.1)
```

---

### Event Studies & Early Warning

---

#### `SOV_RESTRUCTURING_COMPARABLES`
**Python:** `restructuring_comparables(debt_gdp, spread_bps, reserves_months, haircut_comparables)`

Nearest-neighbour matching against 15 canonical historical sovereign restructuring episodes (Argentina 2001, Greece 2012, Ecuador 1999, etc.) using Euclidean distance on normalised pre-crisis fundamentals. Returns the top 5 matches with haircut, recovery rate, and time-to-resolution, plus distance-weighted averages.

| Parameter | Type | Description |
|---|---|---|
| `debt_gdp` | float | Current debt-to-GDP |
| `spread_bps` | float | Current sovereign spread in basis points |
| `reserves_months` | float | Current import cover in months |
| `haircut_comparables` | float | (Unused; retained for future calibration) |

**Returns:** Table of top-5 comparables + weighted-average haircut, recovery rate, and months to resolution.

**Excel example:**
```
=SOV_RESTRUCTURING_COMPARABLES(1.10, 3200, 1.5, 0)
```

---

#### `SOV_EVENT_STUDY_SPREAD`
**Python:** `event_study_spread_reaction(spread_series, event_dates_serial, window_before, window_after)`

Computes the average abnormal spread change around a set of events with 95% confidence bands. For each event, the pre-event window mean is subtracted as a baseline, then abnormal changes are averaged across all events.

| Parameter | Type | Description |
|---|---|---|
| `spread_series` | float range | Daily spread time series |
| `event_dates_serial` | float range | 0-based indices of event dates within the spread series |
| `window_before` | integer | Days of pre-event window used as baseline (≥ 1) |
| `window_after` | integer | Days of post-event window to track (≥ 1) |

**Returns:** Table: day relative to event, mean abnormal spread, CI95 lower/upper, plus `n_events_used`.

**Excel example:**
```
=SOV_EVENT_STUDY_SPREAD(B2:B500, E2:E10, 20, 10)
```
Average spread reaction to 9 events, 20 days before and 10 days after.

---

#### `SOV_CRISIS_EARLY_WARNING`
**Python:** `crisis_early_warning_signal(indicator_values, thresholds)`

Kaminsky-Lizondo-Reinhart (1999) signal extraction approach. Issues a signal for each indicator that breaches its crisis threshold, then returns a composite traffic-light assessment:

| Signal Ratio | Traffic Light |
|---|---|
| ≥ 60% of indicators | 🔴 RED |
| 30–60% | 🟡 AMBER |
| < 30% | 🟢 GREEN |

| Parameter | Type | Description |
|---|---|---|
| `indicator_values` | float range | Current values of each early-warning indicator |
| `thresholds` | float range | Crisis threshold for each indicator (same length) |

**Returns:** Table: n_indicators, n_signals_active, signal_ratio, noise-to-signal ratio, traffic light, plus per-indicator signal flags.

**Excel example:**
```
=SOV_CRISIS_EARLY_WARNING(B2:B8, C2:C8)
```
7 indicators vs. their respective thresholds.

---

### Inline Charts (Plotting)

These functions render Matplotlib charts to PNG and return them as **PyXLL inline images**, so the chart appears directly inside the Excel cell — no VBA, no popup windows. Results are LRU-cached (up to 128 entries) so recalculation skips re-rendering when inputs haven't changed.

---

#### `SDXL_PLOT_YIELD_CURVE`
**Python:** `sdxl_plot_yield_curve(tenors, yields, title, x_label, y_label, width_px, height_px, style)`

Plots a yield curve (tenor on x-axis, yield on y-axis) and returns an inline chart image.  
If all yield values are ≤ 1.0, they are treated as decimal fractions and the y-axis is automatically formatted as a percentage.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `tenors` | float range | — | Tenor values (numeric years or labels) |
| `yields` | float range | — | Yield values — must be the same length as `tenors` |
| `title` | string | `"Yield Curve"` | Chart title |
| `x_label` | string | `"Tenor"` | X-axis label |
| `y_label` | string | `"Yield"` | Y-axis label (auto-appended with `(%)` when decimal yields detected) |
| `width_px` | integer | `800` | Output image width in pixels |
| `height_px` | integer | `450` | Output image height in pixels |
| `style` | string | `"line"` | `"line"` for a plain line; `"markers"` to add circle markers |

**Returns:** A PyXLL inline image (PNG rendered at `width_px × height_px`).

**Excel example:**
```
=SDXL_PLOT_YIELD_CURVE(A2:A10, B2:B10, "UST Curve", "Tenor (yrs)", "Yield", 900, 500)
```
Plots the on-the-run US Treasury curve stored in columns A and B.

---

#### `SDXL_PLOT_TIMESERIES`
**Python:** `sdxl_plot_timeseries(dates, values, title, width_px, height_px)`

Plots a single time series (date on x-axis, value on y-axis) with automatic date-tick formatting and returns an inline chart image.  
`dates` can be Excel serial date numbers, ISO date strings (`"2024-01-31"`), or Python `datetime.date` objects.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `dates` | date range | — | Date values for the x-axis |
| `values` | float range | — | Numeric values — must be the same length as `dates` |
| `title` | string | `"Time Series"` | Chart title |
| `width_px` | integer | `800` | Output image width in pixels |
| `height_px` | integer | `450` | Output image height in pixels |

**Returns:** A PyXLL inline image (PNG rendered at `width_px × height_px`).

**Excel example:**
```
=SDXL_PLOT_TIMESERIES(A2:A300, B2:B300, "10yr Yield")
```
Plots 300 daily observations of the 10-year benchmark yield.

---

#### `SDXL_PLOT_ROLLING_AVG`
**Python:** `sdxl_plot_rolling_avg(dates, values, window, title, width_px, height_px)`

Plots the original series (light blue, semi-transparent) overlaid with a trailing rolling mean (bold blue) and returns an inline chart image.  
The rolling mean is `NaN` for the first `window − 1` positions (insufficient history) so the overlay begins only once a full window of data is available.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `dates` | date range | — | Date values for the x-axis |
| `values` | float range | — | Numeric values — must be the same length as `dates` |
| `window` | integer | `20` | Number of periods in the rolling window (must be ≥ 1) |
| `title` | string | `"Rolling Average"` | Chart title |
| `width_px` | integer | `800` | Output image width in pixels |
| `height_px` | integer | `450` | Output image height in pixels |

**Returns:** A PyXLL inline image (PNG rendered at `width_px × height_px`).

**Excel example:**
```
=SDXL_PLOT_ROLLING_AVG(A2:A300, B2:B300, 20, "Rolling Avg (20)")
```
Plots daily CDS spreads with a 20-day rolling mean overlay.

**Error codes returned by all plotting functions:**

| Error | Cause |
|---|---|
| `#SDXL: no data` | Input range is empty |
| `#SDXL: length mismatch (x=N, y=M)` | Date and value ranges have different lengths |
| `#SDXL: window must be >= 1` | `SDXL_PLOT_ROLLING_AVG` window parameter is zero or negative |

---

## Error Handling

Every function returns an `#ERR: <message>` string (rather than crashing Excel) when inputs are invalid. Common error messages:

| Error | Cause |
|---|---|
| `#ERR: Empty values` | Input range contains no valid numbers |
| `#ERR: values and weights must have same length` | Mismatched range sizes |
| `#ERR: window must be > 0` | Invalid window parameter |
| `#ERR: All maturities must be positive` | Zero or negative tenor |
| `#ERR: …must be in [0, 1]` | Probability/share parameter out of range |

In Excel, wrap any formula in `IFERROR` to suppress error strings and substitute a default:
```
=IFERROR(SOV_WEIGHTED_AVERAGE(B2:B10, C2:C10), 0)
```

---

## Running the Tests

The test suite mocks PyXLL so it can run without an Excel installation:

```bash
# From the repo root
pip install pytest
python -m pytest
```

All 184 tests should pass in under 5 seconds.

---

## sovereign\_debt\_py plotting

`sovereign_debt_py` is a pure-Python analytics library (no PyXLL dependency)
included in this repository.  Its `plotting` subpackage provides Matplotlib-
based charting functions for all common sovereign-debt visualisations.

### Quick start

```python
from sovereign_debt_py.plotting import (
    plot_yield_curve,
    plot_timeseries,
    plot_rolling_average,
    plot_spread,
    plot_fan_chart,
    fig_to_png_bytes,
)
```

### Yield curve

```python
fig, ax = plot_yield_curve(
    [1, 2, 5, 10],       # tenors (years)
    [0.04, 0.045, 0.05, 0.052],  # yields (decimal)
    title="Sovereign Yield Curve",
    style="line+markers",   # "line" | "markers" | "line+markers"
    as_percent=True,        # format y-axis as 4.00%, 4.50%, …
)
fig.show()
```

### Time series

```python
import datetime

dates  = [datetime.date(2023, m, 1) for m in range(1, 13)]
yields = [0.04 + 0.001 * m for m in range(12)]

fig, ax = plot_timeseries(dates, yields, title="10Y Yield – 2023")
```

### Rolling average overlay

```python
fig, ax = plot_rolling_average(
    dates, yields,
    window=3,
    base_label="Raw yield",
    roll_label="3-month MA",
)
```

### Spread chart

```python
em_yields = [0.06 + 0.001 * i for i in range(6)]
us_yields = [0.04 + 0.001 * i for i in range(6)]

fig, ax = plot_spread(
    dates[:6], em_yields, us_yields,
    label_a="EM", label_b="US",
    spread_label="EM–US Spread",
)
```

### DSA fan chart

```python
x    = list(range(2024, 2031))
p50  = [60, 62, 64, 63, 61, 60, 59]

bands = {
    (0.10, 0.90): ([55] * 7, [70] * 7),
    (0.25, 0.75): ([58] * 7, [66] * 7),
}

fig, ax = plot_fan_chart(x, p50, bands, title="Debt/GDP Fan Chart")
```

### Export to PNG bytes (for embedding / reports)

```python
png: bytes = fig_to_png_bytes(fig, width_px=800, height_px=450, dpi=120)
# png starts with b'\x89PNG' and can be written to a file or embedded in Excel:
with open("chart.png", "wb") as f:
    f.write(png)
```
All 176 tests should pass in under 10 seconds.

---

## Extracting sovereign\_debt\_py

`sovereign_debt_py` is a pure-Python package (no PyXLL / Excel dependency) that
lives alongside the Excel add-in in this repo.  It currently exposes a
`plotting` subpackage (see the [section above](#sovereign_debt_py-plotting)) and
is designed to be usable from any Python environment — scripts, notebooks, web
apps, and CI pipelines.

If you want to move `sovereign_debt_py` into its own GitHub repository, a
step-by-step guide covering git-subtree / git-filter-repo extraction, CI setup,
and optional import-delegation back to `sovereign_debt_xl` is available at:

[`docs/extract-sovereign-debt-py.md`](docs/extract-sovereign-debt-py.md)

### Current layout

```
sovereign_debt_xl/              ← repo root
├── sovereign_debt_py/          ← pure-Python package (no PyXLL)
│   ├── __init__.py
│   └── plotting/
│       ├── __init__.py
│       ├── core.py             ← validation helpers + fig_to_png_bytes
│       ├── yield_curve.py      ← plot_yield_curve
│       ├── timeseries.py       ← plot_timeseries / plot_rolling_average / plot_spread
│       └── dsa.py              ← plot_fan_chart
├── sovereign_debt_xl/          ← PyXLL / Excel add-in package
│   └── *.py                    ← SOV_* Excel functions
├── test_plotting.py            ← pytest suite for sovereign_debt_py
├── pyproject.toml
└── requirements.txt
```

