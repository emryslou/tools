import pytest

class TestHumanReadableTime:
    def test_format_time_multi_units(self):
        from tools.format.time import format_time_multi_units, UnitName
        assert format_time_multi_units(0) == '0 秒'
        assert format_time_multi_units(1) == '1 秒'
        assert format_time_multi_units(60) == '1 分'
        assert format_time_multi_units(60 * 2) == '2 分'
        assert format_time_multi_units(60 * 60) == '1 小时'
        assert format_time_multi_units(60 * 60 * 2) == '2 小时'
        assert format_time_multi_units(60 * 60 * 24) == '1 天'
        assert format_time_multi_units(60 * 60 * 24 * 2) == '2 天'
        assert format_time_multi_units(60 * 60 * 24 * 30.44) == '1 月'
        assert format_time_multi_units(60 * 60 * 24 * 30.44 * 2) == '2 月'
        assert format_time_multi_units(60 * 60 * 24 * 365) == '1 年'
        assert format_time_multi_units(60 * 60 * 24 * 365 * 2) == '2 年'
