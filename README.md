# dataclassy
**dataclassy** is a reimplementation of data classes in Python — an alternative to the built-in [dataclasses module](https://docs.python.org/3/library/dataclasses.html) that avoids many of [its](https://stackoverflow.com/questions/54678337) [common](https://stackoverflow.com/q/51575931) [pitfalls](https://stackoverflow.com/q/50180735). dataclassy is designed to be more flexible, less verbose, and more powerful than dataclasses, while retaining a familiar interface.

### What are data classes?
Simply put, data classes are classes optimised for storing data. In this sense they are similar to record or struct types in other languages. However, Python's data classes can also have methods, making them more reminiscent of Scala's [case classes](https://docs.scala-lang.org/tour/case-classes.html). In Python, data classes take the form of a decorator which, when applied to a class, automatically generates methods to set the class's fields from arguments to its constructor, represent it as a string, and more.

### Why use dataclassy?
Data classes from **dataclassy** offer the following advantages over those from **dataclasses**:

- Cleaner code: no messy `InitVar`, `ClassVar`, `field` or `__post_init__`
- Friendly inheritance:
    - No need to apply a decorator to each and every subclass - just once and all following classes will also be data classes
    - Complete freedom in field ordering - no headaches if a field with a default value follows a field without one
- Optional generation of:
    - `__slots__`, significantly improving memory efficiency and lookup performance
    - `**kwargs`, simplifying dataclass instantiation from dictionaries
    - An `__iter__` method, enabling data class destructuring
- Internal fields (marked with `_` or `__`) are excluded from `__repr__` by default

In addition, dataclassy:

- Has no dependencies
- Supports Python 3.6 and up
- Has 100% test coverage

All in a tiny, tidy codebase that's a fraction of the size of Python's dataclasses or other alternatives like attrs.

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
For simple use cases it is possible to instantly migrate from dataclasses to dataclassy by simply changing

```Python
from dataclasses import dataclass
```

to

```Python
from dataclassy import dataclass
```

dataclassy [implements](#functions) all of dataclasses' functions, and it also includes aliases for the functions [`as_dict`](#as_dictdataclass-dict_factorydict) (`asdict`) and [`as_tuple`](#as_tupledataclass) (`astuple`) to assist in migration from dataclasses. Constructs from dataclasses like `field`, `InitVar` and `__post_init__` are not supported nor required in dataclassy because it uses Python's built-in syntactic features to accomplish the same things.


### Examples
#### The basics
To define a data class, simply apply the `@dataclass` decorator to a class definition:

```Python
@dataclass  # with default parameters
class Pet:
    name: str
    age: int
    species: str
    foods: List[str] = []
    fluffy: bool
```

Without arguments to the decorator, the resulting class will behave very similarly to its equivalent from the built-in module. However, dataclassy's decorator has some additional options over dataclasses', and it is also inherited so that subclasses of data classes are automatically data classes too.

The decorator generates various methods for the class. Which ones exactly depend on the options to the decorator. For example, `@dataclass(repr=False)` will prevent a `__repr__` method from being generated. `@dataclass` is equivalent to using the decorator with default parameters (i.e. `@dataclass` and `@dataclass()` are equivalent). Options to the decorator are detailed fully in the [next section](#decorator-options).

You can exclude a class attribute from dataclassy's mechanisms entirely by simply defining it without a type annotation. This can be used for class variables and constants.

#### Default values
Default values for fields work exactly as default arguments to functions (and in fact this is how they are implemented), with one difference: for mutable defaults, a copy is automatically created for each class instance. This means that a new copy of the `list` field `foods` in `Pet` above will be created each time it is instantiated, so that appending to that attribute in one instance will not affect other instances.

#### Inheritance
Unlike dataclasses, dataclassy's decorator only needs to be applied once, and all subclasses will become data classes with the same options as the parent class. The decorator can still be reapplied to subclasses in order to apply new parameters.

To change the type, or to add or change the default value of a field in a subclass, simply redeclare it in the subclass.

#### Post-initialisation logic

You can define custom post-initialisation logic (such as calculating new fields based on the value of others) by defining an `__init__` method. This works because dataclassy uses `__new__` to set the attributes of the class before `__init__` is called. This is demonstrated in the following example:

```Python
@dataclass
class CustomInit:
    a: int
    b: int
    
    def __init__(self, a, b, c):
        self.d = (self.a + self.b) / c
```

When this class is instantiated with `CustomInit(1, 2, 3)`, it gets a new instance attribute `d` which is calculated using the value of the `__init__`-only parameter `c`.

When defining an `__init__`, you *must* ensure that the signature includes, in order, all fields of the class in addition to your init-only parameters, either by explicitly listing them as shown, or by using `*args` and/or `**kwargs` (e.g. `def __init__(self, *args, c)`. Note however that this syntax makes `c` a  *keyword-only argument*). This prevents ambiguity when initialising the class. Python will enforce this by raising a `RuntimeError` if you do not.

This mechanism performs the roles of dataclasses' `InitVar` and `__post_init__`.

## API
### Decorator
#### `@dataclass(init=True, repr=True, eq=True, iter=False, frozen=False, kwargs=False, slots=False, hide_internals=True)`
The decorator used to signify that a class definition should become a data class. The decorator returns a new data class with generated methods as detailed below. If the class already defines a particular method, it will not be replaced with a generated one.

Without arguments, its behaviour is, superficially, almost identical to its equivalent in the built-in module. However, dataclassy's decorator only needs to be applied once, and all subclasses will become data classes with the same parameters. The decorator can still be reapplied to subclasses in order to change parameters.

A data class' fields are defined using Python's type annotations syntax. To change the type or default value of a field in a subclass, simply redeclare it.

This decorator takes advantage of two equally important features added in Python 3.6: [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation) and [dictionaries being ordered](https://docs.python.org/3.7/tutorial/datastructures.html#dictionaries). (The latter is technically an [implementation detail](https://docs.python.org/3.6/whatsnew/3.6.html#whatsnew36-compactdict) of Python 3.6, only becoming standardised in Python 3.7, but is the case for all current implementations of Python 3.6, i.e. CPython and PyPy.)

#### Decorator options

> The term "field", as used in this section, refers to a class-level variable with a type annotation. For more information, see the documentation for [`fields()`](#fieldsdataclass-internalsfalse) below.

##### `init`
If true (the default), generate a [`__new__`](https://docs.python.org/3/reference/datamodel.html#object.__new__) method that has as parameters all fields up its inheritance chain. These are ordered in definition order, with all fields with default values placed towards the end, following all fields without them. The method initialises the class by applying these parameters to the class as attributes.

This ordering is an important distinction from dataclasses, where all fields are simply ordered in definition order, and is what allows dataclassy's data classes to be far more flexible in terms of inheritance. 

You can verify the signature of the generated initialiser for any class using `signature` from the `inspect` module. For example, `print(inspect.signature(Pet))` will output `(name: str, age: int, species: str, foods: List[str] = [])`.

A shallow copy will be created for mutable arguments (defined as those defining a `copy` method). This means that default field values that are mutable (e.g. a list) will not be mutated between instances.

##### `repr`
If true (the default), generate a [`__repr__`](https://docs.python.org/3/reference/datamodel.html#object.__repr__) method that displays all fields (or if `hide_internals` is true, all fields excluding internal ones) of the data class instance and their values.

##### `eq`
If true (the default), generate an [`__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__eq__) method that compares this data class to another as if they were tuples created by [`as_tuple`](#as_tupledataclass).

##### `iter`
If true, generate an [`__iter__`](https://docs.python.org/3/reference/datamodel.html#object.__iter__) method that returns the values of the class's fields, in order of definition. This can be used to destructure a data class instance, as with a Scala `case class` or a Python `namedtuple`.

##### `kwargs`
If true, add [`**kwargs`](https://docs.python.org/3.3/glossary.html#term-parameter) to the end of the parameter list for `__init__`. This simplifies data class instantiation from dictionaries that may have keys in addition to the fields of the dataclass (i.e. `SomeDataClass(**some_dict)`).

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

#### `make_dataclass(name, fields, defaults, bases=(), **options)`
Dynamically create a data class with name `name`, fields `fields`, default field values `defaults` and inheriting from `bases`.

#### `replace(dataclass, **changes)`
Return a new copy of `dataclass` with field values replaced as specified in `changes`.

### Type hints
#### Internal
The `Internal` type wrapper marks a field as being "internal" to the data class. Fields which begin with the ["internal use"](https://www.python.org/dev/peps/pep-0008/#descriptive-naming-styles) idiomatic indicator `_` or the [private field](https://docs.python.org/3/tutorial/classes.html#private-variables) interpreter indicator `__` are automatically treated as internal fields.  The `Internal` type wrapper therefore serves as an alternative method of indicating that a field is internal for situations where you are unable to name your fields in this way.

#### DataClass
Use this type hint to indicate that a variable, parameter or field should be a generic data class instance. For example, dataclassy uses these in the signatures of `as_dict`, `as_tuple` and `fields` to show that these functions should be called on data class instances.


### To be added
- The missing decorator options from dataclasses: `order=False` and `unsafe_hash=False`.
