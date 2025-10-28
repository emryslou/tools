import pytest
from tools.format.util import __


class TestHumanUtil:
    units = [('B',  2 ** 0), ('KB', 2 ** 10), ('MB', 2 ** 20),
        ('GB', 2 ** 30), ('TB', 2 ** 40), ('PB', 2 ** 50),
        ('EB', 2 ** 60), ('ZB', 2 ** 70), ('YB', 2 ** 80),
    ]

    def test_human_readable_size_invalid_params(self):
        with pytest.raises(AssertionError, match='units must be a non-empty list'):
            __([], 0, 0, 1)
        
        with pytest.raises(AssertionError, match='size_num must be a non-negative integer'):
            __(self.units, -1, 0, 1)
        
        with pytest.raises(AssertionError, match='min_unit must be less or equal than max_unit'):
            __(self.units, 0, 1, 0)

    def test_human_readable_size(self):
        assert __(self.units, 0, 0, 1) == ([(0, 'B')], 0)
        assert __(self.units, 1, 0, 1) == ([(1, 'B')], 0)
        assert __(self.units, 1024, 0, 1) == ([(1, 'KB')], 0)
        assert __(self.units, 1024 * 1024, 0, 2) == ([(1, 'MB')], 0)
        assert __(self.units, 1024 * 1024 * 1024, 0, 3) == ([(1, 'GB')], 0)
        assert __(self.units, 1024 * 1024 * 1024 * 1024, 0, 4) == ([(1, 'TB')], 0)
        assert __(self.units, 1024 * 1024 * 1024 * 1024 * 1024, 0, 5) == ([(1, 'PB')], 0)
    
    def test_human_readable_size_remainder(self):
        assert __(self.units, 1024 * 1024 * 1024 + 500, 1, 3) == ([(1, 'GB')], 500)
        assert __(self.units, 1024 * 1024 * 1024 + 1024, 2, 3) == ([(1, 'GB')], 1024)
        assert __(self.units, 1024 * 1024 * 1024 +  1024 * 1024, 3, 3) == ([(1, 'GB')], 1024 * 1024)
        assert __(self.units, 2**0, 2, 5) == ([(0, 'MB')], 1)
        assert __(self.units, 2**10, 2, 5) == ([(0, 'MB')], 2**10)
        assert __(self.units, 2**20 + 2 ** 10 * 1022, 2, 5) == ([(1, 'MB')], 2 ** 10 * 1022)
        assert __(self.units, 2**20 * 511 + 2 ** 10 * 1022, 2, 5) == ([(511, 'MB')], 2 ** 10 * 1022)
        assert __(self.units, 2 ** 30 + 2**20 * 511 + 2 ** 10 * 1022, 2, 5) == ([(1, 'GB'), (511, 'MB')], 2 ** 10 * 1022)
        assert __(self.units, 2 ** 30 * 100 + 2**20 * 511 + 2 ** 10 * 1022, 2, 5) == ([(100, 'GB'), (511, 'MB')], 2 ** 10 * 1022)

    def test_human_readable_size_calc_once(self):
        assert __(self.units, 2 ** 30 * 100 + 2**20 * 511 + 2 ** 10 * 1022, 2, 5, calc_once=True) == ([(100, 'GB')], 2**20 * 511 + 2 ** 10 * 1022)