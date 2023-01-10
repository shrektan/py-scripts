import writexlsx as w
import pandas as pd


def test_write(tmp_path) -> None:
    df = pd.DataFrame({
        "Col1": [1, 2.0, 3],
        "Col2": pd.Series(pd.date_range("2022-01-02", periods=3)),
        "Col3": ["ABC", "BCD", "EFFFF"]
    })

    df2 = pd.DataFrame({
        "Col1": [12, 12.455, 13],
        "Col2": pd.Series(pd.date_range("2023-09-02", periods=3)),
        "Col3": ["ABC", "BCD", "EFFFF"]
    })
    df2.set_index("Col2")

    excel = (tmp_path / "test.xlsx")
    w.write({"表1": df, "S2": df2}, excel, open=True, overwrite=True)
