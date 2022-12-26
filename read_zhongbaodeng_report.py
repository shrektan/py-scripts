"""读取中保登组合类产品月度报告数据
读取Excel里的组合产品数据并生成为Excel
"""

import pathlib
from PyPDF2 import PdfFileReader
import pandas as pd
pd.set_option('display.unicode.ambiguous_as_wide',True)
pd.set_option('display.unicode.east_asian_width',True)


def rate2num(x :pd.Series) -> list | pd.Series:
    if x is not pd.Series[str]:
        return x
    out :list = []
    for elem in x:
        if elem == "-":
            out.append(pd.NA)
        elif elem.find("%") > -1:
            out.append(pd.to_numeric(elem.replace("%", "")) / 100.0)
        else:
            out.append(pd.to_numeric(elem))
    return out


def find_prod_type(x: str) -> str:
    opts = ["固定收益类", "混合类", "权益类", "货币类"]
    for opt in opts:
        if x.count(opt) > 0:
            return opt
    return "N/A"


def read_tbl(pdf_path: pathlib.Path) -> pd.DataFrame:
    out: list[pd.DataFrame] = []
    p: PdfFileReader = PdfFileReader(pdf_path)
    garbage: str = '½ö¹©°²Áª×Ê²ú²Î¿¼'
    for i in range(p.getNumPages()):
        text: list[str] = p.getPage(i).extract_text().replace(garbage, "")\
            .strip().split("\n")
        tbl_text: filter[str] = filter(lambda x: x.count(" ") == 6, text)
        meta_text: filter[str] = filter(lambda x: x.count(" ") != 6, text)
        cols: list[str] = [
            "产品全称", "产品成立时间", "期末累计单位净值(元/份)",
            "当月累计单位净值增长率", "年初以来累计单位净值增长率", "期末净资产(亿元)", "产品管理机构"
        ]
        df: pd.DataFrame = pd.DataFrame(
            map(lambda x: x.split(" "), tbl_text), columns=cols
        )
        df["产品类型"] = find_prod_type("".join(meta_text))
        out.append(df)
    out2: pd.DataFrame = pd.concat(out, ignore_index=True)
    out2["产品成立时间"] = pd.to_datetime(out2["产品成立时间"], format="%Y%m%d")
    out2["期末累计单位净值(元/份)"] = pd.to_numeric(out2["期末累计单位净值(元/份)"])
    out2["期末净资产(亿元)"] = pd.to_numeric(out2["期末净资产(亿元)"])
    out2["当月累计单位净值增长率"] = rate2num(out2["当月累计单位净值增长率"])
    out2["年初以来累计单位净值增长率"] = rate2num(out2["年初以来累计单位净值增长率"])
    return out2


def main() -> None:
    pdf_path: str = "/Users/shrektan/Library/CloudStorage/OneDrive-共享的库-onedrive/"\
        "安联资管文档/监管和协会资料/组合类产品信息/保险资产管理产品行业报告（2022年10月）-组合行情-开放式组合类资管产品清单.pdf"
    out_path:str = "~/Downloads/中保登数据-2022年10月.xlsx"
    path: pathlib.Path = pathlib.Path(pdf_path)
    if not path.exists():
        raise FileExistsError
    read_tbl(path).to_excel(out_path)


if __name__ == "__main__":
    main()
