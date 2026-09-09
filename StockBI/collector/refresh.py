"""真实日线增量刷新：每天收盘后跑一次，把最新一个交易日补进 MySQL。

默认增量：以库里已有的最大交易日为起点往前多取 ~7 天(容错覆盖)，拉取到今天。
首次使用（库里没有/或刚清掉合成数据）会全量回填到 BACKFILL_START。

用法（collector 目录）：
    python refresh.py                 # A股 + 美股 全量按清单刷新
    python refresh.py --market a      # 只刷 A股
    python refresh.py --full          # 忽略存量，全量重拉（换真实数据前先清空用）
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
from watchlist import BACKFILL_START, WATCH  # noqa: E402


def _last_date(conn, market: str, code: str) -> dt.date | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT MAX(trade_date) AS d FROM daily_quote WHERE market=%s AND code=%s",
            (market, code),
        )
        row = cur.fetchone()
    return row["d"] if row and row["d"] else None


def _run(market: str, code: str, conn, full: bool) -> int:
    if market == "A":
        # akshare 的 start 需要 YYYYMMDD
        start = BACKFILL_START.replace("-", "") if full else None
        last = None if full else _last_date(conn, market, code)
        if start is None and last:
            start = (last - dt.timedelta(days=7)).strftime("%Y%m%d")  # 往前多取，覆盖漏算
        start = start or BACKFILL_START.replace("-", "")
        end = dt.date.today().strftime("%Y%m%d")
        bars = fetch_a_stock(code, start=start, end=end)
        name = get_a_name(code) or code
        upsert_stock(conn, market, code, name, infer_a_exchange(code))
    else:
        start = BACKFILL_START if full else None
        last = None if full else _last_date(conn, market, code)
        if start is None and last:
            start = (last - dt.timedelta(days=7)).isoformat()
        start = start or BACKFILL_START
        bars = fetch_us_stock(code, start=start, end=dt.date.today().isoformat())
        name = get_us_name(code) or code
        upsert_stock(conn, market, code, name, None)

    n = upsert_quotes(conn, market, code, bars)
    span = f"{bars[0]['date']}~{bars[-1]['date']}" if bars else "无新增"
    print(f"[{market}] {code:8s} {name:14s} 写入={n:4d}  {span}")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="真实日线增量刷新")
    ap.add_argument("--market", choices=["a", "us"], default=None, help="只刷指定市场，缺省全刷")
    ap.add_argument("--full", action="store_true", help="忽略存量全量重拉(用于首次回填)")
    args = ap.parse_args()

    conn = get_conn()
    total = 0
    for market, codes in WATCH.items():
        if args.market and args.market.upper() != market:
            continue
        for code in codes:
            total += _run(market, code, conn, args.full)
    conn.close()
    print(f"\n刷新完成，共写入 {total} 根日线")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
