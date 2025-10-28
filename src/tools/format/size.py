from enum import Enum
from .util import __

__units_name_and_divisor = [
    ('B',  2 ** 0),
    ('KB', 2 ** 10),
    ('MB', 2 ** 20),
    ('GB', 2 ** 30),
    ('TB', 2 ** 40),
    ('PB', 2 ** 50),
    ('EB', 2 ** 60),
    ('ZB', 2 ** 70),
    ('YB', 2 ** 80),
]

__units_map_name_to_divisor = {name: divisor for name, divisor in __units_name_and_divisor}

__UNITS_SIZE = len(__units_name_and_divisor)

class UnitName(Enum):
    B = 0
    KB = 1
    MB = 2
    GB = 3
    TB = 4
    PB = 5
    EB = 6
    ZB = 7
    YB = 8



def format_size_multi_units(bytes: int, min_unit: UnitName = UnitName.B, max_unit: UnitName = UnitName.YB) -> str:
    """Format size in bytes to a human readable string."""
    assert min_unit.value < max_unit.value, 'min_unit must be less than max_unit'
    result, _ = __(__units_name_and_divisor, bytes, int(min_unit.value), int(max_unit.value))
    return ', '.join(f'{value} {unit}' for value, unit in result)


def format_size(bytes: int, precision: int = 3) -> str:
    """Format size in bytes to a human readable string."""
    assert precision > 0, 'precision must be greater than 0'
    result, remainder = __(__units_name_and_divisor, bytes, UnitName.B.value, UnitName.YB.value, calc_once=True)

    result_value, result_unit = result[0] if len(result) > 0 else (0, UnitName.B.name)
    if remainder > 0:
        result_value += (remainder / __units_map_name_to_divisor[result_unit])
        return f'{result_value:.{precision}f} {result_unit}'
    else:
        return f'{result_value} {result_unit}'
