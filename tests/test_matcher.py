import re

import pytest

from sigmatch import SignatureMatcher, SignatureMismatchError, IncorrectArgumentsOrderError


def test_random_functions():
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

    assert SignatureMatcher().match(function_1) == True
    assert SignatureMatcher('.').match(function_2) == True
    assert SignatureMatcher('**').match(function_3) == True
    assert SignatureMatcher('*', '**').match(function_4) == True
    assert SignatureMatcher('.', '.').match(function_5) == True
    assert SignatureMatcher('.', '.', '.').match(function_6) == True
    assert SignatureMatcher('.', '.', 'c').match(function_7) == True
    assert SignatureMatcher('.', '.', 'c', '*').match(function_8) == True
    assert SignatureMatcher('.', '.', 'c', '*', '**').match(function_9) == True
    assert SignatureMatcher('.', '.', 'c', 'c2', '*', '**').match(function_10) == True
    assert SignatureMatcher('.', '.', '.', 'c', 'c2', '*', '**').match(function_11) == True
    assert SignatureMatcher('c', 'c2').match(function_12) == True

    assert SignatureMatcher('.').match(lambda x: None) == True
    assert SignatureMatcher('.', '.').match(lambda x, y: None) == True
    assert SignatureMatcher('.', '*').match(lambda x, *y: None) == True
    assert SignatureMatcher('.', '**').match(lambda x, **y: None) == True


def test_random_async_functions():
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

    assert SignatureMatcher().match(function_1) == True
    assert SignatureMatcher('.').match(function_2) == True
    assert SignatureMatcher('**').match(function_3) == True
    assert SignatureMatcher('*', '**').match(function_4) == True
    assert SignatureMatcher('.', '.').match(function_5) == True
    assert SignatureMatcher('.', '.', '.').match(function_6) == True
    assert SignatureMatcher('.', '.', 'c').match(function_7) == True
    assert SignatureMatcher('.', '.', 'c', '*').match(function_8) == True
    assert SignatureMatcher('.', '.', 'c', '*', '**').match(function_9) == True
    assert SignatureMatcher('.', '.', 'c', 'c2', '*', '**').match(function_10) == True
    assert SignatureMatcher('.', '.', '.', 'c', 'c2', '*', '**').match(function_11) == True
    assert SignatureMatcher('c', 'c2').match(function_12) == True


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

    assert SignatureMatcher('.').match(function_1) == False
    assert SignatureMatcher('c').match(function_2) == False
    assert SignatureMatcher('.', '**').match(function_3) == False
    assert SignatureMatcher('.', '**').match(function_4) == False
    assert SignatureMatcher('.', 'c').match(function_5) == False
    assert SignatureMatcher('.', '.').match(function_6) == False
    assert SignatureMatcher('.', '.').match(function_7) == False
    assert SignatureMatcher('.', '.', 'c').match(function_8) == False
    assert SignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert SignatureMatcher('c').match(function_12) == False


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

    assert SignatureMatcher('.').match(function_1) == False
    assert SignatureMatcher('c').match(function_2) == False
    assert SignatureMatcher('.', '**').match(function_3) == False
    assert SignatureMatcher('.', '**').match(function_4) == False
    assert SignatureMatcher('.', 'c').match(function_5) == False
    assert SignatureMatcher('.', '.').match(function_6) == False
    assert SignatureMatcher('.', '.').match(function_7) == False
    assert SignatureMatcher('.', '.', 'c').match(function_8) == False
    assert SignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert SignatureMatcher('c').match(function_12) == False

    assert SignatureMatcher().match(lambda x: None) == False
    assert SignatureMatcher('.').match(lambda x, y: None) == False
    assert SignatureMatcher('*').match(lambda x, *y: None) == False
    assert SignatureMatcher('**').match(lambda x, **y: None) == False


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

    assert SignatureMatcher('.').match(function_1) == False
    assert SignatureMatcher('c').match(function_2) == False
    assert SignatureMatcher('.', '**').match(function_3) == False
    assert SignatureMatcher('.', '**').match(function_4) == False
    assert SignatureMatcher('.', 'c').match(function_5) == False
    assert SignatureMatcher('.', '.').match(function_6) == False
    assert SignatureMatcher('.', '.').match(function_7) == False
    assert SignatureMatcher('.', '.', 'c').match(function_8) == False
    assert SignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert SignatureMatcher('c').match(function_12) == False


