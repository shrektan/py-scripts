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
1. Set proper column width for date, datetime, long numbers, etc.

## TODO
- We should not use `DataFrame.to_xlsx()`. It makes everything complicated.
  We should just write the cell by ourselves.
- Be able to add Index
- Auto fit the column and support Chinese strings, the wb.autofit() doesn't
  work well. For date there's no padding. For CN strings, it's not correct.
- Plan to submit to `pip` when matured

## Dependencies:
- `xlsxwriter`: https://xlsxwriter.readthedocs.io
"""
import xlsxwriter as xw
from xlsxwriter.workbook import Worksheet
import pandas as pd
from pathlib import Path
import subprocess
from typing import Callable, Optional, Any

Dict_DF = dict[str, pd.DataFrame]
Dict_Format = Optional[dict[str, Any]]
Wb_Format = xw.workbook.Format
Styler = Callable[[pd.DataFrame, Worksheet, Wb_Format], None]


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


style_fmts: dict[str, Dict_Format] = {
    "header": {
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#538DD5',
        'color': "white",
        'bottom': 1,
    },
    "cell": {
        'bottom': 1,
    }
}


def write_df(df: pd.DataFrame, sheet: Worksheet,
             head_fmt: Optional[Wb_Format], cell_fmt: Optional[Wb_Format]) -> None:
    # TODO: add index support
    # column width to 12, so date can display;
    # this can be set in wb creator via default_col_width
    sheet.set_column(0, len(df.columns) - 1, width=12, cell_format=cell_fmt)
    # header
    for j, value in enumerate(df.columns.values):
        sheet.write(0, j, value, head_fmt)
    # content
    for (j, col) in enumerate(df.columns):
        # xlsxwriter doesn't support writting NA directly
        sheet.write_column(1, j, df[col].fillna(""))
    # sheet.autofit()


def write(df: pd.DataFrame | Dict_DF |
          tuple[pd.DataFrame] | list[pd.DataFrame],
          path: str | Path, /,
          #   comma: Optional[list[str]] = None, percent: Optional[list[str]] = None,
          overwrite: bool = False, open: bool = False) -> Path:
    if isinstance(path, str):
        filepath = Path(path).expanduser()
    else:
        filepath = path
    if filepath.suffix != ".xlsx":
        raise NameError(f"The path must end with .xlsx ({path})")
    if filepath.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists")
    x = make_dict(df)

    with xw.Workbook(filepath, {'default_date_format': 'yyyy-mm-dd'}) as wb:
        head_fmt = wb.add_format(style_fmts["header"])
        # TODO: when applied cell_fmt, the default date_format will be replaced
        # we need to find a way to know the cell type is date and set the format
        # cell_fmt = wb.add_format(style_fmts["cell"])
        for (nm, df) in x.items():
            ws = wb.add_worksheet(nm)
            write_df(df, ws, head_fmt, None)

    if open:
        subprocess.run(["open", str(filepath)])
    return filepath
