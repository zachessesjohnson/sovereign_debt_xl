import math

from sovereign_debt_py.averaging import (
    xl_describe,
    xl_rolling_average,
    xl_trimmed_mean,
    xl_weighted_average,
)


def test_weighted_average_basic():
    assert xl_weighted_average([1, 2, 3], [1, 1, 2]) == 2.25


def test_weighted_average_mismatch():
    assert str(xl_weighted_average([1, 2], [1])).startswith("#ERR:")


def test_rolling_average_window_2():
    out = xl_rolling_average([1, 2, 3, 4], 2)
    assert out == [1.0, 1.5, 2.5, 3.5]


def test_trimmed_mean_basic():
    assert xl_trimmed_mean([1, 2, 100], 1 / 3) == 2.0


def test_describe_contains_mean():
    table = xl_describe([1, 2, 3])
    assert table[0] == ["stat", "value"]
    # find mean row
    mean_row = [r for r in table if r[0] == "mean"][0]
    assert math.isclose(mean_row[1], 2.0)
