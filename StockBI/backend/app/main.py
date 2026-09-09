"""StockBI 后端入口：FastAPI + CORS + 路由挂载。"""
from __future__ import annotations

import datetime as dt

import pymysql
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import cors_origins, db_params
from .routers import kline, overview, stocks

app = FastAPI(title="StockBI API", version="0.1.0", description="A股+美股 日线行情看板后端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api", tags=["行情列表"])
app.include_router(kline.router, prefix="/api", tags=["K线"])
app.include_router(overview.router, prefix="/api", tags=["概览"])


@app.get("/api/health", tags=["系统"])
def health():
    """存活检查 + DB ping。"""
    db_status = "up"
    try:
        conn = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor, autocommit=True, **db_params()
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
    except pymysql.MySQLError as e:
        db_status = f"down: {e}"
    return {"status": "ok", "db": db_status, "time": dt.datetime.now().isoformat()}