def test_random_generator_functions():
    """
    Проверяем, что слепки сигнатур функций отрабатывают корректно.
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

    assert SignatureMatcher().match(function_1) == True
    assert SignatureMatcher('.').match(function_2) == True
    assert SignatureMatcher('**').match(function_3) == True
    assert SignatureMatcher('*', '**').match(function_4) == True
    assert SignatureMatcher('.', '.').match(function_5) == True
    assert SignatureMatcher('.', '.', '.').match(function_6) == True
    assert SignatureMatcher('.', '.', 'c').match(function_7) == True
    assert SignatureMatcher('.', '.', 'c', '*').match(function_8) == True
    assert SignatureMatcher('.', '.', 'c', '*', '**').match(function_9) == True
    assert SignatureMatcher('.', '.', 'c', 'c2', '*', '**').match(function_10) == True
    assert SignatureMatcher('.', '.', '.', 'c', 'c2', '*', '**').match(function_11) == True
    assert SignatureMatcher('c', 'c2').match(function_12) == True


def test_raise_exception_if_not_callable():
    with pytest.raises(ValueError, match='It is impossible to determine the signature of an object that is not being callable.'):
        SignatureMatcher().match('kek', raise_exception=True)


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'raise_exception': False},
    ],
)
def test_not_raise_exception_if_not_callable(options):
    assert SignatureMatcher().match('kek', **options) == False


def test_raise_exception_if_dismatch():
    with pytest.raises(SignatureMismatchError):
        SignatureMatcher().match(lambda x: None, raise_exception=True)


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'raise_exception': False},
    ],
)
def test_not_raise_exception_if_dismatch_and_flag_is_false(options):
    assert SignatureMatcher().match(lambda x: None, **options) == False


def test_it_works_with_class_based_callables():
    class LocalCallable:
        def __call__(self):
            pass

    assert SignatureMatcher().match(LocalCallable)
    assert not SignatureMatcher('.').match(LocalCallable)


def test_empty_class_as_callable():
    class Kek:
        pass

    assert SignatureMatcher().match(Kek)
    assert not SignatureMatcher('.').match(Kek)


def test_class_with_init_as_callable():
    class Kek:
        def __init__(self, a, b, c):
            pass

    assert SignatureMatcher('.', '.', '.').match(Kek)
    assert not SignatureMatcher().match(Kek)


def test_class_with_call_dunder_object_is_callable():
    class Kek:
        def __call__(self, a, b, c):
            pass

    assert SignatureMatcher('.', '.', '.').match(Kek())
    assert not SignatureMatcher().match(Kek())


def test_check_method():
    class Kek:
        def kek(self, a, b, c):
            pass

    assert SignatureMatcher('.', '.', '.').match(Kek().kek)
    assert not SignatureMatcher().match(Kek().kek)


def test_if_parameter_is_not_string():
    with pytest.raises(TypeError, match=re.escape('Only strings can be used as symbolic representation of function parameters. You used "1" (int).')):
        SignatureMatcher('.', 1, '.')


def test_bad_string_with_spaces_as_parameter():
    with pytest.raises(ValueError, match=re.escape('Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**", "?" strings. You used "".')):
        SignatureMatcher('.', '   ')


@pytest.mark.parametrize(
    'bad_string', [
        '88',
        '/',
        '$',
        'keko kek',
    ]
)
def test_other_bad_string_as_parameter(bad_string):
    with pytest.raises(ValueError, match=re.escape(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**", "?" strings. You used "{bad_string}".')):
        SignatureMatcher('.', bad_string)


@pytest.mark.parametrize(
    'before,after,message',
    [
        ('kek', '.', 'Positional arguments must be specified first.'),
        ('*', '.', 'Positional arguments must be specified first.'),
        ('**', '.', 'Positional arguments must be specified first.'),

        ('*', 'kek', 'Keyword arguments can be specified after positional ones, but before unpacking.'),
        ('**', 'kek', 'Keyword arguments can be specified after positional ones, but before unpacking.'),

        ('**', '*', 'Unpacking positional arguments should go before unpacking keyword arguments.'),

        ('*', '*', 'Unpacking of the same type (*args in this case) can be specified no more than once.'),
        ('**', '**', 'Unpacking of the same type (**kwargs in this case) can be specified no more than once.'),

        ('kek', 'kek', 'The same argument name cannot occur twice. You have a repeat of "kek".'),
    ],
)
def test_wrong_order(before, message, after):
    with pytest.raises(IncorrectArgumentsOrderError, match=re.escape(message)):
        SignatureMatcher(before, after)


@pytest.mark.parametrize(
    'input,output',
    [
        (['lol, kek'], ['lol', 'kek']),
        (['., .'], ['.', '.']),
        (['., *'], ['.', '*']),
        (['., kek, *, **'], ['.', 'kek', '*', '**']),
        (['., kek , *, **'], ['.', 'kek', '*', '**']),
        (['., kek           , *, **'], ['.', 'kek', '*', '**']),

        (['lol,kek'], ['lol', 'kek']),
        (['.,.'], ['.', '.']),
        (['.,*'], ['.', '*']),
        (['.,kek,*,**'], ['.', 'kek', '*', '**']),
        (['..,kek,*,**'], ['.', '.', 'kek', '*', '**']),

        (['..'], ['.', '.']),
        (['...., *'], ['.', '.', '.', '.', '*']),
        (['...., ., *'], ['.', '.', '.', '.', '.', '*']),
        (['..., kek, *, **'], ['.', '.', '.', 'kek', '*', '**']),
    ],
)
def test_strings_with_multiple_items(input, output):
    assert SignatureMatcher(*input).expected_signature == output


def test_repr():
    assert repr(SignatureMatcher()) == 'SignatureMatcher()'
    assert repr(SignatureMatcher('.')) == 'SignatureMatcher(".")'
    assert repr(SignatureMatcher('...')) == 'SignatureMatcher("...")'
    assert repr(SignatureMatcher('..., kek')) == 'SignatureMatcher("..., kek")'
    assert repr(SignatureMatcher('kek')) == 'SignatureMatcher("kek")'
    assert repr(SignatureMatcher('kek, lol')) == 'SignatureMatcher("kek, lol")'
    assert repr(SignatureMatcher('kek, lol, *')) == 'SignatureMatcher("kek, lol, *")'
    assert repr(SignatureMatcher('*')) == 'SignatureMatcher("*")'
    assert repr(SignatureMatcher('*, **')) == 'SignatureMatcher("*, **")'
    assert repr(SignatureMatcher('**')) == 'SignatureMatcher("**")'
    assert repr(SignatureMatcher('..., kek, *, **')) == 'SignatureMatcher("..., kek, *, **")'


def test_eq():
    assert SignatureMatcher() == SignatureMatcher()
    assert SignatureMatcher('.') == SignatureMatcher('.')
    assert SignatureMatcher('..., kek, *, **') == SignatureMatcher('..., kek, *, **')
    assert SignatureMatcher('..., kek, *, **') == SignatureMatcher('...', 'kek', '*', '**')

    assert not (SignatureMatcher('.') == SignatureMatcher())
    assert not (SignatureMatcher('..., kek, *, **') == SignatureMatcher('...', 'kek', '*'))
    assert not (SignatureMatcher('.') == 5)
    assert not (SignatureMatcher('.') == 'kek')
