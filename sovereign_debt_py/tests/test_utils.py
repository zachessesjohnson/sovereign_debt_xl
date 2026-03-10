from datetime import date

from sovereign_debt_py.utils import xl_array_shape, xl_date_diff_bus, xl_flatten


def test_array_shape():
    assert xl_array_shape([[1, 2], [3, 4]]) == [["rows", "cols"], [2, 2]]


def test_flatten():
    assert xl_flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]


def test_date_diff_bus_accepts_date():
    # Mon to Fri inclusive = 5
    assert xl_date_diff_bus(date(2026, 3, 2), date(2026, 3, 6)) == 5
