import re

import pytest
from full_match import match

from sigmatch import FunctionSignatureMatcher, SignatureMismatchError


def test_random_wrong_functions():
    def function_1():
        pass
    def function_2(arg):
        pass
    def function_3(**kwargs):
        pass
    def function_4(*args, **kwargs):
        pass
    def function_5(a, b):
        pass
    def function_6(a, b, c):
        pass
    def function_7(a, b, c=False):
        pass
    def function_8(a, b, c=False, *d):
        pass
    def function_9(a, b, c=False, *d, **e):
        pass
    def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
    def function_12(c=False, c2=False):
        pass

    assert FunctionSignatureMatcher('.').match(function_1) == False
    assert FunctionSignatureMatcher('c').match(function_2) == False
    assert FunctionSignatureMatcher('.', '**').match(function_3) == False
    assert FunctionSignatureMatcher('.', '**').match(function_4) == False
    assert FunctionSignatureMatcher('.', 'c').match(function_5) == False
    assert FunctionSignatureMatcher('.', '.').match(function_6) == False
    assert FunctionSignatureMatcher('.', '.').match(function_7) == False
    assert FunctionSignatureMatcher('.', '.', 'c').match(function_8) == False
    assert FunctionSignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert FunctionSignatureMatcher('c').match(function_12) == False


def test_random_wrong_async_functions():
    async def function_1():
        pass
    async def function_2(arg):
        pass
    async def function_3(**kwargs):
        pass
    async def function_4(*args, **kwargs):
        pass
    async def function_5(a, b):
        pass
    async def function_6(a, b, c):
        pass
    async def function_7(a, b, c=False):
        pass
    async def function_8(a, b, c=False, *d):
        pass
    async def function_9(a, b, c=False, *d, **e):
        pass
    async def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    async def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
    async def function_12(c=False, c2=False):
        pass

    assert FunctionSignatureMatcher('.').match(function_1) == False
    assert FunctionSignatureMatcher('c').match(function_2) == False
    assert FunctionSignatureMatcher('.', '**').match(function_3) == False
    assert FunctionSignatureMatcher('.', '**').match(function_4) == False
    assert FunctionSignatureMatcher('.', 'c').match(function_5) == False
    assert FunctionSignatureMatcher('.', '.').match(function_6) == False
    assert FunctionSignatureMatcher('.', '.').match(function_7) == False
    assert FunctionSignatureMatcher('.', '.', 'c').match(function_8) == False
    assert FunctionSignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert FunctionSignatureMatcher('c').match(function_12) == False

    assert FunctionSignatureMatcher().match(lambda x: None) == False
    assert FunctionSignatureMatcher('.').match(lambda x, y: None) == False
    assert FunctionSignatureMatcher('*').match(lambda x, *y: None) == False
    assert FunctionSignatureMatcher('**').match(lambda x, **y: None) == False


def test_random_wrong_generator_functions():
    """
    Проверяем, что слепки сигнатур функций с неподходящими функциями не матчатся.
    """
    def function_1():
        yield None
    def function_2(arg):
        yield None
    def function_3(**kwargs):
        yield None
    def function_4(*args, **kwargs):
        yield None
    def function_5(a, b):
        yield None
    def function_6(a, b, c):
        yield None
    def function_7(a, b, c=False):
        yield None
    def function_8(a, b, c=False, *d):
        yield None
    def function_9(a, b, c=False, *d, **e):
        yield None
    def function_10(a, b, c=False, c2=False, *d, **e):
        yield None
    def function_11(a, b, b2, c=False, c2=False, *d, **e):
        yield None
    def function_12(c=False, c2=False):
        yield None

    assert FunctionSignatureMatcher('.').match(function_1) == False
    assert FunctionSignatureMatcher('c').match(function_2) == False
    assert FunctionSignatureMatcher('.', '**').match(function_3) == False
    assert FunctionSignatureMatcher('.', '**').match(function_4) == False
    assert FunctionSignatureMatcher('.', 'c').match(function_5) == False
    assert FunctionSignatureMatcher('.', '.').match(function_6) == False
    assert FunctionSignatureMatcher('.', '.').match(function_7) == False
    assert FunctionSignatureMatcher('.', '.', 'c').match(function_8) == False
    assert FunctionSignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert FunctionSignatureMatcher('c').match(function_12) == False
