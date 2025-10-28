import pytest

class TestHumanReadableSize:
    def test_format_size_multi_units(self):
        from tools.format.size import format_size_multi_units
        assert format_size_multi_units(2 ** 0) == '1 B'
        assert format_size_multi_units(100) == '100 B'
        assert format_size_multi_units(1023) == '1023 B'

        assert format_size_multi_units(2 ** 10) == '1 KB'
        assert format_size_multi_units(2 ** 10 + 1) == '1 KB, 1 B'
        assert format_size_multi_units(2 ** 10 + 512) == '1 KB, 512 B'
        assert format_size_multi_units(2 ** 10 * 100) == '100 KB'
        assert format_size_multi_units(2 ** 10 * 100 + 1000) == '100 KB, 1000 B'

        assert format_size_multi_units(2 ** 20) == '1 MB'
        assert format_size_multi_units(2 ** 20 + 1) == '1 MB, 1 B'
        assert format_size_multi_units(2 ** 20 + 512) == '1 MB, 512 B'
        assert format_size_multi_units(2 ** 20 * 100) == '100 MB'
        assert format_size_multi_units(2 ** 20 * 100 + 2 ** 10 * 300 + 1000) == '100 MB, 300 KB, 1000 B'
        assert format_size_multi_units(2 ** 20 * 100 + 2 ** 10 * 1023) == '100 MB, 1023 KB'

        assert format_size_multi_units(2 ** 30) == '1 GB'
        assert format_size_multi_units(2 ** 40) == '1 TB'
        assert format_size_multi_units(2 ** 50) == '1 PB'
        assert format_size_multi_units(2 ** 60) == '1 EB'
        assert format_size_multi_units(2 ** 70) == '1 ZB'
        assert format_size_multi_units(2 ** 80) == '1 YB'
        assert format_size_multi_units(2 ** 90) == '1024 YB'
    
    def test_format_size_multi_units_min_unit(self):
        from tools.format.size import format_size_multi_units, UnitName
        assert format_size_multi_units(2 ** 0, min_unit=UnitName.KB) == '0 KB'
        assert format_size_multi_units(100, min_unit=UnitName.KB) == '0 KB'
        assert format_size_multi_units(1023, min_unit=UnitName.KB) == '0 KB'
        assert format_size_multi_units(2 ** 10, min_unit=UnitName.KB) == '1 KB'
        assert format_size_multi_units(2 ** 10 + 1, min_unit=UnitName.KB) == '1 KB'
        assert format_size_multi_units(2 ** 10 + 512, min_unit=UnitName.KB) == '1 KB'
        assert format_size_multi_units(2 ** 10 * 100, min_unit=UnitName.KB) == '100 KB'
        assert format_size_multi_units(2 ** 10 * 100 + 1000, min_unit=UnitName.KB) == '100 KB'
        assert format_size_multi_units(2**20 * 50 + 2 ** 10 * 100 + 1000, min_unit=UnitName.KB) == '50 MB, 100 KB'
    
    def test_format_size_multi_units_max_unit(self):
        from tools.format.size import format_size_multi_units, UnitName
        assert format_size_multi_units(2 ** 0, max_unit=UnitName.KB) == '1 B'
        assert format_size_multi_units(100, max_unit=UnitName.KB) == '100 B'
        assert format_size_multi_units(1023, max_unit=UnitName.KB) == '1023 B'
        assert format_size_multi_units(2 ** 10, max_unit=UnitName.KB) == '1 KB'
        assert format_size_multi_units(2 ** 10 + 1, max_unit=UnitName.KB) == '1 KB, 1 B'
        assert format_size_multi_units(2 ** 10 + 512, max_unit=UnitName.KB) == '1 KB, 512 B'
        assert format_size_multi_units(2 ** 10 * 100, max_unit=UnitName.KB) == '100 KB'
        assert format_size_multi_units(2 ** 20 + 100 * 2 ** 10, max_unit=UnitName.KB) == '1124 KB'
        assert format_size_multi_units(2 ** 20 + 100 * 2 ** 10 + 1000, max_unit=UnitName.KB) == '1124 KB, 1000 B'
    
    def test_format_size_multi_units_min_max_unit(self):
        from tools.format.size import format_size_multi_units, UnitName
        
        with pytest.raises(AssertionError):
            format_size_multi_units(2 ** 0, min_unit=UnitName.KB, max_unit=UnitName.KB)
        
        with pytest.raises(AssertionError):
            format_size_multi_units(2 ** 0, min_unit=UnitName.KB, max_unit=UnitName.B)

    def test_format_size(self):
        from tools.format.size import format_size
        assert format_size(2 ** 0) == '1 B'
        assert format_size(100) == '100 B'
        assert format_size(1023) == '1023 B'
        assert format_size(1024) == '1 KB'
        assert format_size(2 ** 10 + 1) == f'{1025/1024:.3f} KB'
        assert format_size(2 ** 20 + 100000) == f'{(2 ** 20 + 100000)/(2**20):.3f} MB'
        assert format_size(2 ** 30 + 100 * 2 ** 20) == f'{(2 ** 30 + 100 * 2 ** 20)/(2**30):.3f} GB'
            