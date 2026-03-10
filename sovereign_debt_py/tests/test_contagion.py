import numpy as np

from sovereign_debt_py.contagion import (
    dcc_garch_correlation,
    granger_causality_spreads,
    sovereign_contagion_beta,
    trade_linkage_matrix,
)


# ---------------------------------------------------------------------------
# sovereign_contagion_beta
# ---------------------------------------------------------------------------

def test_contagion_beta_structure():
    rng = np.random.default_rng(0)
    n = 40
    src = rng.normal(300, 50, n).tolist()
    tgt = [s + rng.normal(0, 20) for s in src]
    gf = rng.normal(0, 1, n).tolist()
    table = sovereign_contagion_beta(tgt, src, gf, 10)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table if isinstance(r[0], str)]
    assert "mean_beta" in metrics


def test_contagion_beta_too_short():
    result = sovereign_contagion_beta([1.0] * 8, [1.0] * 8, [1.0] * 8, 5)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_contagion_beta_length_mismatch():
    result = sovereign_contagion_beta([1.0] * 20, [1.0] * 15, [1.0] * 20, 5)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# dcc_garch_correlation
# ---------------------------------------------------------------------------

def test_dcc_garch_structure():
    rng = np.random.default_rng(1)
    n = 50
    a = rng.normal(200, 30, n).tolist()
    b = [x + rng.normal(0, 15) for x in a]
    table = dcc_garch_correlation(a, b, 10)
    assert table[0] == ["metric", "value"]
    metrics = [r[0] for r in table if isinstance(r[0], str)]
    assert "mean_dcc" in metrics


def test_dcc_garch_correlation_range():
    rng = np.random.default_rng(2)
    n = 40
    a = rng.normal(0, 1, n).tolist()
    b = rng.normal(0, 1, n).tolist()
    table = dcc_garch_correlation(a, b, 8)
    mean_dcc = [r[1] for r in table if r[0] == "mean_dcc"][0]
    assert -1.0 <= mean_dcc <= 1.0


# ---------------------------------------------------------------------------
# granger_causality_spreads
# ---------------------------------------------------------------------------

def test_granger_causality_shape():
    rng = np.random.default_rng(3)
    # 3 countries, 30 periods
    data = [[rng.normal(300 + i * 50, 20) for i in range(3)] for _ in range(30)]
    table = granger_causality_spreads(data, 2, 0.10)
    # header + 3 rows
    assert len(table) == 4
    # each row has header + 3 values
    assert len(table[0]) == 4


def test_granger_causality_too_short():
    data = [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]  # only 3 rows
    result = granger_causality_spreads(data, 1, 0.10)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# trade_linkage_matrix
# ---------------------------------------------------------------------------

def test_trade_linkage_matrix_values():
    flows = [[0.0, 100.0, 50.0],
             [80.0, 0.0, 60.0],
             [40.0, 70.0, 0.0]]
    gdp = [1000.0, 2000.0, 1500.0]
    table = trade_linkage_matrix(flows, gdp)
    # header row + 3 data rows
    assert len(table) == 4
    # exposure[0, 1] = 100 / 2000 = 0.05
    assert abs(table[1][2] - 0.05) < 1e-6


def test_trade_linkage_matrix_non_square():
    flows = [[0.0, 100.0], [80.0, 0.0], [40.0, 70.0]]
    gdp = [1000.0, 2000.0, 1500.0]
    result = trade_linkage_matrix(flows, gdp)
    assert isinstance(result, str) and result.startswith("#ERR:")
