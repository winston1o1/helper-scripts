from excel_tooling.toolbox import toolbox


class _FakeDataFrame:
    """Minimal stand-in for ``pd.DataFrame`` used by ``toolbox``."""

    def __init__(self, columns, rows_by_column):
        self._columns = columns
        self._rows = rows_by_column
        self.columns = self

    def to_list(self):
        return self._columns

    def __getitem__(self, key):
        return self._rows[key]


class _FakeWorksheet:
    def __init__(self):
        self.sets = []

    def set_column(self, first, last, width):
        self.sets.append((first, last, width))


def test_calculate_column_width_pads_short_values():
    df = _FakeDataFrame(
        columns=["name", "age"],
        rows_by_column={"name": ["alice", "bob"], "age": [1, 22]},
    )
    # "name": len("name") + 3 = 7 vs longest "alice" (5) -> 7
    # "age":  len("age") + 3 = 6 vs longest "22" (2) -> 6
    assert toolbox.calculate_column_width(df) == [7, 6]


def test_calculate_column_width_uses_longest_value():
    df = _FakeDataFrame(
        columns=["x"],
        rows_by_column={"x": ["a_very_long_value"]},
    )
    # "x": len("x") + 3 = 4 vs longest value (17) -> 17
    assert toolbox.calculate_column_width(df) == [17]


def test_auto_fit_column_width():
    worksheet = _FakeWorksheet()
    result = toolbox.auto_fit_column_width([7, 6], worksheet)
    assert result is worksheet
    assert worksheet.sets == [(0, 0, 7), (1, 1, 6)]
