import pandas as pd
import pathlib
from datetime import date, datetime
from dataclasses import dataclass
import re
import argparse
from typing import Optional
import logging


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
    match = re.findall(r"\d{4}-\d{2}-\d{2}", x)
    if match:
        return datetime.strptime(match[0], "%Y-%m-%d").date()
    else:
        return None


def read_nav(excel: pathlib.Path, date_rgs: tuple[int, int],
             nav_nms: tuple[str, str], sheet: str | int = 0) -> Nav:
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
    indexes = list(content.iloc[:, 0])
    values = list(content.iloc[:, 1])
    navs = find_nav(indexes, values, nav_nms)
    return Nav(ref_date, navs[0], navs[1])


def to_path(x: str) -> pathlib.Path:
    out = pathlib.Path(x).expanduser()
    if not out.exists():
        raise FileNotFoundError(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'excel', type=str, help="The excel to be read from")
    parser.add_argument(
        'date_rgs', type=str,
        help="the possible date positions, must be ")
    parser.add_argument(
        'nav_nms', type=str,
        help="the nav field names, require 2 names, must be a valid python expression")
    parser.add_argument(
        '-s', "--sheet", type=int, help="The sheet name of the nav table", default=0)
    parser.add_argument(
        '-d', "--debug", help="display the debug message",
        action="store_true", default=False)
    opt = parser.parse_args()
    if opt.debug:
        logging.basicConfig(level=logging.DEBUG)
    print(read_nav(
        to_path(opt.excel), eval(opt.date_rgs), eval(opt.nav_nms), opt.sheet
    ))


if __name__ == "__main__":
    main()
