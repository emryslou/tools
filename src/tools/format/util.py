
def __(
        units: list[tuple[str, int]], size_num: int,
        min_unit: int, max_unit: int,
        calc_once: bool = False
    ) -> tuple[list[(int, str)], int]:
    """
    Format a size number to a human-readable string with multiple units.

    Args:
        units (list[tuple[str, int]]): A list of unit tuples, where each tuple contains the unit name (str) and the divisor (int).
        size_num (int): The size number to be formatted.
        min_unit (int): The index of the minimum unit to be included in the result.
        max_unit (int): The index of the maximum unit to be included in the result.
        precision (int, optional): The number of decimal places to round the values. Defaults to 3.

    Returns:
        list[str]: A list of formatted size strings, where each string contains the value and the unit.

    Raises:
        AssertionError: If min_unit is greater than max_unit.
    """
    assert size_num >= 0, 'size_num must be a non-negative integer'
    assert units, 'units must be a non-empty list'
    assert min_unit <= max_unit, 'min_unit must be less or equal than max_unit'
    result, remainder_size_num = [], 0
    
    if size_num < units[min_unit][1]:
        result.append((0, units[min_unit][0]))

    units = units[min_unit:max_unit + 1]
    units.reverse()
    for unit, divisor in units:
        value, size_num = divmod(size_num, divisor)
        remainder_size_num = size_num
        if value > 0:
            result.append((int(value), unit))
            if calc_once:
                break
         
    return (result, remainder_size_num)
