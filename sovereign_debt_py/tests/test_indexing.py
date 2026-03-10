import math

from sovereign_debt_py.indexing import xl_index_to_base, xl_normalize_minmax, xl_rank_pct, xl_zscore


def test_rank_pct_medianish():
    p = xl_rank_pct(2, [1, 2, 3])
    assert 0.0 <= p <= 1.0


def test_zscore_zero_mean():
    z = xl_zscore([1, 2, 3])
    assert len(z) == 3
    assert math.isclose(sum(z), 0.0, abs_tol=1e-9)


def test_normalize_minmax_bounds():
    out = xl_normalize_minmax([10, 20, 30])
    assert out[0] == 0.0 and out[-1] == 1.0


def test_index_to_base():
    out = xl_index_to_base([100, 110, 120], 1)
    assert all(math.isclose(a, b) for a, b in zip(out, [100.0, 110.0, 120.0])), (
        f"Expected [100.0, 110.0, 120.0], got {out}"
    )
