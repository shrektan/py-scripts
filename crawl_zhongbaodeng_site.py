"""爬取组合类产品登记数据
主要目的是为了爬取组合类产品的注册登记信息
具体表单的获取方式，是从网页源代码找到的
total_page和excel_path分别表示爬取的页面范围和生成的excel地址

# TODO
- add verbose argument and use logging to display the message
"""
import requests
import bs4
import pandas as pd
import writexlsx
import argparse
import subprocess


def read_tbl(page: int) -> pd.DataFrame | None:
    """Read the table content from ZhongBaoDeng website

    Args:
        page (int): which page of the table should be downloaded

    Returns:
        list: each element contains a 5-length row data
    """
    url: str = "https://www.zhongbaodeng.com/channel/"\
        "350b43d4af88460b93ccd46658cf631e.html"
    params = {
        "isChannel": "",
        "isSelect": "",
        "type": "",
        "typeId": "",
        "keyValue": "",
        "currentPage": page,
        "keyword": "",
    }
    rsp: requests.Response = requests.post(url=url, params=params, timeout=10)
    soup = bs4.BeautifulSoup(rsp.text, "lxml")
    tbl = soup.find('div', attrs={
        "class": "product_content_content product_content_content1"
    })
    if isinstance(tbl, bs4.element.Tag):
        lis = tbl.find_all("li")
    else:
        return None
    out = []
    for ele in lis:
        ele = ele.find_all("div")
        out.append([
            ele[0].text.strip(),
            ele[1].text.strip(),
            ele[2].text.strip(),
            ele[3].text.strip(),
            ele[4].text.strip()
        ])
    cols: list[str] = ["序号", "产品管理人", "产品登记编码", "产品全称", "登记时间"]
    return pd.DataFrame(out, columns=cols)


def main() -> None:
    zbdurl = ("https://www.zhongbaodeng.com/channel/"
              "350b43d4af88460b93ccd46658cf631e.html")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--pages', type=int,
        help="the total pages to be downloaded (check the website by yourself), "
        "must be positive.")
    parser.add_argument(
        '-o', '--open', action='store_true', default=False,
        help="open the excel file when finished")
    parser.add_argument(
        "--overwrite", help="overwrite the `toexcel` if exists",
        action="store_true", default=False)
    parser.add_argument(
        "--openzbd", action="store_true", default=False,
        help="open the 中保登组合类产品登记网页: "
        f"{zbdurl} "
    )
    parser.add_argument(
        'outfile', help="the excel file to store the result")
    opt = parser.parse_args()

    if opt.openzbd:
        subprocess.run(["open", zbdurl])
        return None

    outfile = opt.outfile
    total_page = opt.pages
    if total_page is None:
        raise ValueError("`pages` param is not provided")
    if total_page < 1:
        raise ValueError(
            f"`pages` parameter must be positive integer (now is {total_page})!")

    out: list[pd.DataFrame] = []
    for i in range(1, total_page):
        print(f"fetching page {i}")
        r = read_tbl(i)
        if r is not None:
            out.append(r)
    tbl: pd.DataFrame = pd.concat(out, ignore_index=True)
    writexlsx.write({"组合类产品": tbl}, outfile,
                    open=opt.open, overwrite=opt.overwrite)
    print(f"the result has been saved to excel: {outfile}")


if __name__ == "__main__":
    main()
