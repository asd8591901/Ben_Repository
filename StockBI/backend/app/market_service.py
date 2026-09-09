"""行情查询服务：从 MySQL 取出列表/单只 K 线，附带涨跌幅计算。"""
from __future__ import annotations

from typing import Any

from .indicators import moving_average, pct_change

VALID_MARKETS = {"A", "US"}

# K 线图带上的均线窗口
MA_WINDOWS = (5, 10, 20, 60)


def is_valid_market(market: str) -> bool:
    return market in VALID_MARKETS


def _latest_rows(conn, market: str) -> list[dict]:
    """每只股票最新一根 K 线 + 其前一交易日收盘，用于算现价/涨跌幅。"""
    stocks = _query_all(
        conn,
        "SELECT market, code, name, exchange FROM stock_info WHERE market=%s ORDER BY code",
        (market,),
    )
    rows = []
    for s in stocks:
        cur = _query_all(
            conn,
            "SELECT trade_date, close FROM daily_quote "
            "WHERE market=%s AND code=%s ORDER BY trade_date DESC LIMIT 2",
            (market, s["code"]),
        )
        if not cur:
            continue  # 尚无行情数据
        latest, *rest = cur
        prev_close = rest[0]["close"] if rest else None
        close = latest["close"]
        rows.append({
            "market": market,
            "code": s["code"],
            "name": s["name"],
            "exchange": s.get("exchange"),
            "trade_date": latest["trade_date"].isoformat(),
            "price": close,
            "prev_close": prev_close,
            "change": round(close - prev_close, 4) if prev_close is not None else None,
            "change_pct": pct_change(prev_close, close),
        })
    return rows


def market_rows(conn, market: str, keyword: str | None = None) -> list[dict]:
    """市场行情行（最新价 + 涨跌幅）。keyword 模糊匹配 代码/名称。"""
    rows = _latest_rows(conn, market)
    if keyword:
        kw = keyword.strip()
        rows = [r for r in rows if kw.lower() in r["code"].lower() or kw.lower() in r["name"].lower()]
    return rows


def stock_bars(conn, market: str, code: str, days: int) -> list[dict]:
    """取最近 days 根日线并按时间升序返回。多取 60 根用于给均线“预热”，再截断。"""
    fetch = days + max(MA_WINDOWS)
    rows = _query_all(
        conn,
        "SELECT trade_date, open, high, low, close, volume "
        "FROM daily_quote WHERE market=%s AND code=%s "
        "ORDER BY trade_date DESC LIMIT %s",
        (market, code, fetch),
    )
    rows.reverse()  # 升序
    closes = [r["close"] for r in rows]
    mas = {w: moving_average(closes, w) for w in MA_WINDOWS}
    bars = []
    for i, r in enumerate(rows):
        bars.append({
            "date": r["trade_date"].isoformat(),
            "open": r["open"],
            "high": r["high"],
            "low": r["low"],
            "close": r["close"],
            "volume": r["volume"],
            **{f"ma{w}": mas[w][i] for w in MA_WINDOWS},
        })
    return bars[-days:] if days > 0 else bars


def stock_info(conn, market: str, code: str) -> dict | None:
    return _query_one(
        conn,
        "SELECT market, code, name, exchange FROM stock_info WHERE market=%s AND code=%s",
        (market, code),
    )


def _query_all(conn, sql: str, params: tuple) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return list(cur.fetchall())


def _query_one(conn, sql: str, params: tuple) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()
