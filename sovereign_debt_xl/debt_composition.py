from __future__ import annotations

from typing import Any

import numpy as np
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats


@xl_func(
    "float fx_denominated_debt, float total_debt, float local_currency_debt_held_by_nonresidents: object[][]",
    name="SOV_ORIGINAL_SIN_INDEX",
)
def original_sin_index(
    fx_denominated_debt: float,
    total_debt: float,
    local_currency_debt_held_by_nonresidents: float,
) -> list[list[Any]] | str:
    """Eichengreen-Hausmann original sin metric plus the 'original sin redux'.

    Original sin (OSin): share of debt denominated in foreign currency.
    OSin_redux: share of local-currency debt held by non-residents, capturing
    the 'original sin redux' where FX risk is held by domestic balance sheets
    exposed to non-resident outflows.

    Returns both measures and a composite.
    """
    try:
        fx = float(fx_denominated_debt)
        total = float(total_debt)
        lc_nonres = float(local_currency_debt_held_by_nonresidents)
        if total <= 0:
            return safe_err(ValueError("total_debt must be > 0"))
        if fx < 0 or lc_nonres < 0:
            return safe_err(ValueError("Debt components must be >= 0"))
        if fx > total:
            return safe_err(ValueError("fx_denominated_debt cannot exceed total_debt"))
        osin = fx / total
        lc_debt = total - fx
        osin_redux = lc_nonres / lc_debt if lc_debt > 0 else float("nan")
        # Composite: simple average of the two measures, treating NaN as 0
        composite = (osin + (osin_redux if not np.isnan(osin_redux) else 0.0)) / 2.0
        return [
            ["metric", "value"],
            ["original_sin_osin", round(osin, 4)],
            ["original_sin_redux", round(osin_redux, 4) if not np.isnan(osin_redux) else float("nan")],
            ["composite_fx_vulnerability", round(composite, 4)],
            ["fx_denominated_share", round(osin, 4)],
            ["lc_nonresident_share", round(osin_redux, 4) if not np.isnan(osin_redux) else float("nan")],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float reported_public_debt, float soe_guaranteed_debt, float ppp_commitments,"
    " float central_bank_quasi_fiscal, float local_govt_off_budget: object[][]",
    name="SOV_HIDDEN_DEBT_ESTIMATOR",
)
def hidden_debt_estimator(
    reported_public_debt: float,
    soe_guaranteed_debt: float,
    ppp_commitments: float,
    central_bank_quasi_fiscal: float,
    local_govt_off_budget: float,
) -> list[list[Any]] | str:
    """Augmented debt figure aggregating off-balance-sheet and contingent exposures.

    Follows the Kose/Nagle/Ohnsorge framework for comprehensive public-sector debt.
    Returns the augmented total and each component as a share of the reported figure.
    """
    try:
        reported = float(reported_public_debt)
        soe = float(soe_guaranteed_debt)
        ppp = float(ppp_commitments)
        cb = float(central_bank_quasi_fiscal)
        lg = float(local_govt_off_budget)
        if reported < 0:
            return safe_err(ValueError("reported_public_debt must be >= 0"))
        for name, val in [("soe", soe), ("ppp", ppp), ("cb", cb), ("lg", lg)]:
            if val < 0:
                return safe_err(ValueError(f"{name} component must be >= 0"))
        off_balance = soe + ppp + cb + lg
        augmented = reported + off_balance
        base = reported if reported > 0 else 1.0
        return [
            ["metric", "value"],
            ["reported_debt", round(reported, 4)],
            ["soe_guaranteed_debt", round(soe, 4)],
            ["ppp_commitments", round(ppp, 4)],
            ["cb_quasi_fiscal", round(cb, 4)],
            ["local_govt_off_budget", round(lg, 4)],
            ["total_off_balance_sheet", round(off_balance, 4)],
            ["augmented_debt", round(augmented, 4)],
            ["hidden_debt_pct_of_reported", round(off_balance / base * 100.0, 2)],
        ]
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float imf_sdds_subscriber, float debt_reporting_frequency, float coverage_of_soe,"
    " float coverage_of_subnational, float arrears_reporting: object[][]",
    name="SOV_DEBT_TRANSPARENCY_SCORE",
)
def debt_transparency_score(
    imf_sdds_subscriber: float,
    debt_reporting_frequency: float,
    coverage_of_soe: float,
    coverage_of_subnational: float,
    arrears_reporting: float,
) -> list[list[Any]] | str:
    """Data quality and reporting completeness score (0–100).

    Higher score = more transparent; flags where published figures may be understated.

    Inputs (all expected in [0, 1] unless stated):
    - imf_sdds_subscriber: 1 = SDDS subscriber, 0 = not
    - debt_reporting_frequency: 1 = quarterly+, 0.5 = annual, 0 = none
    - coverage_of_soe: share of SOE debt covered in public debt statistics
    - coverage_of_subnational: share of subnational debt covered
    - arrears_reporting: 1 = arrears reported, 0 = not
    """
    try:
        sdds = float(imf_sdds_subscriber)
        freq = float(debt_reporting_frequency)
        soe = float(coverage_of_soe)
        sub = float(coverage_of_subnational)
        arr = float(arrears_reporting)
        for name, val in [("imf_sdds_subscriber", sdds), ("debt_reporting_frequency", freq),
                          ("coverage_of_soe", soe), ("coverage_of_subnational", sub),
                          ("arrears_reporting", arr)]:
            if not (0.0 <= val <= 1.0):
                return safe_err(ValueError(f"{name} must be in [0, 1]"))
        # Weights summing to 1
        weights = [0.20, 0.20, 0.25, 0.20, 0.15]
        values = [sdds, freq, soe, sub, arr]
        composite = sum(w * v for w, v in zip(weights, values)) * 100.0
        flags: list[str] = []
        if soe < 0.5:
            flags.append("SOE_COVERAGE_LOW")
        if sub < 0.5:
            flags.append("SUBNATIONAL_COVERAGE_LOW")
        if freq < 0.5:
            flags.append("REPORTING_FREQUENCY_LOW")
        if sdds == 0:
            flags.append("NOT_SDDS_SUBSCRIBER")
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["transparency_score_0_100", round(composite, 2)])
        out.append(["sdds_score", round(sdds * 100, 1)])
        out.append(["frequency_score", round(freq * 100, 1)])
        out.append(["soe_coverage_score", round(soe * 100, 1)])
        out.append(["subnational_coverage_score", round(sub * 100, 1)])
        out.append(["arrears_reporting_score", round(arr * 100, 1)])
        out.append(["flags", "; ".join(flags) if flags else "none"])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float resource_backed_loans, float total_debt, float export_revenues, str resource_type: object[][]",
    name="SOV_COLLATERALIZED_DEBT_FLAG",
)
def collateralized_debt_flag(
    resource_backed_loans: float,
    total_debt: float,
    export_revenues: float,
    resource_type: str,
) -> list[list[Any]] | str:
    """Identify and quantify resource-collateralised borrowing.

    Returns the share of total debt that is resource-backed and the share of
    annual export revenues effectively pre-committed (pledged) to debt service.
    Common in Sub-Saharan Africa (oil, mineral-backed loans).
    """
    try:
        rbl = float(resource_backed_loans)
        td = float(total_debt)
        er = float(export_revenues)
        rtype = str(resource_type).strip()
        if td <= 0:
            return safe_err(ValueError("total_debt must be > 0"))
        if rbl < 0 or er < 0:
            return safe_err(ValueError("resource_backed_loans and export_revenues must be >= 0"))
        rbl_share_of_debt = rbl / td
        pledged_share_of_exports = rbl / er if er > 0 else float("nan")
        risk_flag = "HIGH" if rbl_share_of_debt > 0.25 else ("MEDIUM" if rbl_share_of_debt > 0.10 else "LOW")
        return [
            ["metric", "value"],
            ["resource_type", rtype],
            ["resource_backed_loans", round(rbl, 4)],
            ["resource_backed_share_of_debt", round(rbl_share_of_debt, 4)],
            ["pledged_share_of_exports", round(pledged_share_of_exports, 4) if not np.isnan(pledged_share_of_exports) else float("nan")],
            ["concentration_risk_flag", risk_flag],
        ]
    except Exception as e:
        return safe_err(e)
