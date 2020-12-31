"""
 Copyright (C) 2020 biqqles.
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This file contains the internal mechanism that makes data classes
 work, as well as functions which operate on them.
"""
from types import FunctionType as Function
from typing import Any, Dict, Generic, Hashable, TypeVar

DataClass = Any  # type hint for variables that should be data class instances
T = TypeVar('T')


class Internal(Generic[T]):
    """This type hint wrapper represents a field that is internal to the data class and is, for example, not to be
    shown in a repr."""
    @classmethod
    def is_internal(cls, annotation):
        return getattr(annotation, '__origin__', None) is cls or \
               (type(annotation) is str and cls.__name__ in annotation)


class DataClassMeta(type):
    """The metaclass for a data class."""
    DEFAULT_OPTIONS = dict(init=True, repr=True, eq=True, iter=False, frozen=False, kwargs=False, slots=False,
                           order=False, unsafe_hash=True, hide_internals=True)

    def __new__(mcs, name, bases, dict_, **kwargs):
        # collect annotations, defaults, slots and options from this class' ancestors, in definition order
        all_annotations = {}
        all_defaults = {}
        all_slots = set()
        options = dict(mcs.DEFAULT_OPTIONS)

        dataclass_bases = [vars(b) for b in bases if hasattr(b, '__dataclass__')]
        for b in dataclass_bases + [dict_]:
            all_annotations.update(b.get('__annotations__', {}))
            all_defaults.update(b.get('__defaults__', dict_))
            all_slots.update(b.get('__slots__', set()))
            options.update(b.get('__dataclass__', {}))
        options.update(kwargs)

        # fill out this class' dict and store defaults, annotations and decorator options for future subclasses
        dict_.update(all_defaults)
        dict_['__defaults__'] = all_defaults
        dict_['__annotations__'] = all_annotations
        dict_['__dataclass__'] = options

        # delete what will become stale references so that Python creates new ones
        del dict_['__dict__'], dict_['__weakref__']

        # create/apply generated methods and attributes
        # TODO: neaten
        user_init = (not dataclass_bases and type(dict_.get('__init__')) is Function) or '__user_init__' in dict_

        if options['slots']:
            # values with default values must only be present in slots, not dict, otherwise Python will interpret them
            # as read only
            for d in all_annotations.keys() & all_defaults.keys():
                del dict_[d]
            dict_['__slots__'] = all_annotations.keys() - all_slots
        elif '__slots__' in dict_:
            # if the slots option has been removed from an inheriting dataclass we must remove descriptors and __slots__
            for d in all_annotations.keys() - all_defaults.keys() & dict_.keys():
                del dict_[d]
            del dict_['__slots__']

        if options['init'] and all_annotations:  # only generate __init__ if there are fields to set
            if user_init:
                dict_['__user_init__'] = dict_.pop('__init__')  # could also maybe use __post_init__ if not confusing
            print(name)
            dict_['__init__'] = _generate_init(all_annotations, all_defaults, user_init,
                                               options['kwargs'], options['frozen'])
        if options['repr']:
            from reprlib import recursive_repr
            dict_.setdefault('__repr__', recursive_repr(f'{name}(this)')(__repr__))
        if options['eq']:
            dict_.setdefault('__eq__', __eq__)
        if options['iter']:
            dict_.setdefault('__iter__', __iter__)
        if options['frozen']:
            dict_['__delattr__'] = dict_['__setattr__'] = __setattr__
        if options['order']:
            dict_.setdefault('__lt__', __lt__)
        if (options['eq'] and options['frozen']) or options['unsafe_hash']:
            dict_.setdefault('__hash__', __hash__)

        return type.__new__(mcs, name, bases, dict_)

    def __init__(cls, *args, **kwargs):
        # warn the user if they try to use __post_init__
        if hasattr(cls, '__post_init__'):
            raise TypeError('dataclassy does not use __post_init__. You should rename this method __init__')

        if cls.__dataclass__['eq'] and cls.__dataclass__['order']:
            from functools import total_ordering
            total_ordering(cls)

        # determine a static expression for an instance's fields as a tuple, then evaluate this to create a property
        # allowing efficient representation for internal methods
        tuple_expr = ', '.join((*(f'self.{f}' for f in fields(cls)), ''))  # '' ensures closing comma
        cls.__tuple__ = property(eval(f'lambda self: ({tuple_expr})'))


def _generate_init(annotations: Dict, defaults: Dict, user_init: bool, gen_kwargs: bool, frozen: bool) -> Function:
    """Generate and return a __new__ method for a data class which has as parameters all fields of the data class.
    When the data class is initialised, arguments to this function are applied to the fields of the new instance. Using
    __new__ frees up __init__, allowing it to be defined by the user to perform additional, custom initialisation.

    If __init__ is defined, all arguments to __new__ become keyword-only, and the custom __call__ converts positional
    arguments to keyword arguments. This prevents ambiguity during attempts to pass the same argument twice,
    positionally and as a keyword."""
    arguments = [a for a in annotations if a not in defaults]
    default_arguments = [f'{a}={a}' for a in annotations if a in defaults]
    args = ['*args'] if user_init else []
    kwargs = ['**kwargs'] if user_init or gen_kwargs else []

    parameters = ', '.join(arguments + default_arguments + args + kwargs)

    # determine what to do with arguments before assignment. If the argument matches a mutable default, make a copy
    references = {n: f'{n}.copy() if {n} is self.__defaults__[{n!r}] else {n}'  # todo or compare ids
                  if n in defaults and hasattr(defaults[n], 'copy') else n for n in annotations}

    # if the class is frozen, use the necessary but slightly slower object.__setattr__
    assignments = [f'object.__setattr__(self, {n!r}, {r})' if frozen else f'self.{n} = {r}'
                   for n, r in references.items()]

    call_user_init = ['self.__user_init__(*args, **kwargs)'] if user_init else []

    # generate the function
    lines = [f'def __init__(self, {parameters}):', *assignments, *call_user_init]

    exec('\n\t'.join(lines), {}, defaults)
    function = defaults.pop('__init__')
    function.__annotations__ = annotations
    return function


# generic method implementations common to all data classes
# these are currently relatively inefficient - it would be better to cache an expression for a class' tuple
from .functions import values, fields


def __eq__(self: DataClass, other: DataClass):
    return type(self) is type(other) and self.__tuple__ == other.__tuple__


def __lt__(self: DataClass, other: DataClass):
    if isinstance(other, type(self)):
        return self.__tuple__ < other.__tuple__
    return NotImplemented


def __hash__(self):
    # currently not ideal since gives no warning if a field expected to be hashable is not
    return hash((type(self), *(v for v in self.__tuple__ if v is isinstance(v, Hashable))))


def __iter__(self):
    return iter(self.__tuple__)


def __repr__(self):
    show_internals = not self.__dataclass__['hide_internals']
    field_values = ', '.join(f'{f}={v!r}' for f, v in values(self, show_internals).items())
    return f'{type(self).__name__}({field_values})'


def __setattr__(self, *args):
    raise AttributeError('Frozen class')
