"""单只股票 K 线：GET /api/markets/{market}/stocks/{code}/kline"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import market_service as svc
from ..db import get_db

router = APIRouter()


@router.get("/markets/{market}/stocks/{code}/kline")
def kline(
    market: str,
    code: str,
    days: int = Query(250, ge=30, le=2000),
    conn=Depends(get_db),
):
    if not svc.is_valid_market(market):
        raise HTTPException(status_code=404, detail=f"不支持的市场: {market}")
    info = svc.stock_info(conn, market, code)
    if not info:
        raise HTTPException(status_code=404, detail=f"股票不存在: {market}/{code}")

    bars = svc.stock_bars(conn, market, code, days)
    latest = bars[-1] if bars else None
    return {"market": market, "code": code, "name": info["name"], "bars": bars, "latest": latest}
