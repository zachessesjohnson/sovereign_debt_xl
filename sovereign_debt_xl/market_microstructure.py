from __future__ import annotations

from typing import Any

import numpy as np
from pyxll import xl_func

from ._coerce import safe_err, to_1d_floats, to_2d_list


@xl_func(
    "float[] bid_ask_spreads, float[] turnover_ratios, float[] issue_sizes: object[][]",
    name="SOV_BID_ASK_LIQUIDITY_SCORE",
)
def bid_ask_liquidity_score(
    bid_ask_spreads: Any,
    turnover_ratios: Any,
    issue_sizes: Any,
) -> list[list[Any]] | str:
    """Composite liquidity score for a sovereign's bond curve (0–100; higher = more liquid).

    Weights bid-ask tightness (40%), turnover ratios (35%), and benchmark size (25%).

    Inputs (all arrays of equal length, one entry per bond):
    - bid_ask_spreads: bid-ask spread in bps per bond (lower is better; caps at 200 bps)
    - turnover_ratios: turnover as fraction of outstanding (higher is better; caps at 2×)
    - issue_sizes: outstanding face value per bond (USD bn; higher is better; caps at 20 bn)
    """
    try:
        ba = np.array(to_1d_floats(bid_ask_spreads), dtype=float)
        to = np.array(to_1d_floats(turnover_ratios), dtype=float)
        sz = np.array(to_1d_floats(issue_sizes), dtype=float)
        n = len(ba)
        if n == 0:
            return safe_err(ValueError("bid_ask_spreads must not be empty"))
        if len(to) != n or len(sz) != n:
            return safe_err(ValueError("All arrays must have the same length"))
        # Normalise to 0–100 (higher = more liquid)
        ba_score = np.clip(100.0 - ba / 200.0 * 100.0, 0.0, 100.0)
        to_score = np.clip(to / 2.0 * 100.0, 0.0, 100.0)
        sz_score = np.clip(sz / 20.0 * 100.0, 0.0, 100.0)
        bond_scores = 0.40 * ba_score + 0.35 * to_score + 0.25 * sz_score
        composite = float(np.mean(bond_scores))
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["composite_liquidity_score", round(composite, 2)])
        out.append(["mean_bid_ask_score", round(float(np.mean(ba_score)), 2)])
        out.append(["mean_turnover_score", round(float(np.mean(to_score)), 2)])
        out.append(["mean_size_score", round(float(np.mean(sz_score)), 2)])
        out.append(["", ""])
        out.append(["bond_index", "bond_liquidity_score"])
        for i, s in enumerate(bond_scores.tolist()):
            out.append([i + 1, round(s, 2)])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] local_currency_yields, float[] cross_currency_swap_rates,"
    " float[] usd_yields, float[] tenors: object[][]",
    name="SOV_LOCAL_VS_EXTERNAL_BASIS",
)
def local_vs_external_curve_basis(
    local_currency_yields: Any,
    cross_currency_swap_rates: Any,
    usd_yields: Any,
    tenors: Any,
) -> list[list[Any]] | str:
    """Cross-currency basis-adjusted spread: local vs. external curve comparison.

    hedged_local_yield = local_yield − cross_currency_swap_rate
    basis_spread = hedged_local_yield − usd_yield
    Positive basis = local bonds cheaper on a hedged basis.

    All arrays must share the same tenors vector.
    """
    try:
        lc = np.array(to_1d_floats(local_currency_yields), dtype=float)
        xccy = np.array(to_1d_floats(cross_currency_swap_rates), dtype=float)
        usd = np.array(to_1d_floats(usd_yields), dtype=float)
        t = np.array(to_1d_floats(tenors), dtype=float)
        n = len(lc)
        if n == 0:
            return safe_err(ValueError("local_currency_yields must not be empty"))
        if len(xccy) != n or len(usd) != n or len(t) != n:
            return safe_err(ValueError("All arrays must have the same length"))
        hedged = lc - xccy
        basis = hedged - usd
        out: list[list[Any]] = [["tenor", "local_yield", "hedged_local_yield", "usd_yield", "basis_spread"]]
        for i in range(n):
            out.append([
                round(float(t[i]), 2),
                round(float(lc[i]), 4),
                round(float(hedged[i]), 4),
                round(float(usd[i]), 4),
                round(float(basis[i]), 4),
            ])
        out.append(["", "", "", "", ""])
        out.append(["mean_basis", "", "", "", round(float(np.mean(basis)), 4)])
        out.append(["recommendation", "", "", "", "local_cheaper" if float(np.mean(basis)) > 0 else "external_cheaper"])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[][] auction_results, float[] bid_cover_ratios, float[] cutoff_vs_when_issued: object[][]",
    name="SOV_AUCTION_TAIL_ANALYSIS",
)
def auction_tail_analysis(
    auction_results: Any,
    bid_cover_ratios: Any,
    cutoff_vs_when_issued: Any,
) -> list[list[Any]] | str:
    """Analyze primary market reception by tracking tail sizes and bid-to-cover trends.

    auction_results: T × 2 matrix of [auction_date_serial, tail_bps] per auction.
    bid_cover_ratios: T-length vector of bid-to-cover ratios.
    cutoff_vs_when_issued: T-length vector of cutoff yield minus WI yield (bps; positive = auction cheap).

    Returns trend statistics and flags deteriorating demand.
    """
    try:
        grid = to_2d_list(auction_results)
        if not grid:
            return safe_err(ValueError("auction_results is empty"))
        start = 1 if isinstance(grid[0][0], str) else 0
        data_rows = grid[start:]
        if len(data_rows) < 3:
            return safe_err(ValueError("Need at least 3 auction observations"))
        try:
            tails = np.array([float(row[1]) for row in data_rows], dtype=float)
        except (IndexError, ValueError):
            return safe_err(ValueError("auction_results must have [date, tail_bps] columns"))
        bc = np.array(to_1d_floats(bid_cover_ratios), dtype=float)
        cwi = np.array(to_1d_floats(cutoff_vs_when_issued), dtype=float)
        n = len(tails)
        if len(bc) != n or len(cwi) != n:
            return safe_err(ValueError("All inputs must have the same number of observations"))
        # Trend: positive slope in tail or negative slope in bid-cover = deterioration
        x = np.arange(n, dtype=float)
        from scipy.stats import linregress
        tail_slope, _, _, tail_p, _ = linregress(x, tails)
        bc_slope, _, _, bc_p, _ = linregress(x, bc)
        cwi_slope, _, _, cwi_p, _ = linregress(x, cwi)
        demand_flag = "DETERIORATING" if (tail_slope > 0 and tail_p < 0.10) or (bc_slope < 0 and bc_p < 0.10) else "STABLE"
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["n_auctions", n])
        out.append(["mean_tail_bps", round(float(np.mean(tails)), 2)])
        out.append(["mean_bid_cover", round(float(np.mean(bc)), 2)])
        out.append(["mean_cutoff_vs_wi_bps", round(float(np.mean(cwi)), 2)])
        out.append(["tail_trend_slope", round(float(tail_slope), 4)])
        out.append(["tail_trend_pvalue", round(float(tail_p), 4)])
        out.append(["bid_cover_trend_slope", round(float(bc_slope), 4)])
        out.append(["bid_cover_trend_pvalue", round(float(bc_p), 4)])
        out.append(["demand_flag", demand_flag])
        return out
    except Exception as e:
        return safe_err(e)


