"""## Read Nav from Excels (估值表)
读取国内常见估值表的*估值日期、单位净值和累计单位净值*三则信息。
需要将估值表Excel放置在一个文件夹中，程序会遍历文件夹中所有的Excel表。
要求Excel表的格式大体一致。

### 解析原理

- `净值日期`：读取特定列的前n行，会自动根据`%Y-%m-%d`或%Y年%m月%d日信息去解析，
返回第一个成功解析的日期。
- `单位净值`和`累计单位净值`，根据第一列的字符信息，找到第二列的净值。

结果会输出到Excel表中。

### 代码示例

```bash
python read_nav_from_excel.py ~/Downloads/excels ~/Downloads/nav-data.xlsx --overwrite
```

"""
import pandas as pd
import pathlib
from datetime import date, datetime
from dataclasses import dataclass, astuple
import re
import argparse
from typing import Optional
import logging
import subprocess


@dataclass
class Nav:
    ref_date: date
    nav: float
    nav_acc: float


def find_nav(indexes: list[str], values: list[str],
             nms: tuple[str, str]) -> tuple[float, float]:
    nav = None
    nav_acc = None
    for (index, value) in zip(indexes, values):
        if re.search(nms[0], index) is not None:
            nav = float(value)
        if re.search(nms[1], index) is not None:
            nav_acc = float(value)
        if nav is not None and nav_acc is not None:
            return (nav, nav_acc)
    nms_cand = list(filter(lambda x: re.search("净值", x) is not None, indexes))
    raise LookupError(
        f"Can't find {nms} in the first column, possible names {nms_cand}")


def parse_date(x: str) -> Optional[date]:
    match = re.search(r"(\d{4})[-年](\d{2})[-月](\d{2})日?", x)
    if match:
        datestr = "-".join(match.groups())
        return datetime.strptime(datestr, "%Y-%m-%d").date()
    else:
        return None


def read_nav(excel: pathlib.Path, date_rgs: tuple[int, int],
             nav_nms: tuple[str, str], sheet: str | int = 0) -> Nav:
    """Read Nav data from Excel (估值表)

    Args:
        excel (pathlib.Path): Must be an existing excel
        date_rgs (tuple[int, int]): The range to search for ref_date of navs.
        Program will search such `0:date_rgs[0], date_rgs[1]` area and return
        the first valid date. It tries to find the date by searching the pattern
        of `%Y-%m-%d`.
        nav_nms (tuple[str, str]): The row names that marked the nav and accumulative
        nav.
        sheet (str | int, optional): The sheet to search for. Defaults to 0.

    Raises:
        LookupError: It raise exception with searched area or potential row names, when
        any of the values can't be found.

    Returns:
        Nav: contains the reference date, the unit nav, and the accumulative nav
    """
    logging.debug(f"Parsing `{excel}...`")
    content: pd.DataFrame = pd.read_excel(excel, sheet_name=sheet)
    ref_date = None
    for date_rg in range(date_rgs[0]):
        cell = str(content.iloc[date_rg])
        logging.debug(f"the date range content is: {cell}")
        ref_date = parse_date(cell)
        if ref_date is not None:
            break
    if ref_date is None:
        raise LookupError(f"Fail to find ref_date in {date_rgs} cells")
    indexes = list(content.iloc[:, 0].astype(str))
    values = list(content.iloc[:, 1].astype(str))
    navs = find_nav(indexes, values, nav_nms)
    return Nav(ref_date, navs[0], navs[1])


def to_path(x: str) -> pathlib.Path:
    out = pathlib.Path(x).expanduser()
    if not out.exists():
        raise FileNotFoundError(out)
    return out


def find_all_excels(x: str) -> list[pathlib.Path]:
    dir = pathlib.Path(x).expanduser()
    if not dir.exists() or not dir.is_dir():
        raise FileNotFoundError(f"{x} is not a valid directory")
    out = []
    for f in dir.iterdir():
        if f.is_file() and f.suffix in [".xlsx", ".xls"]:
            out.append(f)
    out.sort()
    return out


def read_navs(excels: list[pathlib.Path], date_rgs: tuple[int, int],
              nav_nms: tuple[str, str], sheet: str | int = 0) -> pd.DataFrame:
    out = []
    for (i, excel) in enumerate(excels):
        logging.info(f"Parsing {i+1} of {len(excels)}, {excel.name}...")
        nav = read_nav(excel, date_rgs=date_rgs, nav_nms=nav_nms, sheet=sheet)
        logging.debug(f"nav is {nav}")
        out.append(astuple(nav))
    cols = ["净值日期", "单位净值", "累计单位净值"]
    df = pd.DataFrame(out, columns=cols)
    df = df.sort_values("净值日期")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'fromdir', type=str, help="the directory that stores the nav excels (估值表)")
    parser.add_argument(
        'toexcel', type=str, help="the excel file that stores the parsed result")
    parser.add_argument(
        '-date_rgs', type=str, default="(10,0)",
        help="the possible date positions, must be in the form of (int, int), "
        "which means the program tries to find the reference date "
        "among the range `0:date_rgs[0], date_rgs[1]` cells")
    parser.add_argument(
        '-nav_nms', type=str, default="('(今日|基金)单位净值', '累计单位净值')",
        help="the nav field names, require 2 names, must be in the format of (str, str), "
        "which represents the unit nav and accumulative nav row names, respectively")
    parser.add_argument(
        '-s', "--sheet", type=int, help="the sheet name of the nav table", default=0)
    parser.add_argument(
        '-n', type=int,
        help="only parse the first n Excels (default 0, means all)", default=0)
    parser.add_argument(
        "--overwrite", help="overwrite the `toexcel` if exists",
        action="store_true", default=False)
    parser.add_argument(
        "-o", help="open the output excel file when job is over",
        action="store_true", default=False)
    parser.add_argument(
        '-v', "--verbose", help="display the info message",
        action="store_true", default=False)
    parser.add_argument(
        '-d', "--debug", help="display the debug message",
        action="store_true", default=False)

    opt = parser.parse_args()
    toexcel = pathlib.Path(opt.toexcel).expanduser()
    if toexcel.exists() and opt.overwrite is False:
        raise FileExistsError(f"{toexcel} already exists")

    if opt.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif opt.verbose:
        logging.basicConfig(level=logging.INFO)

    excels = find_all_excels(opt.fromdir)
    if opt.n > 0:
        excels = excels[:opt.n]
    logging.debug(f"find excels: {list(map(lambda x: x.name, excels))}")

    out = read_navs(excels, date_rgs=eval(opt.date_rgs),
                    nav_nms=eval(opt.nav_nms), sheet=opt.sheet)
    out.to_excel(opt.toexcel)

    if opt.o:
        subprocess.run(["open", str(opt.toexcel)])


if __name__ == "__main__":
    main()
