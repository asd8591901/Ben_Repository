// 后端 API 封装（走 vite proxy /api → localhost:8000）
const BASE = "/api";

async function get(path, params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") qs.set(k, v);
  });
  const query = qs.toString();
  const url = `${BASE}${path}${query ? "?" + query : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`请求失败 ${res.status} ${body}`);
  }
  return res.json();
}

export function listStocks(market, { keyword, sort, order, page, size } = {}) {
  return get(`/markets/${market}/stocks`, {
    keyword, sort, order, page, size,
  });
}

export function getKline(market, code, days = 250) {
  return get(`/markets/${market}/stocks/${code}/kline`, { days });
}

export function getOverview(market) {
  return get(`/markets/${market}/overview`);
}
