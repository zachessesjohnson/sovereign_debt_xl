from sovereign_debt_xl.modeling import xl_correlation_matrix, xl_regression


def test_regression_simple():
    # y = 1 + 2x
    y = [1 + 2 * x for x in [1, 2, 3, 4]]
    X = [[1], [2], [3], [4]]
    table = xl_regression(y, X)
    # ensure it returns R2 row
    assert any(r[0] == "R2" for r in table)


def test_corr_matrix_shape():
    table = xl_correlation_matrix([[1, 2], [2, 4], [3, 6]])
    # header + 2 rows
    assert len(table) == 3
    assert len(table[0]) == 3
