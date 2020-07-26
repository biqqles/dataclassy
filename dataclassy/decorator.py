"""
 Copyright (C) 2020 biqqles.
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This file contains code relating to dataclassy's decorator.
"""
from typing import Any, Dict, Optional
from .dataclass import DataClassMeta


def dataclass(cls: Optional[type] = None, **options):
    """The decorator used to apply DataClassMeta to a class."""
    def apply_metaclass(to_class, metaclass=DataClassMeta):
        """Apply a metaclass to a class."""
        dict_ = dict(vars(to_class), __metaclass__=metaclass)
        return metaclass(to_class.__name__, to_class.__bases__, dict_, **options)

    if cls:  # if decorator used with no arguments, apply metaclass to the class immediately
        if not isinstance(cls, type):
            raise TypeError('This decorator takes no positional arguments')
        return apply_metaclass(cls)
    return apply_metaclass  # otherwise, return function for later evaluation


def make_dataclass(name: str, fields: Dict[str, type], defaults: Dict[str, Any], bases=(), **options) -> type:
    """Dynamically create a data class with name `name`, fields `fields`, default field values `defaults` and
    inheriting from `bases`."""
    return dataclass(type(name, bases, dict(defaults, __annotations__=fields)), **options)
