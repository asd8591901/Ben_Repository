// 涨跌配色：A股红涨绿跌，美股绿涨红跌
export const COLORS = {
  A: { up: "#e5484d", down: "#16a34a" },
  US: { up: "#16a34a", down: "#e5484d" },
};

export function colorFor(market) {
  return COLORS[market] || COLORS.A;
}

// 由涨跌幅数字取该市场应显示的涨跌色
export function pctColor(market, pct) {
  const { up, down } = colorFor(market);
  if (pct === null || pct === undefined) return "#8b96ab";
  if (pct > 0) return up;
  if (pct < 0) return down;
  return "#b9c1d0";
}

// 格式化涨跌幅：1.24 → "+1.24%"
export function fmtPct(pct, digits = 2) {
  if (pct === null || pct === undefined) return "--";
  const s = pct.toFixed(digits);
  return (pct > 0 ? "+" : "") + s + "%";
}

export function fmtPrice(p, digits = 2) {
  if (p === null || p === undefined) return "--";
  return Number(p).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}
