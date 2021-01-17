"""
Benchmarks for dataclassy.
Example output:

 === Simple class ===
dataclasses: 0.22464673200738616 seconds
dataclassy: 0.2270237009797711 seconds
dataclassy (slots): 0.1814715740038082 seconds

 === Default value ===
dataclasses: 0.2395797820063308 seconds
dataclassy: 0.25323228500201367 seconds
dataclassy (slots): 0.20265625597676262 seconds
"""
from typing import Dict
from timeit import timeit
import dataclasses
import dataclassy


def heading(text: str, decoration: str = '==='):
    """Print a heading."""
    print('\n', decoration, text, decoration)


def result(label: str, expression: str):
    """Time an expression and print the result, along with a label."""
    timing = timeit(expression, globals=globals())
    print(f'{label}: {timing} seconds')


heading('Simple class')


@dataclasses.dataclass
class DsSimple:
    a: int
    b: int


@dataclassy.dataclass
class DySimple:
    a: int
    b: int


@dataclassy.dataclass(slots=True)
class DySimpleSlots:
    a: int
    b: int


result('dataclasses', 'DsSimple(1, 2)')
result('dataclassy', 'DySimple(1, 2)')
result('dataclassy (slots)', 'DySimpleSlots(1, 2)')


heading('Default value')


@dataclasses.dataclass
class DsDefault:
    c: Dict = dataclasses.field(default_factory=dict)


@dataclassy.dataclass
class DyDefault:
    c: Dict = {}


@dataclassy.dataclass(slots=True)
class DyDefaultSlots:
    c: Dict = {}


result('dataclasses', 'DsDefault()')
result('dataclassy', 'DyDefault()')
result('dataclassy (slots)', 'DyDefaultSlots()')
