"""真实行情采集 CLI。

用法（在 collector 目录下，需联网）：
    python fetch.py a 600519,000001,300750 [2023-01-01] [2026-09-09]
    python fetch.py us AAPL,MSFT,NVDA [2023-01-01] [2026-09-09]

把行情 upsert 进 MySQL（幂等，可重复跑补数据）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_conn, upsert_quotes, upsert_stock  # noqa: E402
from fetch_a import fetch_a_stock, get_a_name  # noqa: E402
from fetch_us import fetch_us_stock, get_us_name  # noqa: E402
from normalize import infer_a_exchange, parse_date  # noqa: E402


def _parse_args():
    ap = argparse.ArgumentParser(description="拉取日线行情入库")
    ap.add_argument("market", choices=["a", "us"], help="a=A股, us=美股")
    ap.add_argument("codes", help="逗号分隔的代码/ticker，如 600519,AAPL")
    ap.add_argument("start", nargs="?", default=None, help="起始日期 YYYY-MM-DD，默认 2023-01-01")
    ap.add_argument("end", nargs="?", default=None, help="结束日期 YYYY-MM-DD，默认今天")
    ap.add_argument("--clear", action="store_true",
                    help="入库前清空这些代码已有的行情（换真实数据时用，避免混入合成/旧数据）")
    return ap.parse_args()


def _today() -> str:
    return dt.date.today().isoformat()


def main() -> int:
    args = _parse_args()
    market = "A" if args.market == "a" else "US"
    codes = [c.strip().upper() if args.market == "us" else c.strip() for c in args.codes.split(",") if c.strip()]

    # akshare 的 start 需 YYYYMMDD，yfinance 需 YYYY-MM-DD
    start = args.start
    end = args.end or _today()
    if args.market == "a":
        start = (start or "2023-01-01").replace("-", "")
        end = end.replace("-", "")
    else:
        start = start or "2023-01-01"
    end_d = parse_date(end) or dt.date.today()

    conn = get_conn()
    total = 0
    for code in codes:
        if args.clear:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM daily_quote WHERE market=%s AND code=%s",
                    (market, code),
                )
            print(f"[{market}] 已清空 {code} 的历史行情")
        if args.market == "a":
            bars = fetch_a_stock(code, start=start, end=end)
            name = get_a_name(code) or code
            exchange = infer_a_exchange(code)
        else:
            bars = fetch_us_stock(code, start=start, end=end)
            name = get_us_name(code) or code
            exchange = None  # yfinance 不区分交易所，前端不依赖
        upsert_stock(conn, market, code, name, exchange)
        n = upsert_quotes(conn, market, code, bars)
        total += n
        dates = f"{bars[0]['date']}~{bars[-1]['date']}" if bars else "无数据"
        print(f"[{market}] {code:10s} {name:20s} 行数={n:5d}  区间={dates}")
    conn.close()
    print(f"完成，共 upsert {total} 行行情（最新交易日 {end_d}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
