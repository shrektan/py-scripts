"""The example code to fetch RSC plumber API
"""
import requests
import json
import pandas as pd
import os


def rsc_key() -> str:
    """the way of setting up the env var: `export RSC_KEY=xxxx`"""
    key = os.environ.get("RSC_KEY")
    if key is None:
        raise RuntimeError("You should define environment variable RSC_KEY")
    return key


def read_db(con: str, sql: str) -> pd.DataFrame:
    key: str = rsc_key()
    url: str = "http://icube.allianziamc.com.cn/sql-api/db_read"
    headers: dict[str, str] = {
        "accept": "application/json",
        "Authorization": f"Key {key}",
    }
    data: dict[str, str] = {
        "con": con,
        "sql": sql
    }
    ret: requests.Response = requests.post(
        url=url, data=data, headers=headers, timeout=10)
    if ret.status_code == 200:
        out = pd.DataFrame(json.loads(ret.text))
        return out
    else:
        raise RuntimeError(f"the status code is {ret.status_code}")


if __name__ == "__main__":
    # run a test
    sql = "select * from pq.idb_param_hs_fund where rownum <= 10"
    df = read_db("pqread", sql)
    print(df)
