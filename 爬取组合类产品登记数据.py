"""爬取组合类产品登记数据
主要目的是为了爬取组合类产品的注册登记信息
具体表单的获取方式，是从网页源代码找到的
total_page和excel_path分别表示爬取的页面范围和生成的excel地址
"""
import requests
import bs4
import pandas


def read_tbl(page: int):
    """Read the table content from ZhongBaoDeng website

    Args:
        page (int): which page of the table should be downloaded

    Returns:
        list: each element contains a 5-length row data
    """
    url = "https://www.zhongbaodeng.com/channel/"\
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
    rsp = requests.post(url=url, params=params, timeout=10)
    soup = bs4.BeautifulSoup(rsp.text, "lxml")
    tbl = soup.find('div', attrs={
        "class": "product_content_content product_content_content1"
    })
    tbl = tbl.find_all("li")
    out = []
    for ele in tbl:
        ele = ele.find_all("div")
        out.append([
            ele[0].text.strip(),
            ele[1].text.strip(),
            ele[2].text.strip(),
            ele[3].text.strip(),
            ele[4].text.strip()
        ])
    return out


out = []
msg = "The total pages to be downloaded (check the website by yourself):\n"
total_page = int(input(msg))
print(f"total page is set to {total_page}")
if total_page < 1:
    raise ValueError(f"The {total_page=} must be positive integer!")
for i in range(1, total_page):
    print(f"fetching page {i}")
    out.append(read_tbl(i))
cols = ["序号", "产品管理人", "产品登记编码", "产品全称", "登记时间"]
tbl = map(lambda x: pandas.DataFrame(x, columns=cols), out)
tbl = list(tbl)
tbl = pandas.concat(tbl, ignore_index=True)

excel_path = "~/Downloads/组合类产品登记信息.xlsx"
print(f"writing to excel: {excel_path}")
tbl.to_excel(excel_path, index=False)

print("done")
