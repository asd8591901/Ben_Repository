"""行情列表：GET /api/markets/{market}/stocks"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import market_service as svc
from ..db import get_db

router = APIRouter()

# 允许排序的字段（白名单，防止任意排序键）
_SORTABLE = {"price", "change_pct", "change", "code", "name", "exchange"}


@router.get("/markets/{market}/stocks")
def list_stocks(
    market: str,
    keyword: str | None = None,
    sort: str = Query("change_pct"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    conn=Depends(get_db),
):
    if not svc.is_valid_market(market):
        raise HTTPException(status_code=404, detail=f"不支持的市场: {market}")
    if sort not in _SORTABLE:
        raise HTTPException(status_code=422, detail=f"不支持排序字段: {sort}")

    rows = svc.market_rows(conn, market, keyword)
    reverse = order == "desc"
    if sort in ("price", "change_pct", "change"):
        rows.sort(key=lambda r: (r[sort] is None, r[sort] or 0), reverse=reverse)
    else:
        rows.sort(key=lambda r: str(r[sort] or "").lower(), reverse=reverse)

    total = len(rows)
    start = (page - 1) * size
    items = rows[start : start + size]
    return {"market": market, "total": total, "page": page, "size": size, "items": items}
