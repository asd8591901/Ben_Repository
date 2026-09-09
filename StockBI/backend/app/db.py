"""MySQL 连接管理。轻量方案：每个请求/调用短连接，用完即关。"""
from __future__ import annotations

import pymysql
import pymysql.cursors
from fastapi import Depends

from .config import db_params


def connect():
    params = db_params()
    return pymysql.connect(
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        **params,
    )


def get_db():
    """FastAPI 依赖：按请求提供一个连接，请求结束自动关闭。"""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
