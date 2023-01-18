"""读取中保登组合类产品月度报告数据
读取Excel里的组合产品数据并生成为Excel
"""

import pathlib
from PyPDF2 import PdfFileReader
import pandas as pd
import logging
import re
import argparse
from typing import Optional
import writexlsx


def rate2num(x: pd.Series) -> list | pd.Series:
    if not pd.api.types.is_string_dtype(x):
        return x
    out: list = []
    for elem in x:
        if pd.isna(elem) or elem == "-":
            out.append(pd.NA)
        elif elem.find("%") > -1:
            out.append(pd.to_numeric(elem.replace("%", "")) / 100.0)
        else:
            out.append(pd.to_numeric(elem))
    return out


def find_prod_type(x: list[str]) -> str:
    txt = "".join(filter(lambda x: (n := x.count(" "), n != 6 and n != 4), x))
    opts = ["固定收益类", "混合类", "权益类", "货币类"]
    for opt in opts:
        if opt in txt:
            return opt
    return "N/A"


def conv_normal(x: list[str]) -> pd.DataFrame:
    txt = filter(lambda x: x.count(" ") == 6 and x.find("产品全称") == -1, x)
    cols = [
        "产品全称", "产品成立时间", "期末累计单位净值(元/份)",
        "当月累计单位净值增长率", "年初以来累计单位净值增长率", "期末净资产(亿元)", "产品管理机构"
    ]
    return pd.DataFrame(map(lambda x: x.split(" "), txt), columns=cols)


def conv_mmp(x: list[str]) -> pd.DataFrame:
    txt = filter(lambda x: x.count(" ") == 4 and x.find("产品全称") == -1, x)
    cols = ["产品全称", "产品成立时间", "年初以来累计单位净值增长率", "期末净资产(亿元)", "产品管理机构"]
    out = pd.DataFrame(map(lambda x: x.split(" "), txt), columns=cols)
    out["期末累计单位净值(元/份)"] = pd.NA
    out["当月累计单位净值增长率"] = pd.NA
    return out


def rm_space(x: str) -> str:
    """remove unexpected space from table strings

    Args:
        x (str): the row string read from pdf

    Returns:
        str: the cleaned row string
    """
    pattern = r"(.+)(?=\s\d{8})"
    match = re.match(pattern, x)
    if match is None:
        return x
    prod_name = match.group(0).replace(" ", "")
    return re.sub(pattern, prod_name, x)


def rm_garbage(x: str) -> list[str]:
    """remove garbage letters

    Args:
        x (str): _description_

    Returns:
        list[str]: _description_
    """
    garbage = ['½ö¹©°²Áª×Ê²ú²Î¿¼', 'NÅO\x9b[\x89\x80T\x8dDN§O\x7fu(']
    for elem in garbage:
        x = x.replace(elem, "")
    return x.strip().split("\n")


def read_tbl(pdf_path: pathlib.Path, pages: Optional[list[int]] = None) -> pd.DataFrame:
    out: list[pd.DataFrame] = []
    p: PdfFileReader = PdfFileReader(pdf_path)
    for i in range(p.getNumPages()):
        if pages is not None:
            if i + 1 not in pages:
                continue
        logging.info(f"handling page {i + 1}/{p.getNumPages()}")
        txt = list(map(rm_space, rm_garbage(p.getPage(i).extract_text())))
        normal_df = conv_normal(txt)
        mmp_df = conv_mmp(txt)
        df = pd.concat([normal_df, mmp_df])
        df["产品类型"] = find_prod_type(txt)
        out.append(df)
        logging.debug(
            f"page {i} has {len(df)} rows with {find_prod_type(txt)} type")
    if len(out) == 0:
        raise RuntimeError("no table content found")
    out2: pd.DataFrame = pd.concat(out, ignore_index=True)
    out2["产品成立时间"] = pd.to_datetime(out2["产品成立时间"], format="%Y%m%d")
    out2["期末累计单位净值(元/份)"] = pd.to_numeric(out2["期末累计单位净值(元/份)"])
    out2["期末净资产(亿元)"] = pd.to_numeric(out2["期末净资产(亿元)"])
    out2["当月累计单位净值增长率"] = rate2num(out2["当月累计单位净值增长率"])
    out2["年初以来累计单位净值增长率"] = rate2num(out2["年初以来累计单位净值增长率"])
    return out2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=str, help="中保登月度组合行情-开放式组合类资管产品清单的文档路径")
    parser.add_argument("excel", type=str, help="生成的Excel路径")
    parser.add_argument(
        '-p', "--pages", type=str,
        help="the page range to be parsed, starting from 1",
        default=None)
    parser.add_argument(
        '-v', "--verbose", help="display the info message",
        action="store_true", default=False)
    parser.add_argument(
        '-d', "--debug", help="display the debug message",
        action="store_true", default=False)
    parser.add_argument(
        "--overwrite", help="overwrite the excel if it exists",
        action="store_true", default=False)
    parser.add_argument(
        "-o", "--open", help="open the output excel file when job is over",
        action="store_true", default=False)

    opt = parser.parse_args()

    if opt.pages is None:
        pages = None
    else:
        pages_raw = eval(opt.pages)
        if isinstance(pages_raw, range):
            pages = list(pages_raw)
        elif isinstance(pages_raw, int):
            pages = [pages_raw]
        else:
            raise TypeError(
                f"{opt.pages} are not valid input, must be eval to int or range")

    if opt.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif opt.verbose:
        logging.basicConfig(level=logging.INFO)

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pdf_path = pathlib.Path(opt.pdf).expanduser()
    out_path = pathlib.Path(opt.excel).expanduser()
    if not pdf_path.exists():
        raise FileNotFoundError(f"{opt.pdf}")
    if not opt.overwrite and out_path.exists():
        raise FileExistsError(f"{opt.excel}")
    df = read_tbl(pdf_path, pages)
    writexlsx.write(df, out_path, overwrite=opt.overwrite, open=opt.open)


if __name__ == "__main__":
    main()
