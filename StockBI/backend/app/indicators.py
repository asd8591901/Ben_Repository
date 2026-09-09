"""技术指标纯函数（不依赖 DB / 网络），便于单测。输入都按时间升序。"""
from __future__ import annotations


def moving_average(values: list[float], n: int) -> list[float | None]:
    """简单移动平均。前 n-1 个位置无足够数据 → None。

    例：moving_average([1,2,3,4], 3) → [None, None, 2.0, 3.0]
    """
    if n <= 0:
        raise ValueError("n 必须为正整数")
    out: list[float | None] = []
    window_sum = 0.0
    for i, v in enumerate(values):
        window_sum += v
        if i >= n:
            window_sum -= values[i - n]
        out.append(round(window_sum / n, 2) if i + 1 >= n else None)
    return out


def pct_change(prev: float | None, cur: float | None) -> float | None:
    """涨跌幅百分比（%）。prev 缺失/为 0 时返回 None。"""
    if prev is None or cur is None or prev == 0:
        return None
    return round((cur - prev) / prev * 100, 2)
