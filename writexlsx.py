"""## Write Dataframe to Excel(xlsx) with customized styles
Similar to the `to_excel()` method of Pandas's Dataframe.
However, it will set a wider column width for `date` and `datetime`
objects. The font, the background color and the cell grid line will
be set accordingly.

## Main Feature
1. Set the font to *微软雅黑 + Arial*
1. The index always starts from 1 instead of 0
1. Set horizontal line but no vertical line
1. Set the background of the header to heavy blue and the forefont header to white
1. Enable the filter by default
1. Support *comma* and *percent* formatting when specifying the columns, or
   auto-detecting
1. Support multiple Dataframe in `list`, `tuple` or `dict` to be written
   as multiple worksheets or horizontally aligned
1. Support to set the Excel's table style
1. Support to write to tmp file with proper name then open in MS Excel, which is
   quite convinient when exploring data

## Plan
Plan to submit to `pip` when matured

## Dependencies:
- `xlsxwriter`: https://xlsxwriter.readthedocs.io
"""
import xlsxwriter as xw
import pandas as pd
from pathlib import Path
import subprocess
from typing import Callable, Optional

Dict_DF = dict[str, pd.DataFrame]
Styler = Callable[[pd.DataFrame, xw.workbook.Worksheet], None]


def check_elem_df(x: dict) -> None:
    for v in x.values():
        if not isinstance(v, pd.DataFrame):
            raise TypeError(
                f"all elem of df must be DataFrame, but find {type(v)}")


def make_dict(df: pd.DataFrame | Dict_DF |
              tuple[pd.DataFrame] | list[pd.DataFrame]) -> Dict_DF:
    if isinstance(df, dict):
        x = df
    elif isinstance(df, pd.DataFrame):
        x = {"Sheet1": df}
    elif isinstance(df, tuple) or isinstance(df, list):
        x = {}
        for (i, v) in enumerate(df):
            x["Sheet" + str(i + 1)] = v
    else:
        raise TypeError("the type of df must be one of DataFrame, dict, tuple or list. "
                        f"now it's {type(df)}")
    check_elem_df(x)
    return x


def set_date_col_width(df: pd.DataFrame, sheet: xw.workbook.Worksheet) -> None:
    raise NotImplementedError


def set_header(df: pd.DataFrame, sheet: xw.workbook.Worksheet) -> None:
    raise NotImplementedError


def set_grid(df: pd.DataFrame, sheet: xw.workbook.Worksheet) -> None:
    raise NotImplementedError


def gen_styler_comma(cols: list[str]) -> Styler:
    raise NotImplementedError


def gen_styler_percent(cols: list[str]) -> Styler:
    raise NotImplementedError


default_stylers: list[Styler] = [
    set_date_col_width,
    set_header,
    set_grid,
]


def apply(x: Dict_DF, wb: xw.Workbook, styler: Styler) -> None:
    for (df, ws) in zip(x.values(), wb.worksheets()):
        styler(df, ws)


def make_stylers(comma, percent) -> list[Styler]:
    stylers = default_stylers.copy()
    if comma is not None:
        stylers.append(gen_styler_comma(comma))
    if percent is not None:
        stylers.append(gen_styler_percent(percent))
    return stylers


def write(df: pd.DataFrame | Dict_DF |
          tuple[pd.DataFrame] | list[pd.DataFrame],
          path: str, /,
          comma: Optional[list[str]], percent: Optional[list[str]],
          overwrite: bool = False, open: bool = False) -> Path:
    filepath = Path(path).expanduser()
    if filepath.suffix != ".xlsx":
        raise NameError(f"The path must end with .xlsx ({path})")
    if filepath.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists")
    x = make_dict(df)

    stylers = make_stylers(comma, percent)

    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:  # type: ignore
        for (nm, v) in x.items():
            v.to_excel(writer, nm)
        # when specifying `engine="xlsxwriter"`, the typehints will report false error
        # I think it's a bug of pandas, as it doesn't specify "xlsxwriter" as the
        # legal literal so we ignore the type error here
        book: xw.Workbook = writer.book  # type: ignore
        for style in stylers:
            apply(x, book, style)

    if open:
        subprocess.run(["open", str(filepath)])
    return filepath
