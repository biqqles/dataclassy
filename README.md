# dataclassy
Your data classes just got an upgrade! **dataclassy** is a reimplementation of data classes in Python — an alternative to the built-in [dataclasses module](https://docs.python.org/3/library/dataclasses.html) that avoids many of [its](https://stackoverflow.com/questions/54678337) [common](https://stackoverflow.com/q/51575931) [pitfalls](https://stackoverflow.com/q/50180735). dataclassy is designed to be more flexible, less verbose, and more powerful than dataclasses, while retaining a familiar interface.

### What are data classes?
Simply put, data classes are classes optimised for storing data. In this sense they are similar to record or struct types in other languages. In Python, data classes take the form of a decorator which, when applied to a class, automatically generates methods to set the class's fields from arguments to its constructor, represent it as a string, and more.

### Why use dataclassy?
Data classes from **dataclassy** offer the following advantages over those from **dataclasses**:

- Cleaner code: no messy `InitVar`, `ClassVar`, `field` or `__post_init__`
- Beautiful post-init processing: just define an `__init__` as you would normally
- Friendly inheritance:
    - No need to apply a decorator to each and every subclass - just once and all following classes will also be data classes
    - Complete freedom in field ordering - no headaches if a field with a default value follows a field without one
- Optional generation of:
    - `__slots__`, significantly improving memory efficiency and lookup performance
    - `**kwargs`, simplifying dataclass instantiation from dictionaries
    - An `__iter__` method, enabling data class destructuring
- Internal fields (marked with `_` or `__`) are excluded from `__repr__` by default

Worried about performance? [Benchmarks](benchmarks.py) show:

- Performance is at least as good as dataclasses when `slots=False`
- You get an instant ~25% performance boost to initialisation when `slots=True`

In addition, dataclassy:

- Is tiny (around 150 lines of code)
- Has no dependencies
- Supports Python 3.6 and up
- Has 100% test coverage


## Usage
### Installation
Install the latest stable version from [PyPI](https://pypi.org/project/dataclassy/) with pip:

```sh
pip install dataclassy
```

Or install the latest development version straight from this repository:

```sh
pip install https://github.com/biqqles/dataclassy/archive/master.zip -U
```


### Migration
By and large, dataclassy is a drop-in replacement for dataclasses. If you simply use the decorator and other functions, it is possible to instantly migrate from dataclasses to dataclassy by simply changing

```Python
from dataclasses import dataclass
```

to

```Python
from dataclassy import dataclass
```

This being said, there *are* differences.  dataclassy does not try to be a "clone" of dataclasses, but rather an alternative, feature-complete implementation of the concept with its own design philosophy, yet one that remains highly familiar to those acquainted with the module in the standard library. Minimalism takes precedence over compatibility.

#### Similarities
dataclassy's `dataclass` decorator takes all of the same arguments as dataclasses', plus its own, and should therefore be a drop-in replacement.

dataclassy also implements all dataclasses' [functions](#functions): `is_dataclass`, `fields`, `replace`, `make_dataclass`, `asdict` and `astuple` (the last two are aliased from `as_dict` and `as_tuple` respectively), and they should work as you expect.

#### Differences
dataclassy has several important differences from dataclasses, mainly reflective of its minimalistic style and implementation. These differences are enumerated below and fully expanded on in the next section.

|                                 |dataclasses                                 |dataclassy                              |
|---------------------------------|:-------------------------------------------|:---------------------------------------|
|*post-initialisation processing* |`__post_init__` method                      |`__init__` method                       |
|*init-only variables*            |fields with type `InitVar`                  |arguments to `__init__`                 |
|*class variables*                |fields with type `ClassVar`                 |fields without type annotation          |
|*mutable defaults*               |`a: Dict = field(default_factory=dict)`     |`a: Dict = {}`                          |
|*field excluded from `repr`*     |`b: int = field(repr=False)`                |`Internal` type wrapper or `_name`      |
|*"late init" field*              |`c: int = field(init=False`)                |`c: int = None`                         |

There are a couple of minor differences, too:

- `fields` returns `Dict[str, Type]` instead of `Dict[Field, Type]` and has an additional parameter which filters internal fields
- Attempting to modify a frozen instance raises `AttributeError` with an explanation rather than `FrozenInstanceError`

Finally, there are some quality of life improvements that, while not being directly implicated in migration, will allow you to make your code cleaner:

- `@dataclass` does not need to be applied to every subclass - its behaviour and options are inherited
- Unlike dataclasses, fields with defaults do not need to follow those without them. This is particularly useful when working with subclasses, which is almost impossible with dataclasses
- dataclassy adds a `DataClass` type annotation to represent variables that should be generic data class instances
- dataclassy has the `is_dataclass_instance` suggested as a [recipe](https://docs.python.org/3/library/dataclasses.html#dataclasses.is_dataclass) for dataclasses built-in
- The generated comparison methods (when `order=True`) are compatible with supertypes and subtypes of the class. This means that heterogeneous collections of instances with the same superclass can be sorted

It is also worth noting that internally, dataclasses and dataclassy work in different ways. You can think of dataclassy as _turning your class into a different type of thing_ (indeed, it uses a metaclass) and dataclasses as _adding things to your class_ (it does not).


### Examples
#### The basics
To define a data class, simply apply the `@dataclass` decorator to a class definition:

```Python
from dataclassy import dataclass
from typing import List

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

#### Inheritance
Unlike dataclasses, dataclassy's decorator only needs to be applied once, and all subclasses will become data classes with the same options as the parent class. The decorator can still be reapplied to subclasses in order to apply new parameters.

To change the type, or to add or change the default value of a field in a subclass, simply redeclare it in the subclass.

#### Post-initialisation processing
If an initialiser is requested (`init=True`), dataclassy automatically sets the attributes of the class upon initialisation. You can define code that should run after this happens - this is called _post-init processing_.  

You can call the method that contains this logic one of two options:

- `__init__` - this originated back when dataclassy used `__new__` for initialisation. It is recommended if you are comfortable with "magic" - see the note about dataclassy turning a class into a different _thing_. From this point of view, a data class (in contrast to a regular class) happens to perform special logic before `__init__` is called. You must call `super().__post_init__` instead of `super().__init__` to prevent ambiguity.
- `__post_init__` - compatible with dataclasses. Will not be called if `init=False` (like dataclasses) or if the class has no fields.

This logic can include, for example, calculating new fields based on the values of others. This is demonstrated in the following example:

```Python
@dataclass
class CustomInit:
    a: int
    b: int
    
    def __init__(self):
        self.c = self.a / self.b
```

In this example, when the class is instantiated with `CustomInit(1, 2)`, the field `c` is calculated as `0.5`.

Like with any class, your `__init__` can also take parameters which exist only in the context of `__init__`. These can be used for arguments to the class that you do not want to store as fields. A parameter cannot have the name of a class field; this again is to prevent ambiguity.


#### Default values
Default values for fields work exactly as default arguments to functions (and in fact this is how they are implemented), with one difference: for copyable defaults, a copy is automatically created for each class instance. This means that a new copy of the `list` field `foods` in `Pet` above will be created each time it is instantiated, so that appending to that attribute in one instance will not affect other instances. A "copyable default" is defined as any object implementing a `copy` method, which includes all the built-in mutable collections (including `defaultdict`).

If you want to create new instances of objects which do not have a copy method, do so in `__init__`:

```Python
@dataclass
class CustomInit2:
    m: MyClass = None
    
    def __init__(self):
        self.m = MyClass()
```


## API
### Decorator
#### `@dataclass(init=True, repr=True, eq=True, iter=False, frozen=False, kwargs=False, slots=False, hide_internals=True, meta=DataClassMeta)`
The decorator used to signify that a class definition should become a data class. The decorator returns a new data class with generated methods as detailed below. If the class already defines a particular method, it will not be replaced with a generated one.

Without arguments, its behaviour is, superficially, almost identical to its equivalent in the built-in module. However, dataclassy's decorator only needs to be applied once, and all subclasses will become data classes with the same parameters. The decorator can still be reapplied to subclasses in order to change parameters.

A data class' fields are defined using Python's type annotations syntax. To change the type or default value of a field in a subclass, simply redeclare it.

This decorator takes advantage of two equally important features added in Python 3.6: [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation) and [dictionaries being ordered](https://docs.python.org/3.7/tutorial/datastructures.html#dictionaries). (The latter is technically an [implementation detail](https://docs.python.org/3.6/whatsnew/3.6.html#whatsnew36-compactdict) of Python 3.6, only becoming standardised in Python 3.7, but is the case for all current implementations of Python 3.6, i.e. CPython and PyPy.)

#### Decorator options

> The term "field", as used in this section, refers to a class-level variable with a type annotation. For more information, see the documentation for [`fields()`](#fieldsdataclass-internalsfalse) below.

##### `init`
If true (the default), generate an [`__init__`](https://docs.python.org/3/reference/datamodel.html#object.__init__) method that has as parameters all fields up its inheritance chain. These are ordered in definition order, with all fields with default values placed towards the end, following all fields without them. The method initialises the class by applying these parameters to the class as attributes.

This ordering is an important distinction from dataclasses, where all fields are simply ordered in definition order, and is what allows dataclassy's data classes to be far more flexible in terms of inheritance. 

You can verify the signature of the generated initialiser for any class using `signature` from the `inspect` module. For example, `print(inspect.signature(Pet))` will output `(name: str, age: int, species: str, foods: List[str] = [])`.

A shallow copy will be created for mutable arguments (defined as those defining a `copy` method). This means that default field values that are mutable (e.g. a list) will not be mutated between instances.

##### `repr`
If true (the default), generate a [`__repr__`](https://docs.python.org/3/reference/datamodel.html#object.__repr__) method that displays all fields (or if `hide_internals` is true, all fields excluding internal ones) of the data class instance and their values.

##### `eq`
If true (the default), generate an [`__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__eq__) method that compares this data class to another of the same type as if they were tuples created by [`as_tuple`](#as_tupledataclass).

##### `frozen`
If true, instances are nominally immutable: fields cannot be overwritten or deleted after initialisation in `__init__`. Attempting to do so will raise an `AttributeError`. **Warning: incurs a significant initialisation performance penalty.**

##### `unsafe_hash`
If true, force the generation of a [`__hash__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__) method that attempts to hash the class as if it were a tuple of its hashable fields. If `unsafe_hash` is false, `__hash__` will only be generated if `eq` and `frozen` are both true.

##### `order`
If true, a [`__lt__`](https://docs.python.org/3/reference/datamodel.html#object.__lt__) method is generated, making the class *orderable*. If `eq` is also true, all other comparison methods are also generated. These methods compare this data class to another of the same type (or a subclass) as if they were tuples created by [`as_tuple`](#as_tupledataclass). The normal rules of [lexicographical comparison](https://docs.python.org/3/reference/expressions.html#value-comparisons) apply.

##### `iter`
If true, generate an [`__iter__`](https://docs.python.org/3/reference/datamodel.html#object.__iter__) method that returns the values of the class's fields, in order of definition. This can be used to destructure a data class instance, as with a Scala `case class` or a Python `namedtuple`.

##### `kwargs`
If true, add [`**kwargs`](https://docs.python.org/3.3/glossary.html#term-parameter) to the end of the parameter list for `__init__`. This simplifies data class instantiation from dictionaries that may have keys in addition to the fields of the dataclass (i.e. `SomeDataClass(**some_dict)`).

##### `slots`
If true, generate a [`__slots__`](https://docs.python.org/3/reference/datamodel.html#slots) attribute for the class. This reduces the memory footprint of instances and attribute lookup overhead. However, `__slots__` come with a few [restrictions](https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots) (for example, multiple inheritance becomes tricky) that you should be aware of.

##### `hide_internals`
If true (the default), [internal fields](#internal) are not included in the generated `__repr__`.

##### `meta`
Set this parameter to use a metaclass other than dataclassy's own. This metaclass must subclass [`dataclassy.dataclass.DataClassMeta`](dataclassy/dataclass.py).

`DataClassMeta` is best considered less stable than the parts of the library available in the root namespace. Only use a custom metaclass if absolutely necessary.


### Functions
#### `is_dataclass(obj)`
Returns True if `obj` is a data class as implemented in this module.

#### `is_dataclass_instance(obj)`
Returns True if `obj` is an instance of a data class as implemented in this module.

#### `fields(dataclass, internals=False)`
Return a dict of `dataclass`'s fields and their types. `internals` selects whether to include internal fields. `dataclass` can be either a data class or an instance of a data class.

A field is defined as a class-level variable with a [type annotation](https://docs.python.org/3/glossary.html#term-variable-annotation). Variables defined in the class without type annotations are completely excluded from dataclassy's consideration. Class variables and constants can therefore be indicated by the absence of type annotations.

#### `values(dataclass, internals=False)`
Return a dict of `dataclass`'s fields and their values. `internals` selects whether to include internal fields. `dataclass` must be an instance of a data class.

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
Use this type hint to indicate that a variable, parameter or field should be a generic data class instance. For example, dataclassy uses these in the signatures of `as_dict`, `as_tuple` and `values` to show that these functions should be called on data class instances.
