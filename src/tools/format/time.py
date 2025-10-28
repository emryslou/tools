from enum import Enum
from .util import __

__units = [
    ('秒', 1),
    ('分', 60),
    ('小时', 60 * 60),
    ('天', 60 * 60 * 24),
    ('月', 60 * 60 * 24 * 30.44),
    ('年', 60 * 60 * 24 * 365),
]

__units_perf = [(__unit[0], __unit[1] * 10 ** 6) for __unit in __units[::-1]]
__units_perf.extend([('毫秒', 1_000), ('微秒', 1)])
__units_perf.reverse()

class UnitName(Enum):
    SECOND = 0
    MINUTE = 1
    HOUR = 2
    DAY = 3
    MONTH = 4
    YEAR = 5

class UnitNamePerf(Enum):
    MICROSECOND = 0
    MILLISECOND = 1
    SECOND = 2
    MINUTE = 3
    HOUR = 4
    DAY = 5
    MONTH = 6
    YEAR = 7


def format_time_multi_units(during_times: int, unit: UnitName = UnitName.YEAR) -> str:
    """Format time in seconds to a human readable string."""
    result, _ = __(__units, during_times, 0, int(unit.value))
    return ', '.join(f'{value} {unit}' for value, unit in result)


def format_time_perf_multi_units(during_times: int, unit: UnitNamePerf = UnitNamePerf.YEAR) -> str:
    """Format time in seconds to a human readable string."""
    result, _ = __(__units_perf, during_times, 0, int(unit.value))
    return ', '.join(f'{value} {unit}' for value, unit in result)





