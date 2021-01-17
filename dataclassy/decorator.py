"""
 Copyright (C) 2020 biqqles.
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This file contains code relating to dataclassy's decorator.
"""
from typing import Dict, Optional, Type
from .dataclass import DataClass, DataClassMeta


def dataclass(cls: Optional[type] = None, *, meta=DataClassMeta, **options) -> Type[DataClass]:
    """The decorator used to apply DataClassMeta, or optionally a subclass of that metaclass, to a class."""
    assert issubclass(meta, DataClassMeta)

    def apply_metaclass(to_class, metaclass=meta):
        """Apply a metaclass to a class."""
        dict_ = dict(vars(to_class), __metaclass__=metaclass)
        return metaclass(to_class.__name__, to_class.__bases__, dict_, **options)

    if cls:  # if decorator used with no arguments, apply metaclass to the class immediately
        if not isinstance(cls, type):
            raise TypeError('This decorator must be applied to a class')
        return apply_metaclass(cls)
    return apply_metaclass  # otherwise, return function for later evaluation


def make_dataclass(name: str, fields: Dict, defaults: Dict, bases=(), **options) -> Type[DataClass]:
    """Dynamically create a data class with name `name`, fields `fields`, default field values `defaults` and
    inheriting from `bases`."""
    return dataclass(type(name, bases, dict(defaults, __annotations__=fields)), **options)
