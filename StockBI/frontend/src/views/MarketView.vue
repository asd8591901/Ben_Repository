<template>
  <section class="market">
    <!-- 工具栏 -->
    <div class="toolbar">
      <h2 class="title">{{ label }}行情</h2>
      <span v-if="total !== null" class="count">共 {{ total }} 只</span>
      <input
        v-model="keywordInput"
        class="search"
        type="text"
        placeholder="搜索代码 / 名称，回车确认"
        @keyup.enter="applyKeyword"
      />
      <select v-model="sort" class="sort" @change="fetchRows()">
        <option v-for="s in SORTS" :key="s.value" :value="s.value">排序：{{ s.label }}</option>
      </select>
      <button class="btn" :title="order === 'desc' ? '降序' : '升序'" @click="toggleOrder">
        {{ order === "desc" ? "↓ 降序" : "↑ 升序" }}
      </button>
      <button class="btn" title="刷新" @click="fetchRows()">↻ 刷新</button>
    </div>

    <!-- 左列表 / 右详情 -->
    <div class="split">
      <div class="pane-left">
        <StockTable
          :rows="rows"
          :market="market"
          :selected-code="selected ? selected.code : ''"
          :loading="loading"
          :error="listError"
          @select="selectStock"
        />
        <div class="pager" v-if="total > size">
          <button class="btn" :disabled="page <= 1" @click="goPage(page - 1)">‹ 上一页</button>
          <span class="page-info">{{ page }} / {{ Math.max(1, Math.ceil(total / size)) }}</span>
          <button class="btn" :disabled="page * size >= total" @click="goPage(page + 1)">下一页 ›</button>
        </div>
      </div>

      <div class="pane-right">
        <!-- 选中股票头信息 -->
        <div v-if="selected" class="stock-head">
          <div class="ident">
            <span class="code">{{ selected.code }}<span v-if="selected.exchange" class="ex">.{{ selected.exchange }}</span></span>
            <span class="name">{{ selected.name }}</span>
          </div>
          <div class="quote">
            <span class="price" :style="{ color: pctColor(market, selected.change_pct) }">
              {{ fmtPrice(selected.price) }}
            </span>
            <span class="pct" :style="{ color: pctColor(market, selected.change_pct) }">
              {{ fmtChange(selected) }}
            </span>
            <span class="date">{{ selected.trade_date }}</span>
          </div>
        </div>

        <div class="chart-area">
          <KLineChart v-if="klineBars && klineBars.length" :bars="klineBars" :market="market" />
          <div v-else-if="klineLoading" class="placeholder">K线加载中…</div>
          <div v-else class="placeholder">
            {{ klineError || (selected ? "该股票暂无日线数据" : "点击左侧股票查看 K 线") }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { getKline, listStocks } from "../api.js";
import StockTable from "../components/StockTable.vue";
import KLineChart from "../components/KLineChart.vue";
import { fmtPct, fmtPrice, pctColor } from "../theme.js";

const props = defineProps({ market: { type: String, required: true } });

const label = props.market === "A" ? "A股" : "美股";
const SORTS = [
  { value: "change_pct", label: "涨跌幅" },
  { value: "price", label: "现价" },
  { value: "code", label: "代码" },
  { value: "name", label: "名称" },
];

const rows = ref([]);
const total = ref(null);
const page = ref(1);
const size = 50;
const sort = ref("change_pct");
const order = ref("desc");
const loading = ref(false);
const listError = ref("");
const keywordInput = ref("");
const appliedKeyword = ref("");

const selected = ref(null); // {code,name,exchange,price,change_pct,trade_date}
const klineBars = ref([]);
const klineLoading = ref(false);
const klineError = ref("");

let timer = null;
watch(keywordInput, () => {
  clearTimeout(timer);
  timer = setTimeout(applyKeyword, 350);
});

async function fetchRows() {
  loading.value = true;
  listError.value = "";
  try {
    const data = await listStocks(props.market, {
      keyword: appliedKeyword.value,
      sort: sort.value,
      order: order.value,
      page: page.value,
      size,
    });
    rows.value = data.items || [];
    total.value = data.total || 0;
    // 无选中时自动选中第一行，让 K 线默认有内容
    if (!selected.value && rows.value.length) {
      selectStock(rows.value[0]);
    }
  } catch (e) {
    listError.value = e.message || String(e);
  } finally {
    loading.value = false;
  }
}

function applyKeyword() {
  appliedKeyword.value = keywordInput.value.trim();
  page.value = 1;
  selected.value = null;
  klineBars.value = [];
  fetchRows();
}

function toggleOrder() {
  order.value = order.value === "desc" ? "asc" : "desc";
  fetchRows();
}

function goPage(p) {
  page.value = p;
  fetchRows();
}

async function selectStock(r) {
  selected.value = r;
  klineLoading.value = true;
  klineError.value = "";
  klineBars.value = [];
  try {
    const data = await getKline(props.market, r.code, 250);
    klineBars.value = data.bars || [];
  } catch (e) {
    klineError.value = e.message || String(e);
  } finally {
    klineLoading.value = false;
  }
}

function fmtChange(r) {
  if (r.change_pct === null || r.change_pct === undefined) return "--";
  const parts = [];
  if (r.change !== null && r.change !== undefined)
    parts.push((r.change > 0 ? "+" : "") + Number(r.change).toFixed(2));
  parts.push(fmtPct(r.change_pct));
  return parts.join("  ");
}

onMounted(fetchRows);
</script>

<style scoped>
.market { height: 100%; display: flex; flex-direction: column; gap: 10px; }

.toolbar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.title { margin: 0; font-size: 16px; }
.count { color: var(--text-dim); font-size: 12px; }

.search {
  flex: 1;
  min-width: 200px;
  max-width: 340px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  padding: 7px 12px;
  outline: none;
}
.search:focus { border-color: var(--accent); }

.sort {
  background: var(--panel);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 8px;
  padding: 7px 8px;
}

.btn {
  background: var(--panel);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 8px;
  padding: 7px 12px;
  cursor: pointer;
  font-size: 13px;
}
.btn:hover:not(:disabled) { border-color: var(--accent); color: #fff; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.split {
  flex: 1;
  display: grid;
  grid-template-columns: 440px 1fr;
  gap: 12px;
  min-height: 480px;
  overflow: hidden;
}

.pane-left { display: flex; flex-direction: column; gap: 8px; min-height: 0; }
.pane-left :deep(.table-wrap) { flex: 1; min-height: 0; }

.pager { display: flex; align-items: center; gap: 8px; justify-content: center; }
.page-info { color: var(--text-dim); font-size: 12px; }

.pane-right {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  min-height: 0;
}

.stock-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 10px;
}
.ident { display: flex; align-items: baseline; gap: 10px; }
.ident .code { font-size: 18px; font-weight: 700; }
.ident .ex { font-size: 11px; color: var(--text-dim); }
.ident .name { font-size: 15px; color: var(--text-dim); }

.quote { display: flex; align-items: baseline; gap: 12px; }
.price { font-size: 26px; font-weight: 700; font-variant-numeric: tabular-nums; }
.pct { font-weight: 600; font-size: 15px; }
.date { color: var(--text-dim); font-size: 12px; }

.chart-area { flex: 1; min-height: 0; position: relative; }
.placeholder {
  height: 100%;
  min-height: 360px;
  display: grid;
  place-items: center;
  color: var(--text-dim);
  border: 1px dashed var(--border);
  border-radius: 8px;
}
</style>
