<template>
  <div ref="el" class="kline-chart"></div>
</template>

<script setup>
import * as echarts from "echarts/core";
import { BarChart, CandlestickChart, LineChart } from "echarts/charts";
import {
  AxisPointerComponent,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { colorFor } from "../theme.js";

echarts.use([
  CandlestickChart,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  AxisPointerComponent,
  CanvasRenderer,
]);

const props = defineProps({
  bars: { type: Array, required: true }, // [{date,open,high,low,close,volume,ma5,...}]
  market: { type: String, required: true },
});

const el = ref(null);
let chart = null;

const MA_LINES = [
  { key: "ma5", label: "MA5", color: "#e8b34b" },
  { key: "ma10", label: "MA10", color: "#5c9ded" },
  { key: "ma20", label: "MA20", color: "#c678dd" },
  { key: "ma60", label: "MA60", color: "#4cc2a8" },
];

function buildOption(bars, market) {
  const { up, down } = colorFor(market);
  const dates = bars.map((b) => b.date);
  const kData = bars.map((b) => [b.open, b.close, b.low, b.high]);
  const vols = bars.map((b, i) => ({
    value: b.volume,
    itemStyle: { color: b.close >= b.open ? up : down, opacity: 0.55 },
  }));

  const series = [
    {
      name: "K线",
      type: "candlestick",
      data: kData,
      itemStyle: { color: up, color0: down, borderColor: up, borderColor0: down },
    },
    ...MA_LINES.map((m) => ({
      name: m.label,
      type: "line",
      data: bars.map((b) => b[m.key]),
      smooth: true,
      symbol: "none",
      lineStyle: { width: 1, color: m.color },
      itemStyle: { color: m.color },
    })),
    {
      name: "成交量",
      type: "bar",
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: vols,
    },
  ];

  return {
    backgroundColor: "transparent",
    animation: false,
    legend: {
      data: ["K线", ...MA_LINES.map((m) => m.label)],
      top: 2,
      left: 6,
      textStyle: { color: "#8b96ab", fontSize: 11 },
      itemWidth: 12,
      itemHeight: 2,
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross", label: { backgroundColor: "#2c3a56" } },
      backgroundColor: "#1c2639",
      borderColor: "#33405e",
      textStyle: { color: "#dbe3f0", fontSize: 12 },
      formatter: (params) => {
        const k = params.find((p) => p.seriesType === "candlestick");
        if (!k) return "";
        const b = bars[k.dataIndex];
        if (!b) return "";
        const upColor = b.close >= b.open ? up : down;
        const row = (t, v, color = "") =>
          `<tr><td style="padding:1px 10px 1px 0;color:#8b96ab">${t}</td>` +
          `<td style="text-align:right;${color ? `color:${color}` : ""}">${v}</td></tr>`;
        return (
          `<div style="font-weight:600">${b.date}</div><table>` +
          row("开盘", b.open.toFixed(2)) +
          row("最高", b.high.toFixed(2), upColor) +
          row("最低", b.low.toFixed(2), upColor) +
          row("收盘", b.close.toFixed(2), upColor) +
          row("成交量", (b.volume ?? "--").toLocaleString()) +
          `</table>`
        );
      },
    },
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    grid: [
      { left: 56, right: 16, top: 30, height: "56%" },
      { left: 56, right: 16, top: "74%", height: "13%" },
    ],
    xAxis: [
      {
        type: "category",
        data: dates,
        boundaryGap: true,
        axisLine: { lineStyle: { color: "#33405e" } },
        axisLabel: { color: "#8b96ab", fontSize: 10 },
        splitLine: { show: false },
        min: "dataMin",
        max: "dataMax",
      },
      {
        type: "category",
        gridIndex: 1,
        data: dates,
        axisLine: { lineStyle: { color: "#33405e" } },
        axisLabel: { show: false },
        splitLine: { show: false },
      },
    ],
    yAxis: [
      {
        scale: true,
        axisLine: { show: false },
        axisLabel: { color: "#8b96ab", fontSize: 10 },
        splitLine: { lineStyle: { color: "#222c43" } },
      },
      {
        gridIndex: 1,
        scale: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        splitLine: { show: false },
      },
    ],
    dataZoom: [
      { type: "inside", xAxisIndex: [0, 1], start: 55, end: 100 },
      { type: "slider", xAxisIndex: [0, 1], start: 55, end: 100, bottom: 0, height: 14 },
    ],
    series,
  };
}

function render() {
  if (!chart || !props.bars.length) return;
  chart.setOption(buildOption(props.bars, props.market), true);
}

function onResize() {
  chart && chart.resize();
}

watch(
  () => [props.bars, props.market],
  () => render()
);

onMounted(() => {
  chart = echarts.init(el.value);
  render();
  window.addEventListener("resize", onResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  chart && chart.dispose();
  chart = null;
});
</script>

<style scoped>
.kline-chart {
  width: 100%;
  height: 100%;
  min-height: 380px;
}
</style>
