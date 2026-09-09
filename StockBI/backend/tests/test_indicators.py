"""indicators 纯函数单元测试：python -m pytest"""
from app.indicators import moving_average, pct_change


class TestMovingAverage:
    def test_head_padded_with_none(self):
        assert moving_average([1, 2, 3, 4], 3) == [None, None, 2.0, 3.0]

    def test_ma1_equals_values(self):
        assert moving_average([5.0, 10.0, 15.0], 1) == [5.0, 10.0, 15.0]

    def test_ma_over_series(self):
        # MA5 of 1..5 = 3.0; 2..6 = 4.0
        assert moving_average([1, 2, 3, 4, 5, 6], 5) == [None] * 4 + [3.0, 4.0]

    def test_rounding_two_decimals(self):
        assert moving_average([1.0, 2.0], 2) == [None, 1.5]
        assert moving_average([1.0, 1.0, 1.0], 3)[-1] == 1.0

    def test_empty(self):
        assert moving_average([], 5) == []

    def test_invalid_window(self):
        try:
            moving_average([1, 2], 0)
        except ValueError:
            return
        raise AssertionError("n=0 应抛 ValueError")


class TestPctChange:
    def test_normal(self):
        assert pct_change(10.0, 10.5) == 5.0

    def test_negative(self):
        assert pct_change(10.0, 9.5) == -5.0

    def test_none_and_zero_prev(self):
        assert pct_change(None, 10.0) is None
        assert pct_change(0.0, 10.0) is None
        assert pct_change(10.0, None) is None

    def test_zero_growth(self):
        assert pct_change(10.0, 10.0) == 0.0
