"""市场概览：GET /api/markets/{market}/overview  （涨/跌家数 + 领涨领跌 top5）"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import market_service as svc
from ..db import get_db

router = APIRouter()


@router.get("/markets/{market}/overview")
def overview(market: str, conn=Depends(get_db)):
    if not svc.is_valid_market(market):
        raise HTTPException(status_code=404, detail=f"不支持的市场: {market}")

    rows = svc.market_rows(conn, market)
    up = [r for r in rows if (r["change_pct"] or 0) > 0]
    down = [r for r in rows if (r["change_pct"] or 0) < 0]
    flat = [r for r in rows if (r["change_pct"] or 0) == 0]

    top = sorted(rows, key=lambda r: r["change_pct"] or 0, reverse=True)
    return {
        "market": market,
        "count": len(rows),
        "up_count": len(up),
        "down_count": len(down),
        "flat_count": len(flat),
        "top_gainers": top[:5],
        "top_losers": top[-5:][::-1] if top else [],
    }
