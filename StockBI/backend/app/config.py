"""应用配置：读取仓库根目录 .env（含连接参数），缺省值对齐 docker-compose。"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]  # StockBI/
_DEFAULTS = {
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_PORT": "3306",
    "MYSQL_USER": "stockbi",
    "MYSQL_PASSWORD": "stockbi123",
    "MYSQL_DATABASE": "stockbi",
    "CORS_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
}


def load() -> dict:
    load_dotenv(_ROOT / ".env")  # 找不到文件时静默跳过
    out = {k: os.getenv(k, _DEFAULTS[k]) for k in _DEFAULTS}
    return out


settings = load()


def db_params() -> dict:
    return {
        "host": settings["MYSQL_HOST"],
        "port": int(settings["MYSQL_PORT"]),
        "user": settings["MYSQL_USER"],
        "password": settings["MYSQL_PASSWORD"],
        "database": settings["MYSQL_DATABASE"],
    }


def cors_origins() -> list[str]:
    return [o.strip() for o in settings["CORS_ORIGINS"].split(",") if o.strip()]
