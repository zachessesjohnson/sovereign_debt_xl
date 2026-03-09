# sovereign_debt_py

Pure-Python library for sovereign debt analysis — a PyXLL-free mirror of
[sovereign_debt_xl](https://github.com/zachessesjohnson/sovereign_debt_xl).

All Excel-specific `@xl_func` decorators have been removed; every function is
a plain Python callable you can use in notebooks, scripts, or other packages.

## Installation

```bash
pip install sovereign-debt-py
```

Or, directly from source:

```bash
pip install .
```

## Modules

| Module | Functions |
|--------|-----------|
| `averaging` | Weighted average, rolling average, trimmed mean, descriptive stats |
| `indexing` | Rank percentile, z-score, min-max normalisation, index rebasing |
| `forecasting` | Linear forecast, exponential smoothing, Holt, moving-average, seasonal decompose |
| `modeling` | OLS regression, correlation matrix, Monte Carlo, scenario table |
| `utils` | Array shape, flatten, business-day count |
| `fiscal` | Debt trajectory, fiscal reaction function, implicit interest rate, debt-stabilising PB |
| `credit_risk` | Merton default probability, CDS-implied PD, sovereign z-score, spread decomposition |
| `yield_curve` | Nelson-Siegel fit, z-spread, carry & rolldown, asset-swap spread |
| `reserves` | Reserve adequacy metrics, BoP financing gap, REER misalignment |
| `stress` | Fan-chart debt, contingent liability shock, FX passthrough |
| `amortization` | Amortization profile, weighted average maturity, gross financing need |
| `political_esg` | Political risk score, ESG sovereign score, sanctions exposure index |
| `contagion` | Contagion beta, DCC-GARCH correlation, Granger causality, trade linkage matrix |
| `debt_composition` | Original sin index, hidden debt estimator, transparency score, collateralised-debt flag |
| `macro_financial` | Sovereign–bank nexus, monetary financing risk, r−g differential, dollarisation vulnerability |
| `market_microstructure` | Liquidity score, local-vs-external basis, auction tail analysis, investor-base concentration |
| `imf_framework` | DSA replication, IMF program probability, exceptional access check, SDR allocation impact |
| `event_studies` | Restructuring comparables, event-study spread reaction, crisis early-warning signal |

## Quick start

```python
from sovereign_debt_py import xl_weighted_average, debt_trajectory_forecast

result = xl_weighted_average([1, 2, 3], [0.2, 0.3, 0.5])
print(result)  # 2.3

trajectory = debt_trajectory_forecast(
    gdp_growth_path=[0.03, 0.03, 0.03],
    primary_balance_path=[0.01, 0.01, 0.01],
    interest_rate_path=[0.04, 0.04, 0.04],
    initial_debt_gdp=0.60,
    years=3,
)
print(trajectory)
```

## Requirements

- Python ≥ 3.11
- numpy, pandas, scipy, statsmodels, scikit-learn
