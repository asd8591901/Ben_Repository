<template>
  <div class="table-wrap">
    <table v-if="rows.length">
      <thead>
        <tr>
          <th class="num">代码</th>
          <th>名称</th>
          <th class="num">现价</th>
          <th class="num">涨跌幅</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="r in rows"
          :key="r.code"
          :class="{ selected: r.code === selectedCode }"
          @click="$emit('select', r)"
        >
          <td class="num code">
            {{ r.code }}<span v-if="r.exchange" class="ex">.{{ r.exchange }}</span>
          </td>
          <td class="name" :title="r.name">{{ r.name }}</td>
          <td class="num">{{ fmtPrice(r.price) }}</td>
          <td class="num">
            <span
              class="pct"
              :style="{ color: pctColor(market, r.change_pct) }"
            >{{ fmtPct(r.change_pct) }}</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty">
      {{ loading ? "加载中…" : (error || "暂无行情数据") }}
    </div>
  </div>
</template>

<script setup>
import { fmtPct, fmtPrice, pctColor } from "../theme.js";

defineProps({
  rows: { type: Array, default: () => [] },
  market: { type: String, required: true },
  selectedCode: { type: String, default: "" },
  loading: Boolean,
  error: String,
});
defineEmits(["select"]);
</script>

<style scoped>
.table-wrap {
  height: 100%;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--panel);
}
table { width: 100%; border-collapse: collapse; }
th, td {
  padding: 8px 12px;
  text-align: left;
  white-space: nowrap;
}
thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--panel-2);
  color: var(--text-dim);
  font-weight: 600;
  font-size: 12px;
  border-bottom: 1px solid var(--border);
}
th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
tbody tr { cursor: pointer; border-bottom: 1px solid rgba(38, 50, 74, 0.4); }
tbody tr:hover { background: rgba(76, 141, 255, 0.08); }
tbody tr.selected { background: rgba(76, 141, 255, 0.18); }
tbody tr.selected td { box-shadow: inset 3px 0 0 var(--accent); }
.code { color: var(--text-dim); }
.ex { color: var(--text-dim); font-size: 11px; opacity: 0.7; }
.name { max-width: 160px; overflow: hidden; text-overflow: ellipsis; }
.pct { font-weight: 600; }
.empty {
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--text-dim);
  padding: 40px;
}
</style>
