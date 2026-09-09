"""A股日线采集（akshare）。依赖较重，import 放在函数内，便于无网络/未安装时其它脚本仍可用。"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 兼容从任意目录 python xxx.py

from normalize import infer_a_exchange, normalize_akshare

DEFAULT_START = "20230101"


def fetch_a_stock(code: str, start: str | None = None, end: str | None = None) -> list[dict]:
    """拉取单只 A股前复权日线，返回标准 bars。

    akshare 函数与列名随版本演进，只取开盘/最高/最低/收盘/成交量/成交额核心字段。
    """
    import akshare as ak  # 延迟导入

    start = start or DEFAULT_START
    end = end or dt.date.today().strftime("%Y%m%d")
    df = ak.stock_zh_a_hist(
        symbol=code,
        period="daily",
        start_date=start,
        end_date=end,
        adjust="qfq",  # 前复权，历史价与现价可比
    )
    if df is None or df.empty:
        return []
    return normalize_akshare(df, code)


def get_a_name(code: str) -> str | None:
    """尽力获取股票名称（akshare 个股信息接口），失败返回 None，由调用方回退为代码。"""
    try:
        import akshare as ak

        info = ak.stock_individual_info_em(symbol=code)
        row = info[info["item"] == "股票简称"]
        if not row.empty:
            return str(row.iloc[0]["value"])
    except Exception:
        pass
    return None
