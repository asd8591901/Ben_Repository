# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

StockBI 是 A股 + 美股 双市场日线行情看板（Dashboard）。数据链路是单向四层：

```
collector/ 采集入库  →  MySQL 8 (docker)  →  backend/ FastAPI /api  →  frontend/ Vue3 页签看板
(akshare A股 / yfinance 美股 / 演示种子)      (行情列表 / K线 / 概览)     (A股 / 美股 两个页签)
```

核心约定：**行情先落地 MySQL，前端一律经后端 API 读库**，不直接连第三方行情源。

## 常用命令

前置：Docker、Node ≥18、Python ≥3.10。`.env` 在仓库根目录（复制 `.env.example` 而来，已 gitignore）。

```bash
# 起 MySQL（首次自动执行 init_db/01_schema.sql 建库建表）
docker compose up -d mysql
# 改表结构后重建（init 脚本只在数据卷为空时执行一次）：
docker compose down -v && docker compose up -d mysql

# 灌演示数据（离线确定性生成，无需联网）
cd collector && source .venv/bin/activate
python seed_demo.py

# 拉真实行情（需联网）
python fetch.py a 600519,000001,300750 2023-01-01 2026-09-09
python fetch.py us AAPL,MSFT,NVDA 2023-01-01 2026-09-09

# 起后端（端口 8000）
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 后端单测（纯逻辑，无需 DB/网络）
cd backend && source .venv/bin/activate && python -m pytest

# 起前端（vite dev，5173，/api 已代理到 8000）
cd frontend && npm run dev
```

## 数据模型与市场代码

表在 `init_db/01_schema.sql`，三张：`stock_info`、`daily_quote`、`watchlist`（预留）。

- 行情代码**不带交易所后缀**：A股 `600519`，美股 `AAPL`；`market` 列（`'A'`/`'US'`）区分市场。
- `daily_quote` 用 `(market, code, trade_date)` 联合唯一键去重；采集统一 `INSERT ... ON DUPLICATE KEY UPDATE`（`collector/db.py`），重复跑不脏库。
- A股 `stock_info.exchange` 存 `SH/SZ`，由代码前缀推断（`normalize.infer_a_exchange`）；美股为空（前端不依赖）。

## 分层要点

- **collector/**（`requirements.txt` 独立 venv）：`normalize.py` 把数据源统一成标准 bar `{date,open,high,low,close,volume,amount}`。
  - akshare（`fetch_a.py`）中文列名→标准列，映射集中在 `normalize.AKSHARE_COL_MAP`，接口/列名随版本变，改动只需动这里。A股用**前复权 qfq**。
  - yfinance（`fetch_us.py`）日线**原始价**（`auto_adjust=False`）；其 DatetimeIndex 带美东时区，入库前在 `normalize.normalize_yfinance` 里 `tz_localize(None)` 再取 `.date()`，防日期偏移一天。
  - akshare/yfinance 依赖较重，import 全部延迟到函数内（`fetch_a.py`/`fetch_us.py` 顶部仅放 `sys.path` 引导），seed/测试无需安装它们。
- **backend/app/**（FastAPI + PyMySQL，短连接按请求建/关，见 `db.py` 的 `get_db` 依赖）：
  - `indicators.py` 是**纯函数**（MA、涨跌幅），无 DB/网络依赖，配单测。
  - `market_service.py` 承担查询与计算（最新价、涨跌幅、K线均线）；路由薄。MA5/10/20/60 在**服务端**算好随 K 线返回，前端只画图。
  - 排序字段走白名单（`routers/stocks.py` 的 `_SORTABLE`），避免任意排序键。
- **frontend/**（Vue3 + Vite + ECharts 按需引入，见 `KLineChart.vue` 顶部 `echarts.use`）：
  - `App.vue` 用 **A股/美股页签**，`:key="active"` 切换即重建，状态自清；两个市场共用同一个 `MarketView`（props=market）。
  - 涨跌配色按市场分：A股红涨绿跌、美股绿涨红跌，集中定义在 `src/theme.js`，别在组件里散写颜色。

## 其它

- 改动表结构后想让它生效，需 `docker compose down -v`（见上）；生产数据别这么干。
- 前端路由不引入 vue-router：页签就是顶层状态，新增“页”可沿用 App.vue 现有模式或再加路由。
- 贡献点参考：watchlist 表已建但后端 `routers/` 尚未提供接口；前端 bundle 以 ECharts 为主，未来可对页签做代码分割。
