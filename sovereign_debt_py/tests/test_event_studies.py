import numpy as np

from sovereign_debt_py.event_studies import (
    crisis_early_warning_signal,
    event_study_spread_reaction,
    restructuring_comparables,
)


# ---------------------------------------------------------------------------
# restructuring_comparables
# ---------------------------------------------------------------------------

def test_restructuring_comparables_structure():
    table = restructuring_comparables(0.90, 1500.0, 2.0, 0.0)
    assert table[0][0] == "rank"
    # 5 comparables + blank + weighted_avg = 8 data rows
    assert len(table) >= 7


def test_restructuring_comparables_ranked_ascending():
    table = restructuring_comparables(0.90, 1500.0, 2.0, 0.0)
    data_rows = [r for r in table[1:] if isinstance(r[0], int)]
    distances = [r[9] for r in data_rows]
    assert distances == sorted(distances)


def test_restructuring_comparables_haircut_in_range():
    table = restructuring_comparables(0.70, 800.0, 3.0, 0.0)
    avg_row = [r for r in table if r[0] == "weighted_avg"][0]
    haircut = avg_row[6]
    assert 0.0 <= haircut <= 100.0


# ---------------------------------------------------------------------------
# event_study_spread_reaction
# ---------------------------------------------------------------------------

def test_event_study_structure():
    rng = np.random.default_rng(5)
    spreads = rng.normal(300, 30, 100).tolist()
    events = [20, 50, 75]
    table = event_study_spread_reaction(spreads, events, 5, 5)
    assert table[0] == ["day_rel_event", "mean_abnormal_spread", "ci95_lower", "ci95_upper"]


def test_event_study_n_events_row():
    rng = np.random.default_rng(6)
    spreads = rng.normal(300, 30, 80).tolist()
    events = [15, 40, 60]
    table = event_study_spread_reaction(spreads, events, 5, 5)
    n_row = [r for r in table if r[0] == "n_events_used"]
    assert n_row, "Expected n_events_used row"
    assert n_row[0][1] >= 1


def test_event_study_too_short():
    result = event_study_spread_reaction([1.0] * 5, [2], 3, 3)
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_event_study_no_events():
    result = event_study_spread_reaction([1.0] * 50, [], 5, 5)
    assert isinstance(result, str) and result.startswith("#ERR:")


# ---------------------------------------------------------------------------
# crisis_early_warning_signal
# ---------------------------------------------------------------------------

def test_ews_all_breach():
    vals = [1.5, 2.0, 0.8]
    thresholds = [1.0, 1.5, 0.5]
    table = crisis_early_warning_signal(vals, thresholds)
    n_signals = [r[1] for r in table if r[0] == "n_signals_active"][0]
    assert n_signals == 3
    light = [r[1] for r in table if r[0] == "traffic_light"][0]
    assert light == "RED"


def test_ews_none_breach():
    vals = [0.5, 1.0, 0.3]
    thresholds = [1.0, 1.5, 0.5]
    table = crisis_early_warning_signal(vals, thresholds)
    n_signals = [r[1] for r in table if r[0] == "n_signals_active"][0]
    assert n_signals == 0
    light = [r[1] for r in table if r[0] == "traffic_light"][0]
    assert light == "GREEN"


def test_ews_length_mismatch():
    result = crisis_early_warning_signal([1.0, 2.0], [1.0])
    assert isinstance(result, str) and result.startswith("#ERR:")


def test_ews_empty():
    result = crisis_early_warning_signal([], [])
    assert isinstance(result, str) and result.startswith("#ERR:")
