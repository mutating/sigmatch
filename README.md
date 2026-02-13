<details>
  <summary>ⓘ</summary>

[![Downloads](https://static.pepy.tech/badge/sigmatch/month)](https://pepy.tech/project/sigmatch)
[![Downloads](https://static.pepy.tech/badge/sigmatch)](https://pepy.tech/project/sigmatch)
[![Coverage Status](https://coveralls.io/repos/github/pomponchik/sigmatch/badge.svg?branch=main)](https://coveralls.io/github/pomponchik/sigmatch?branch=main)
[![Lines of code](https://sloc.xyz/github/pomponchik/sigmatch/?category=code)](https://github.com/boyter/scc/)
[![Hits-of-Code](https://hitsofcode.com/github/pomponchik/sigmatch?branch=main)](https://hitsofcode.com/github/pomponchik/sigmatch/view?branch=main)
[![Test-Package](https://github.com/pomponchik/sigmatch/actions/workflows/tests_and_coverage.yml/badge.svg)](https://github.com/pomponchik/sigmatch/actions/workflows/tests_and_coverage.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/sigmatch.svg)](https://pypi.python.org/pypi/sigmatch)
[![PyPI version](https://badge.fury.io/py/sigmatch.svg)](https://badge.fury.io/py/sigmatch)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/pomponchik/sigmatch)


</details>

![logo](https://raw.githubusercontent.com/pomponchik/sigmatch/develop/docs/assets/logo_3.svg)


This small library allows you to quickly check whether any called object matches the signature you expect. This may be useful to you, for example, if you write libraries that work with callbacks.


## Table of contents

- [**Installation**](#installation)
- [**Usage**](#usage)
- [**Combining different expectations**](#combining-different-expectations)
- [**Comparing functions with each other**](#comparing-functions-with-each-other)


## Installation

You can install [`sigmatch`](https://pypi.python.org/pypi/sigmatch) using pip:

```bash
pip install sigmatch
```

You can also quickly try out this and other packages without having to install using [instld](https://github.com/pomponchik/instld).


## Usage

To check the signature of a callable, you first need to «bake» your expectations into a special object. Here's how to do it:

```python
from sigmatch import PossibleCallMatcher

expectation = PossibleCallMatcher('.., c')
```

You see, we passed a strange string to the `PossibleCallMatcher` constructor. What does it mean? It is a short description of the expected signature in a special micro-language. Let's learn how to compose short expressions in it! Here are a few rules:

- You list the expected arguments of the function separated by commas, like this: `a, b, c`. The spaces are recommended, but not required
- You indicate positional arguments using dots, like this: `., ., .`. The points do not necessarily have to be separated by commas, so a completely equivalent expression would be `...`.
- If you specify a name, it means that the argument will be passed to the function by name (rather than by position). For example, the expression `x, y` means that the function will be called something like this: `function(x=1, y=2)` (not `function(1, 2)`!).
- If you use unpacking when calling a function, use `*` for usual unpacking and `**` for dictionary one.
- The arguments in the expression must be in the following order: first positional, then keyword, then usual unpacking, then dictionary unpacking. Do not violate this!
- If the function does not accept any arguments, do not pass anything to the `PossibleCallMatcher` constructor.

Here are some examples of expressions:

- `..` means *«the function will be called with 2 positional arguments»*.
- `., first, second` means *«the function will be called with 1 positional argument and 2 named arguments: `first` and `second`»*.
- `.., *` means *«the function will be called with 2 positional arguments, and a list can also be unpacked when calling»*, like this: `function(1, 2, *[3, 4, 5])`.
- `.., first, **` means *«the function will be called with 2 positional arguments, the argument `first` will be passed by name, and a dictionary can be unpacked when calling»*, like this: `function(1, 2, first=3, **{'second': 4, 'third': 5})`.

Well, let's go back to the object we created above and try to apply it to the functions to see if they suit us or not:

```python
def first_suitable_function(a, b, c):
    ...

def second_suitable_function(a, b, c=None, d=None):  # This function also suits us, because the argument "d" does not have to be passed.
    ...

def not_suitable_function(a, b):  # Attention!
    ...

print(expectation.match(first_suitable_function))
#> True
print(expectation.match(second_suitable_function))
#> True
print(expectation.match(not_suitable_function))
#> False
```

> ⚠️ Some built-in functions, such as [`next`](https://docs.python.org/3/library/functions.html#next), are written in C and therefore cannot be extracted from them. But if you wrote the function yourself and it is in Python, there should be no problem.

As you can see, the same expression can correspond to functions with different signatures. This is because our expressions describe not the signature of the function, but *how it will be called*. Python allows the same function to be called in different ways.

If you want an exception to be raised when the signature does not match expectations, pass the argument `raise_exception=True` when calling the `match()` method:

```python
expectation.match(not_suitable_function, raise_exception=True)
#> ...
#> sigmatch.errors.SignatureMismatchError: The signature of the callable object does not match the expected one.
```

In this case, an exception will also be raised if the signature cannot be extracted from the passed object.


## Combining different expectations

Sometimes the same function can be called differently in different parts of a program, and that's perfectly normal. But how can you express this situation concisely in terms of `sigmatch`? Just list several expectation objects using plus signs:

```python
expectation = PossibleCallMatcher('...') + PossibleCallMatcher('.., c'),  + PossibleCallMatcher('.., d')
```

> ⚠️ The current variation selection algorithm has one known flaw: it ignores the presence of default values for strictly positional function parameters. However, this problem rarely occurs in real code.

The resulting object will be completely identical to a regular object of the expected signature, i.e., it will also have a `match()` method. However, it will check several signatures, and if at least one of them matches your object, it will return `True`, otherwise `False`:

```python
def now_its_suitable(a, b):  # Let me remind you that last time a function with the same signature didn't suit us, but now it does!
    ...
    
print(expectation.match(now_its_suitable))
#> True
```

You can treat the sum of such objects as a regular collection: iterate through them, find out their number, check for containing.


## Comparing functions with each other

Sometimes you may not know in advance what specific function signature you expect, but you need it to match the signature of some other function so that they are compatible with each other. How can you do it?

To calculate all possible combinations of function arguments, use the `from_callable()` method of the `PossibleCallMatcher` class:

```python
def function(a, b):
    ...

possible_arguments = PossibleCallMatcher.from_callable(function)

print(possible_arguments)
#> SignatureSeriesMatcher(PossibleCallMatcher('., a'), PossibleCallMatcher('., b'), PossibleCallMatcher('..'), PossibleCallMatcher('a, b'))
```

Yes, this is the sum of expected signatures that you may have read about [above](#combining-different-expectations)!

If you need to make sure that the signatures of two functions are *completely identical*, simply compare these combinations with each other:

```python
def function_1(a, b):
    ...

def function_2(a, b):
    ...

def different_function(a, b, c):
    ...

print(PossibleCallMatcher.from_callable(function_1) == PossibleCallMatcher.from_callable(function_2))
#> True
print(PossibleCallMatcher.from_callable(function_2) == PossibleCallMatcher.from_callable(function_3))
#> False
```

But sometimes, the signature of one function is a subset of another, even though the signatures are not completely equal. And you want to make sure that any way you can call the first function, you can also call the second. How can you do this? Use the `in` operator:

```python
def function_1(a, b):
    ...

def function_2(a, b, c=None):
    ...

print(PossibleCallMatcher.from_callable(function_1) in PossibleCallMatcher.from_callable(function_2))
#> True
```

And finally, the weakest check: sometimes you need to make sure that two different functions have at least one common calling way. To do this, you can calculate the intersection of signatures using the `&` operator:

```python
def function_1(a, b, d=None):
    ...

def function_2(a, b, c=None):
    ...

print(bool(PossibleCallMatcher.from_callable(function_1) & PossibleCallMatcher.from_callable(function_2)))
#> True
```
