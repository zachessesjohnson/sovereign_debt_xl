# sovereign_debt_xl

A [PyXLL](https://www.pyxll.com/) Excel add-in that exposes Python UDFs for sovereign debt analysis: debt sustainability modelling, yield curve fitting, risk metrics, macro-financial linkages, and inline Matplotlib charts — directly in Excel cells with no VBA, no context switching.

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

