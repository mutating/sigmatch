# sigmatch: check function signatures

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


![logo](https://raw.githubusercontent.com/pomponchik/sigmatch/develop/docs/assets/logo_3.svg)


This small library allows you to quickly check whether any called object matches the signature you expect. This may be useful to you, for example, if you write libraries that work with callbacks.

Install it:

```bash
pip install sigmatch
```

Now to check the signatures of the callable objects, you need to create a `SignatureMatcher` object, which will "bake" a description of the parameters you expect. You can pass the following arguments to the constructor of the `SignatureMatcher` class (they are all strings):

- `"."` - corresponds to an ordinary positional argument without a default value.
- `"some_argument_name"` - corresponds to an argument with a default value. The content of the string is the name of the argument.
- `"*"` - corresponds to packing multiple positional arguments without default values (*args).
- `"**"` - corresponds to packing several named arguments with default values (**kwargs).

Note that the arguments can only go in this order, that is, you cannot specify the packing before the positional argument, otherwise you will get an `IncorrectArgumentsOrderError`. When you have prepared a `SignatureMatcher` object, you can apply it to function objects and get a response (`True`/`False`) whether their signatures match the expected ones. As an example, see what a function and a `SignatureMatcher` object for it mights look like:

```python
from sigmatch import SignatureMatcher

def function(a, b, c=5, *d, **e):
    ...

matcher = SignatureMatcher('.', '.', 'c', '*', '**')
print(matcher.match(function))  # True
```

You can also pass all the expected arguments as a single line, separated by commas. Positional arguments do not have to be separated, they can be presented as a fused set of dots. Spaces are also optional, but I recommend using them anyway for readability. See:

```python
matcher = SignatureMatcher('.., c, *, **')  # It works exactly the same as `SignatureMatcher('.', '.', 'c', '*', '**')`.
```

The `match()` method works with both regular and coroutine functions, as well as with lambdas, generators, classes, methods, and many other callable objects. By default, the `match()` method returns a boolean value, but you can ask the library to immediately raise an exception if the function does not have the signature you need:

```python
matcher.match(function, raise_exception=True)
```

To catch this exception, import the `SignatureMismatchError`:

```python
from sigmatch import SignatureMatcher, SignatureMismatchError

try:
    SignatureMatcher('.').match(lambda: None, raise_exception=True)
except SignatureMismatchError:
    print('Deal with it (⌐■_■)')  # It'll be printed.
```
