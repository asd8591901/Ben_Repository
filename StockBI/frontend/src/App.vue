<template>
  <div class="app">
    <header class="top">
      <div class="brand">
        <span class="logo">📈</span>
        <div>
          <h1>StockBI</h1>
          <p>A股 · 美股 日线行情看板</p>
        </div>
      </div>
      <nav class="tabs">
        <button
          v-for="t in markets"
          :key="t.value"
          class="tab"
          :class="{ active: active === t.value }"
          @click="active = t.value"
        >
          {{ t.label }}
        </button>
      </nav>
    </header>

    <!-- key 保证切换市场时整页重建、选中态重置 -->
    <main class="body">
      <MarketView :market="active" :key="active" />
    </main>

    <footer class="foot">
      StockBI · 演示数据可离线运行，真实行情请运行 collector/fetch.py
    </footer>
  </div>
</template>

<script setup>
import { ref } from "vue";
import MarketView from "./views/MarketView.vue";

const markets = [
  { value: "A", label: "A股" },
  { value: "US", label: "美股" },
];
const active = ref("A");
</script>

<style scoped>
.app {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
  flex-wrap: wrap;
  gap: 8px;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand .logo { font-size: 26px; }
.brand h1 { margin: 0; font-size: 18px; letter-spacing: 0.5px; }
.brand p { margin: 2px 0 0; font-size: 12px; color: var(--text-dim); }

.tabs {
  display: flex;
  gap: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 3px;
}
.tab {
  border: none;
  background: transparent;
  color: var(--text-dim);
  font-size: 14px;
  padding: 6px 22px;
  border-radius: 6px;
  cursor: pointer;
}
.tab.active {
  background: var(--accent);
  color: #fff;
  font-weight: 600;
}
.tab:hover:not(.active) { color: var(--text); }

.body { flex: 1; overflow: auto; padding: 14px 18px; }
.foot {
  padding: 8px 18px;
  font-size: 12px;
  color: var(--text-dim);
  border-top: 1px solid var(--border);
  background: var(--panel);
}
</style>
