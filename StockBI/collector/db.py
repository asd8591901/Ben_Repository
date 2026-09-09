"""collector / backend 共用的 MySQL 连接与入库助手。

.env 读取规则：优先当前目录，再向上级目录找（collector 在 StockBI/ 子目录时
读仓库根目录的 .env）。找不到就退回与 docker-compose.yml 一致的默认值。
"""
from __future__ import annotations

import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

_DEFAULTS = {
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_PORT": "3306",
    "MYSQL_USER": "stockbi",
    "MYSQL_PASSWORD": "stockbi123",
    "MYSQL_DATABASE": "stockbi",
}


def _find_dotenv() -> str | None:
    """从当前目录逐级向上找 .env，支持从仓库任意子目录运行。"""
    cur = Path.cwd()
    for d in [cur, *cur.parents]:
        env = d / ".env"
        if env.is_file():
            return str(env)
    return None


def db_params() -> dict:
    path = _find_dotenv()
    if path:
        load_dotenv(path)
    return {
        "host": os.getenv("MYSQL_HOST", _DEFAULTS["MYSQL_HOST"]),
        "port": int(os.getenv("MYSQL_PORT", _DEFAULTS["MYSQL_PORT"])),
        "user": os.getenv("MYSQL_USER", _DEFAULTS["MYSQL_USER"]),
        "password": os.getenv("MYSQL_PASSWORD", _DEFAULTS["MYSQL_PASSWORD"]),
        "database": os.getenv("MYSQL_DATABASE", _DEFAULTS["MYSQL_DATABASE"]),
    }


def get_conn():
    params = db_params()
    return pymysql.connect(
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        **params,
    )


# ---- 入库（全部幂等：INSERT ... ON DUPLICATE KEY UPDATE） ----

def upsert_stock(conn, market: str, code: str, name: str, exchange: str | None = None) -> None:
    sql = """
        INSERT INTO stock_info (market, code, name, exchange)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), exchange = VALUES(exchange)
    """
    with conn.cursor() as cur:
        cur.execute(sql, (market, code, name, exchange))


def upsert_quotes(conn, market: str, code: str, bars: list[dict]) -> int:
    """bars: [{date(或date-str), open, high, low, close, volume, amount}, ...]"""
    if not bars:
        return 0
    sql = """
        INSERT INTO daily_quote (market, code, trade_date, open, high, low, close, volume, amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          open = VALUES(open), high = VALUES(high), low = VALUES(low),
          close = VALUES(close), volume = VALUES(volume), amount = VALUES(amount)
    """
    rows = [
        (
            market, code, str(b["date"]),
            float(b["open"]), float(b["high"]), float(b["low"]), float(b["close"]),
            b.get("volume"), b.get("amount"),
        )
        for b in bars
    ]
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)
