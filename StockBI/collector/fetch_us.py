"""美股日线采集（yfinance）。"""
from __future__ import annotations

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 兼容从任意目录 python xxx.py

from normalize import normalize_yfinance

DEFAULT_START = "2023-01-01"


def fetch_us_stock(ticker: str, start: str | None = None, end: str | None = None) -> list[dict]:
    """拉取单只美股日线（原始未复权价），返回标准 bars。"""
    import yfinance as yf  # 延迟导入

    start = start or DEFAULT_START
    end = end or dt.date.today().isoformat()
    df = yf.download(
        tickers=ticker,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
    )
    return normalize_yfinance(df, ticker)


def get_us_name(ticker: str) -> str | None:
    """尽力获取公司名，失败返回 None（展示名由调用方回退为 ticker）。"""
    try:
        import yfinance as yf

        info = yf.Ticker(ticker).info or {}
        name = info.get("shortName") or info.get("longName")
        return str(name) if name else None
    except Exception:
        return None
