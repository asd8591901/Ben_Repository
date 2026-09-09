"""把不同数据源的行情 DataFrame 统一成标准 bar 列表。

标准 bar: {date: datetime.date, open/high/low/close: float, volume: int|None, amount: float|None}
"""
from __future__ import annotations

import datetime as dt

import pandas as pd

# akshare stock_zh_a_hist 的中文列名 → 标准字段
# （akshare 个别版本列名会变，命中率最高的核心字段做硬映射即可）
AKSHARE_COL_MAP = {
    "日期": "date",
    "开盘": "open",
    "最高": "high",
    "最低": "low",
    "收盘": "close",
    "成交量": "volume",
    "成交额": "amount",
}


def normalize_akshare(df: pd.DataFrame, code: str) -> list[dict]:
    """A股日线（akshare，前复权 qfq）→ 标准 bars。"""
    keep = {c for c in AKSHARE_COL_MAP if c in df.columns}
    sub = df[list(keep)].copy()
    sub = sub.rename(columns={c: AKSHARE_COL_MAP[c] for c in keep})

    bars = []
    for _, r in sub.iterrows():
        try:
            d = pd.to_datetime(r["date"]).date()
        except Exception:
            continue
        open_, high = float(r["open"]), float(r["high"])
        low, close = float(r["low"]), float(r["close"])
        if not (close > 0 and high >= low and high >= max(open_, close) and low <= min(open_, close)):
            continue  # 过滤异常/停牌空行
        vol = r.get("volume")
        amt = r.get("amount")
        bars.append({
            "date": d,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": int(vol) if pd.notna(vol) else None,
            "amount": float(amt) if pd.notna(amt) else None,
        })
    bars.sort(key=lambda b: b["date"])
    return bars


def normalize_yfinance(df: pd.DataFrame, ticker: str) -> list[dict]:
    """美股日线（yfinance, auto_adjust=False 原始价）→ 标准 bars。

    yfinance 用多列时返回 MultiIndex 列（字段, ticker），这里只保留第一层字段；
    DatetimeIndex 常带美东时区，先转无时区再取 .date()，避免入库日期偏移一天。
    """
    if df is None or df.empty:
        return []
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    idx = df.index
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    dates = [pd.Timestamp(t).date() for t in idx]

    bars = []
    for d, (_, r) in zip(dates, df.iterrows()):
        try:
            open_, high = float(r["Open"]), float(r["High"])
            low, close = float(r["Low"]), float(r["Close"])
        except Exception:
            continue
        if not (close > 0 and high >= low):
            continue
        vol = r.get("Volume")
        bars.append({
            "date": d,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": int(vol) if pd.notna(vol) else None,
            "amount": None,  # yfinance 不直接给成交额，美股列 amount 留空
        })
    bars.sort(key=lambda b: b["date"])
    return bars


def infer_a_exchange(code: str) -> str:
    """由 A股代码前缀推断交易所（6xx/9xx=SH 沪，0xx/3xx=SZ 深，8xx/4xx/92x=BJ 北）。"""
    if code.startswith(("6", "5", "9")):
        return "SH"
    if code.startswith(("0", "3", "2")):
        return "SZ"
    return "BJ"


def parse_date(s: str) -> dt.date | None:
    """'YYYY-MM-DD' 或 'YYYYMMDD' → date；解析失败返回 None。"""
    s = str(s).strip().replace("-", "").replace("/", "")
    if len(s) != 8 or not s.isdigit():
        return None
    try:
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))
    except ValueError:
        return None
