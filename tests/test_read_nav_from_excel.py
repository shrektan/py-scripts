import read_nav_from_excel as rd
from datetime import date
import pytest
import re


def test_parse_date():
    out = rd.parse_date("2021-12-31")
    assert out == date(2021, 12, 31)


def test_find_nav():
    # regrex match and conver to float
    indexes = ["ABC", "今日单位净值：", "累计单位净值：", "ZZZ"]
    values = ["345", "1.3", "2.1", "YYY"]
    nms = ("(今日|基金)单位净值", "累计单位净值")
    out = rd.find_nav(indexes, values, nms)
    assert out == (1.3, 2.1)

    # report correct error msg
    indexes2 = ["ABC", "当天单位净值：", "累计单位净值：", "ZZZ"]
    with pytest.raises(
        LookupError, match=re.escape(r"['当天单位净值：', '累计单位净值：']")
    ):
        rd.find_nav(indexes2, values, nms)
