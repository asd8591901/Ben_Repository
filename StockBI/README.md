# StockBI 股票看板

A股 + 美股 双市场日线行情看板。全栈脚手架：行情采集 → MySQL → FastAPI → Vue3 前端。

```
┌────────────┐   ┌────────────┐   ┌──────────────┐   ┌──────────────────┐
│ collector  │ → │ MySQL 8    │ → │ backend      │ → │ frontend Vue3    │
│ akshare /  │   │ (docker)   │   │ FastAPI /api │   │ A股/美股页签看板   │
│ yfinance   │   │ 行情入库     │   │ 列表+K线+指标 │   │ 蜡烛图+均线+成交量 │
└────────────┘   └────────────┘   └──────────────┘   └──────────────────┘
```

## 快速开始

前置：Docker、Node ≥ 18、Python ≥ 3.10。

```bash
# 1) 起 MySQL（首次会自动建库建表）
cp .env.example .env
docker compose up -d mysql

# 2) 灌入演示数据（确定性生成，不联网即可看到看板）
cd collector
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed_demo.py

# 3) 起后端（另开终端）
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4) 起前端（另开终端）
cd frontend
npm install
npm run dev          # 打开 http://localhost:5173
```

浏览器打开后：顶部切 **A股 / 美股**，左侧行情表点任意股票 → 右侧出现蜡烛图 + 均线 + 成交量。

## 拉取真实行情（需联网）

默认库里的“演示数据”是**离线合成**的，只看结构用；想看到真实股价请换成真实日线。

```bash
cd collector && source .venv/bin/activate

# ① 一次性：把合成行情清掉，全量回填清单里股票的真实日线（2023-01-01 起）
python refresh.py --full

# 之后每个交易日收盘后只需增量刷新（自动从库里最大日期续拉）
python refresh.py                # A股 + 美股
python refresh.py --market a     # 只刷 A股
```

想自定义代码/起始日期，用底层 `fetch.py`（`--clear` 先清空防混数据）：

```bash
# A股（代码不带交易所后缀）
python fetch.py a 600519,000001 --clear 2023-01-01 2026-09-09
# 美股
python fetch.py us AAPL,MSFT --clear 2023-01-01 2026-09-09
```

**每日自动刷新**：编辑自己的 crontab（`crontab -e`），收盘后跑一次增量：

```cron
# 每个交易日 18:05 自动刷新（路径按实际改）
5 18 * * 1-5 cd /home/ben/Desktop/Github/Ben_Repository/StockBI/collector && .venv/bin/python refresh.py >> refresh.log 2>&1
```

A股用 [akshare](https://akshare.akfamily.xyz/)（免费、无需 key），美股用 [yfinance](https://github.com/ranaroussi/yfinance)。行情统一 **`INSERT ... ON DUPLICATE KEY UPDATE`** 入库，重复跑不产生脏数据。跟踪的股票清单在 `collector/watchlist.py` 里增删。

## API（前缀 /api）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 存活检查 + DB ping |
| GET | `/api/markets/{A\|US}/stocks?keyword=&sort=&order=&page=&size=` | 行情列表（含最新价/涨跌幅，默认按涨跌幅排） |
| GET | `/api/markets/{A\|US}/stocks/{code}/kline?days=250` | 日线 + MA5/10/20/60 |
| GET | `/api/markets/{A\|US}/overview` | 涨跌统计快照（涨/跌家数） |

## 后端测试

```bash
cd backend && source .venv/bin/activate
python -m pytest
```

## 目录结构

```
init_db/01_schema.sql   建库建表（MySQL 容器首次启动自动执行）
collector/              Python 采集器：演示种子 / akshare(A股) / yfinance(美股)
backend/                FastAPI 应用（app/routers 下分模块），indicators.py 纯函数算均线
frontend/               Vue3 + Vite：App.vue 页签 + MarketView 复用行情页 + ECharts K线组件
```

## 常见问题

- **改了表结构但容器不生效？** MySQL 的 `docker-entrypoint-initdb.d` 只在数据卷为空时执行一次。改 schema 后执行 `docker compose down -v && docker compose up -d mysql` 重建。
- **美股日期偏移一天？** 已处理：入库前统一转成无时区交易日。
- **A股/美股配色不同？** A股红涨绿跌、美股绿涨红跌，前端按市场自动切换。
