# dataclassy
**dataclassy** is a reimplementation of data classes in Python - an alternative to the built-in [dataclasses module](https://docs.python.org/3/library/dataclasses.html) that avoids many of its [common](https://stackoverflow.com/q/51575931) [pitfalls](https://stackoverflow.com/q/50180735). dataclassy is designed to be more flexible, less verbose, and more powerful than dataclasses, while retaining a familiar interface.

### Why use dataclassy?
Data classes from **dataclassy** offer the following advantages over those from **dataclasses**:

- Friendly inheritance:
    - No need to apply a decorator to each subclass - just once and all following classes will also be data classes
    - Complete freedom in field ordering - no headaches if a field with a default value follows a field without one 
- Optional generation of:
    - `__slots__`, significantly improving memory efficiency and lookup performance
    - `**kwargs`, simplifying dataclass instantiation from dictionaries
    - An `__iter__` method, enabling data class destructuring
- Internal fields (marked with `_` or `__`) are excluded from `__repr__` by default

In addition, dataclassy:

- Is pure Python, with zero dependencies
- Supports Python 3.6 and up

All in a tidy codebase that's a fraction of the size of Python's dataclasses!

## Usage
### Installation
Install the latest stable version from PyPI with pip:

```sh
pip install dataclassy
```


Or install the latest development version straight from this repository:

```sh
pip install https://github.com/biqqles/dataclassy/archive/master.zip -U
```


### Migration
For basic applications, it is possible to instantly migrate from dataclasses to dataclassy by simply changing

```Python
from dataclasses import dataclass
```

to

```Python
from dataclassy import dataclass
```

dataclassy also includes aliases for its functions - `asdict` for [`as_dict`](#as_dictdataclass-dict_factorydict), `astuple` for [`as_tuple`](#as_tupledataclass) and `make_dataclass` for [`create_dataclass`](#create_dataclassname-fields-defaults-bases) - to assist in migration from dataclasses.

## API
### Decorator
#### `dataclass(init=True, repr=True, eq=True, iter=False, frozen=False, kwargs=False, slots=False, hide_internals=True)`
The decorator used to signify that a class definition should become a data class. Usage is simple:

```Python
@dataclass  # with default parameters
class Pet:
    name: str
    age: int
    species: str
    foods: List[str] = []
    SOME_CONSTANT = 232
```

The decorator returns a new data class with generated methods as detailed below. If the class already defines a particular method, it will not be replaced with a generated one.

Without arguments, its behaviour is almost identical to its equivalent in the built-in module. However, dataclassy's decorator only needs to be applied once, and all subclasses will become data classes with the same parameters. The decorator can still be reapplied to subclasses in order to change parameters.

A data class' fields are defined using Python's type annotations syntax. Data classes can of course also contain methods.

As shown, class variables and constants are represented by the **absence** of type annotations.

#### Decorator parameters

> The term "field", as used in this section, refers to a class-level variable with a type annotation. For more information, see the documentation for [`fields()`](#fieldsdataclass-internalsfalse) below.

##### `init`
If true (the default), generate an [`__init__`](https://docs.python.org/3/reference/datamodel.html#object.__init__) method that has as parameters all fields up its inheritance chain. These are ordered in definition order, with all fields with default values placed towards the end, following all fields without them.

This is an important distinction from dataclasses, where all fields are simply ordered in definition order, and is what allows dataclassy's data classes to be far more flexible in terms of inheritance. 

You can verify the signature of the generated initialiser for any class using `signature` from the `inspect` module. For example, `print(inspect.signature(Pet))` will output `(name: str, age: int, species: str, foods: List[str] = [])`.

This generated `__init__` will assign its parameters to the fields of the new dataclass instance.

A shallow copy will be created for mutable arguments (defined as those defining a `copy` method). This means that default field values that are mutable (e.g. a list) will not be mutated between instances. For example, a copy of the list field `foods` of `Pet` will be created for each instance, meaning that appending to that attribute in one instance will not affect other instances.

##### `repr`
If true (the default), generate a [`__repr__`](https://docs.python.org/3/reference/datamodel.html#object.__repr__) method that displays all fields (or if `hide_internals` is true, all fields excluding internal ones) of the data class instance and their values.

##### `eq`
If true (the default), generate an [`__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__eq__) method that compares this data class to another as if they were tuples created by [`as_tuple`](#as_tupledataclass).

##### `iter`
If true, generate an [`__iter__`](https://docs.python.org/3/reference/datamodel.html#object.__iter__) method that returns the values of the class's fields, in order of definition. This can be used to destructure a data class instance, as with a Scala `case class` or a Python `namedtuple`.

##### `kwargs`
If true, add [`**kwargs`](https://docs.python.org/3.3/glossary.html#term-parameter) to the end of the parameter list for `__init__`. This simplifies data class intantiation from dictionaries that may have keys in addition to the fields of the dataclass (i.e. `SomeDataClass(**some_dict)`).

##### `slots`
If true, generate a [`__slots__`](https://docs.python.org/3/reference/datamodel.html#slots) attribute for the class. This reduces the memory footprint of instances and attribute lookup overhead. However, `__slots__` come with a few [restrictions](https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots) (for example, multiple inheritance becomes tricky) that you should be aware of.

##### `frozen`
If true, data class instances are nominally immutable: fields cannot be overwritten or deleted after initialisation in `__init__`. Attempting to do so will raise an `AttributeError`.

##### `hide_internals`
If true (the default), [internal fields](#internal) are not included in the generated `__repr__`.


### Functions
#### `is_dataclass(obj)`
Returns True if `obj` is a data class as implemented in this module.

#### `is_dataclass_instance(obj)`
Returns True if `obj` is an instance of a data class as implemented in this module.

#### `fields(dataclass, internals=False)`
Return a dict of `dataclass`'s fields and their values. `internals` selects whether to include internal fields.

A field is defined as a class-level variable with a [type annotation](https://docs.python.org/3/glossary.html#term-variable-annotation). This means that class variables and constants are not fields, assuming they do not have annotations as indicated above.

#### `as_dict(dataclass dict_factory=dict)`
Recursively create a dict of a dataclass instance's fields and their values.

This function is recursively called on data classes, named tuples and iterables.

#### `as_tuple(dataclass)`
Recursively create a tuple of the values of a dataclass instance's fields, in definition order.

This function is recursively called on data classes, named tuples and iterables.

#### `create_dataclass(name, fields, defaults, bases=())`
Dynamically create a data class with name `name`, fields `fields`, default field values `defaults` and inheriting from `bases`.

### Type hints
#### Internal
The `Internal` type wrapper marks a field as being "internal" to the data class. Fields which begin with the ["internal use"](https://www.python.org/dev/peps/pep-0008/#descriptive-naming-styles) idiomatic indicator `_` or the [private field](https://docs.python.org/3/tutorial/classes.html#private-variables) interpreter indicator `__` are automatically treated as internal fields.  The `Internal` type wrapper therefore serves as an alternative method of indicating that a field is internal for situations where you are unable to name your fields in this way.

#### DataClass
Use this type hint to indicate that a variable, parameter or field should be a generic data class instance. For example, dataclassy uses these in the signatures of `as_dict`, `as_tuple` and `fields` to show that these functions should be called on data class instances


### To be added
- An equivalent for `__post_init__`