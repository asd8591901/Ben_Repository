"""灌入确定性演示行情（无需联网）。

几何随机游走生成 ~14 个月日线，用代码做随机种子 → 每次运行结果一致、可重复。
真数据结构：akshare(A股前复权) / yfinance(美股)。此演示数据仅用于离线看效果，
想要真实行情请运行 fetch.py。
"""
from __future__ import annotations

import datetime as dt
import math
import os
import random
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd  # noqa: E402

from db import get_conn, upsert_quotes, upsert_stock  # noqa: E402
from normalize import infer_a_exchange  # noqa: E402

# (market, code, name, start_price, daily_vol, base_volume)
DEMO_STOCKS = [
    # A股：起点价(元) 日波动 基准成交量(股)
    ("A", "600519", "贵州茅台", "SH", 1650.0, 0.018, 3_000_000),
    ("A", "000001", "平安银行", "SZ", 10.50, 0.014, 60_000_000),
    ("A", "300750", "宁德时代", "SZ", 165.0, 0.025, 15_000_000),
    ("A", "601318", "中国平安", "SH", 42.0, 0.016, 30_000_000),
    ("A", "000858", "五粮液", "SZ", 135.0, 0.020, 8_000_000),
    # 美股：起点价(USD) 日波动 基准成交量
    ("US", "AAPL", "Apple", "NASDAQ", 170.0, 0.020, 55_000_000),
    ("US", "MSFT", "Microsoft", "NASDAQ", 330.0, 0.018, 25_000_000),
    ("US", "NVDA", "NVIDIA", "NASDAQ", 46.0, 0.032, 60_000_000),
    ("US", "TSLA", "Tesla", "NASDAQ", 240.0, 0.035, 80_000_000),
    ("US", "GOOGL", "Alphabet", "NASDAQ", 135.0, 0.021, 25_000_000),
]

N_DAYS = 300  # ≈14 个月交易日


def _rng_for(code: str) -> random.Random:
    return random.Random(zlib.crc32(code.encode("utf-8")))  # 跨运行稳定


def gen_bars(code: str, start_price: float, vol: float, base_volume: int) -> list[dict]:
    rng = _rng_for(code)
    end = dt.date.today()
    start = end - dt.timedelta(days=int(N_DAYS * 1.6))
    days = list(pd.bdate_range(start=start, end=end))[-N_DAYS:]
    if not days:
        return []

    # 温和趋势 + 波动，log 收益随机游走
    drift = rng.uniform(-0.0002, 0.0004)
    close = start_price
    bars = []
    for ts in days:
        ret = rng.gauss(drift, vol)
        prev_close = close
        close = max(0.1, close * math.exp(ret))
        gap = rng.gauss(0, vol * 0.35)
        open_ = max(0.1, prev_close * math.exp(gap))
        hi = max(open_, close) * (1 + abs(rng.gauss(0, vol * 0.5)))
        lo = min(open_, close) * (1 - abs(rng.gauss(0, vol * 0.5)))
        hi, lo = max(hi, open_, close), min(lo, open_, close)
        shares = int(base_volume * (1 + 0.8 * abs(ret) / (vol or 1)) * rng.uniform(0.5, 1.5))

        def r2(x: float) -> float:
            return round(x, 2)

        bars.append({
            "date": ts.date(),
            "open": r2(open_), "high": r2(hi), "low": r2(lo), "close": r2(close),
            "volume": shares,
            "amount": round(shares * close, 2),  # 近似成交额，仅演示用
        })
    return bars


def main() -> None:
    conn = get_conn()
    for market, code, name, exchange, start_price, vol, base_volume in DEMO_STOCKS:
        bars = gen_bars(code, start_price, vol, base_volume)
        upsert_stock(conn, market, code, name, exchange)
        n = upsert_quotes(conn, market, code, bars)
        span = f"{bars[0]['date']}~{bars[-1]['date']}" if bars else "空"
        print(f"[{market}] {code:8s} {name:12s} 行数={n:4d}  {span}")

    conn.close()
    print("\n演示数据已入库。真实行情请用：python fetch.py a|us <codes> [start] [end]")


if __name__ == "__main__":
    main()
