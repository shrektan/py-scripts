import read_zhongbaodeng_report as rp


def test_rm_space():
    input = r'平安资产如意 18号资产管理产品 20150508 1.0903 -0.73% -2.92% 31.94 平安资产管理有限责任公司'
    out = r'平安资产如意18号资产管理产品 20150508 1.0903 -0.73% -2.92% 31.94 平安资产管理有限责任公司'
    assert rp.rm_space(input) == out
    input = r'大家资产- 稳健精选 6号(第五期)集合资产管理产品 20170421 2.83% 137.00 大家资产管理有限责任公司'
    out = r'大家资产-稳健精选6号(第五期)集合资产管理产品 20170421 2.83% 137.00 大家资产管理有限责任公司'
    assert rp.rm_space(input) == out
