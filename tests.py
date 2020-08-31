"""
 Copyright (C) 2020 biqqles.
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This file contains tests for dataclassy.
"""
from typing import Dict, List, Tuple
import unittest
from collections import namedtuple
from inspect import signature
from sys import getsizeof

from dataclassy import dataclass, as_dict, as_tuple, make_dataclass, fields, Internal, replace


class Tests(unittest.TestCase):
    def setUp(self):
        """Define and initialise some data classes."""
        @dataclass(slots=True)
        class Alpha:
            a: int
            b: int = 2
            c: int

        class Beta(Alpha):
            d: int = 4
            e: Internal[Dict] = {}
            f: int

        @dataclass(slots=False, iter=True)  # test option inheritance and overriding
        class Gamma(Beta):
            pass

        @dataclass  # same fields as Beta but without inheritance or slots
        class Delta:
            a: int
            b: int = 2
            c: int
            d: int = 4
            e: Internal[Dict] = {}
            f: str

        NT = namedtuple('NT', 'x y z')

        @dataclass  # a complex (nested) class
        class Epsilon:
            g: Tuple[NT]
            h: List['Epsilon']
            _i: int = 0

        self.Alpha, self.Beta, self.Gamma, self.Delta, self.Epsilon = Alpha, Beta, Gamma, Delta, Epsilon
        self.NT = NT
        self.b = self.Beta(1, 2, 3)
        self.e = self.Epsilon((self.NT(1, 2, 3)), [self.Epsilon(4, 5, 6)])

    def test_decorator_options(self):
        """Test decorator options are inherited and overridden correctly."""
        self.assertTrue(self.Beta.__dataclass__['slots'])
        self.assertFalse(self.Delta.__dataclass__['slots'])

    def test_invalid_decorator_use(self):
        """Test invalid use of the decorator."""
        with self.assertRaises(TypeError):
            dataclass(1)

    def test_readme(self):
        """Test all examples from the project readme."""
        @dataclass  # with default parameters
        class Pet:
            name: str
            age: int
            species: str
            foods: List[str] = []
            SOME_CONSTANT = 232

        self.assertEqual(str(signature(Pet)), '(name: str, age: int, species: str, foods: List[str] = [])')

    def test_init(self):
        """Test correct generation of an __init__ method."""
        self.assertEqual(
            str(signature(self.Beta)),
            "(a: int, c: int, f: int, b: int = 2, d: int = 4, e: dataclassy.dataclass.Internal[typing.Dict] = {})")

    def test_repr(self):
        """Test correct generation of a __repr__ method."""
        self.assertEqual(repr(self.b), "Beta(a=1, b=2, c=2, d=4, f=3)")

    def test_iter(self):
        """Test correct generation of an __iter__ method."""
        iterable = self.Gamma(0, 1, [2, 3])
        a, b, *_, f = iterable
        self.assertEqual(a, 0)
        self.assertEqual(b, 2)
        self.assertEqual(f, [2, 3])

    def test_eq(self):
        """Test correct generation of an __eq__ method."""
        self.assertEqual(self.b, self.b)
        unequal_b = self.Beta(10, 20, 30)
        self.assertNotEqual(self.b, unequal_b)
        self.assertNotEqual(self.b, [0])  # test comparisons with non-dataclasses

    def test_slots(self):
        """Test correct generation and efficacy of a __slots__ attribute."""
        self.assertTrue(hasattr(self.b, '__slots__'))
        self.assertFalse(hasattr(self.b, '__dict__'))
        e = self.Epsilon(1, 2, 3)
        self.assertGreater(getsizeof(e) + getsizeof(e.__dict__), getsizeof(self.b))

    def test_frozen(self):
        """Test correct generation of __setattr__ and __delattr__ for a frozen class."""
        @dataclass(frozen=True)
        class Frozen:
            a: int
            b: int

        f = Frozen(1, 2)
        with self.assertRaises(AttributeError):
            f.a = 3
        with self.assertRaises(AttributeError):
            del f.b

    def test_empty_dataclass(self):
        """Test data classes with no fields and data classes with only class fields."""
        @dataclass
        class Empty:
            pass

        @dataclass(kwargs=False)
        class ClassVarOnly:
            class_var = 0

        self.assertEqual(str(signature(ClassVarOnly)), "()")

    def test_mutable_defaults(self):
        """Test mutable defaults are copied and not mutated between instances."""
        @dataclass
        class MutableDefault:
            mutable: List[int] = []

        a = MutableDefault()
        a.mutable.append(2)
        b = MutableDefault()
        b.mutable.append(3)
        c = MutableDefault(4)  # incorrect types should still be OK (shouldn't try to call copy)
        self.assertEqual(a.mutable, [2])
        self.assertEqual(b.mutable, [3])
        self.assertEqual(c.mutable, 4)

    def test_custom_init(self):
        """Test user-defined __init__ used for post-initialisation logic."""
        @dataclass
        class CustomInit:
            a: int
            b: int

            def __init__(self, a, b, c):
                self.d = (self.a + self.b) / c

        custom = CustomInit(1, 2, 3)
        self.assertEqual(custom.d, 1.0)

        @dataclass
        class CustomInitKwargs:
            a: int
            b: int

            def __init__(self, *args, **kwargs):
                self.c = kwargs

        custom_kwargs = CustomInitKwargs(1, 2, c=3)
        self.assertEqual(custom_kwargs.c, {'c': 3})

    def test_fields(self):
        """Test fields()."""
        self.assertEqual(repr(fields(self.e)), "{'g': NT(x=1, y=2, z=3), 'h': [Epsilon(g=4, h=5)]}")
        self.assertEqual(repr(fields(self.e, True)), "{'g': NT(x=1, y=2, z=3), 'h': [Epsilon(g=4, h=5)], '_i': 0}")

    def test_as_tuple(self):
        """Test as_tuple()."""
        self.assertEqual(as_tuple(self.e), ((1, 2, 3), [(4, 5, 6)], 0))

    def test_as_dict(self):
        """Test as_dict()."""
        self.assertEqual(as_dict(self.e), {'g': {'x': 1, 'y': 2, 'z': 3}, 'h': [{'g': 4, 'h': 5, '_i': 6}], '_i': 0})

    def test_make_dataclass(self):
        """Test functional creation of a data class using make_dataclass."""
        dynamic = make_dataclass('Dynamic', dict(name=str), {})
        dynamic(name='Dynamic')

    def test_replace(self):
        """Test replace()."""
        self.assertEqual(replace(self.b, f=4), self.Beta(1, 2, 4))
        self.assertEqual(self.b, self.Beta(1, 2, 3))  # assert that the original instance remains unchanged


if __name__ == '__main__':
    unittest.main()