@xl_func(
    "float[] holdings_by_type: object[][]",
    name="SOV_INVESTOR_BASE_CONCENTRATION",
)
def investor_base_concentration(
    holdings_by_type: Any,
) -> list[list[Any]] | str:
    """Herfindahl index over investor holder types.

    holdings_by_type: shares (or absolute values) for each investor class
    (e.g. domestic banks, foreign real money, central banks, retail, etc.).

    Returns the HHI (0–1), its normalised version (0–1), and the equivalent
    number of holders, plus a concentration flag.
    """
    try:
        h = np.array(to_1d_floats(holdings_by_type), dtype=float)
        if len(h) == 0:
            return safe_err(ValueError("holdings_by_type must not be empty"))
        if np.any(h < 0):
            return safe_err(ValueError("All holdings values must be >= 0"))
        total = float(np.sum(h))
        if total == 0:
            return safe_err(ValueError("Total holdings are zero"))
        shares = h / total
        hhi = float(np.sum(shares**2))
        n = len(h)
        hhi_norm = (hhi - 1.0 / n) / (1.0 - 1.0 / n) if n > 1 else 1.0
        eq_holders = 1.0 / hhi if hhi > 0 else float("inf")
        flag = "HIGH" if hhi > 0.25 else ("MEDIUM" if hhi > 0.15 else "LOW")
        out: list[list[Any]] = [["metric", "value"]]
        out.append(["hhi_raw", round(hhi, 4)])
        out.append(["hhi_normalised", round(hhi_norm, 4)])
        out.append(["equivalent_n_holders", round(eq_holders, 2)])
        out.append(["concentration_flag", flag])
        out.append(["", ""])
        out.append(["holder_index", "share"])
        for i, s in enumerate(shares.tolist()):
            out.append([i + 1, round(s, 4)])
        return out
    except Exception as e:
        return safe_err(e)
