import pytest
from full_match import match

from sigmatch import FunctionSignatureMatcher, PossibleCallMatcher, IncorrectArgumentsOrderError


def test_match_not_callable(matcher_class):
    assert not matcher_class('.').match(123, raise_exception=False)
    assert not matcher_class('.').match(123)

    with pytest.raises(ValueError, match=match('It is impossible to determine the signature of an object that is not being callable.')):
        matcher_class('.').match(123, raise_exception=True)


def test_eq_the_same_class(matcher_class):
    assert matcher_class() == matcher_class()
    assert matcher_class('.') == matcher_class('.')
    assert matcher_class('..., kek, *, **') == matcher_class('..., kek, *, **')
    assert matcher_class('..., kek, *, **') == matcher_class('...', 'kek', '*', '**')

    assert matcher_class('.') != matcher_class()
    assert matcher_class('..., kek, *, **') != matcher_class('...', 'kek', '*')


def test_eq_the_same_class_other_objects(matcher_class):
    assert matcher_class('.') != 5
    assert matcher_class('.') != 'kek'
    assert FunctionSignatureMatcher() != PossibleCallMatcher()


def test_repr(matcher_class):
    class_name = matcher_class.__name__

    assert repr(matcher_class()) == f'{class_name}()'
    assert repr(matcher_class('.')) == f'{class_name}(".")'
    assert repr(matcher_class('...')) == f'{class_name}("...")'
    assert repr(matcher_class('..., kek')) == f'{class_name}("..., kek")'
    assert repr(matcher_class('kek')) == f'{class_name}("kek")'
    assert repr(matcher_class('kek, lol')) == f'{class_name}("kek, lol")'
    assert repr(matcher_class('kek, lol, *')) == f'{class_name}("kek, lol, *")'
    assert repr(matcher_class('*')) == f'{class_name}("*")'
    assert repr(matcher_class('*, **')) == f'{class_name}("*, **")'
    assert repr(matcher_class('**')) == f'{class_name}("**")'
    assert repr(matcher_class('..., kek, *, **')) == f'{class_name}("..., kek, *, **")'


@pytest.mark.parametrize(
    ['input', 'output'],
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
def test_strings_with_multiple_items(input, output, matcher_class):
    assert matcher_class(*input).expected_signature == output


@pytest.mark.parametrize(
    ['before', 'after', 'message'],
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
def test_wrong_order(before, message, after, matcher_class):
    with pytest.raises(IncorrectArgumentsOrderError, match=match(message)):
        matcher_class(before, after)


@pytest.mark.parametrize(
    'bad_string', [
        '88',
        '/',
        '$',
        'keko kek',
    ],
)
def test_other_bad_string_as_parameter(bad_string, matcher_class):
    with pytest.raises(ValueError, match=match(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**", "?" strings. You used "{bad_string}".')):
        matcher_class('.', bad_string)


def test_bad_string_with_spaces_as_parameter(matcher_class):
    with pytest.raises(ValueError, match=match('Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**", "?" strings. You used "".')):
        matcher_class('.', '   ')


def test_if_parameter_is_not_string(matcher_class):
    with pytest.raises(TypeError, match=match('Only strings can be used as symbolic representation of function parameters. You used "1" (int).')):
        matcher_class('.', 1, '.')


def test_raise_exception_if_not_callable(matcher_class):
    with pytest.raises(ValueError, match=match('It is impossible to determine the signature of an object that is not being callable.')):
        matcher_class().match('kek', raise_exception=True)


def test_strict_match_for_random_functions(matcher_class):
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

    assert matcher_class().match(function_1)
    assert matcher_class('.').match(function_2)
    assert matcher_class('**').match(function_3)
    assert matcher_class('*', '**').match(function_4)
    assert matcher_class('.', '.').match(function_5)
    assert matcher_class('.', '.', '.').match(function_6)
    assert matcher_class('.', '.', 'c').match(function_7)
    assert matcher_class('.', '.', 'c', '*').match(function_8)
    assert matcher_class('.', '.', 'c', '*', '**').match(function_9)
    assert matcher_class('.', '.', 'c', 'c2', '*', '**').match(function_10)
    assert matcher_class('.', '.', '.', 'c', 'c2', '*', '**').match(function_11)
    assert matcher_class('c', 'c2').match(function_12)

    assert matcher_class('.').match(lambda x: None)
    assert matcher_class('.', '.').match(lambda x, y: None)
    assert matcher_class('.', '*').match(lambda x, *y: None)
    assert matcher_class('.', '**').match(lambda x, **y: None)


def test_strict_match_random_async_functions(matcher_class):
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

    assert matcher_class().match(function_1)
    assert matcher_class('.').match(function_2)
    assert matcher_class('**').match(function_3)
    assert matcher_class('*', '**').match(function_4)
    assert matcher_class('.', '.').match(function_5)
    assert matcher_class('.', '.', '.').match(function_6)
    assert matcher_class('.', '.', 'c').match(function_7)
    assert matcher_class('.', '.', 'c', '*').match(function_8)
    assert matcher_class('.', '.', 'c', '*', '**').match(function_9)
    assert matcher_class('.', '.', 'c', 'c2', '*', '**').match(function_10)
    assert matcher_class('.', '.', '.', 'c', 'c2', '*', '**').match(function_11)
    assert matcher_class('c', 'c2').match(function_12)


def test_strict_match_random_generator_functions(matcher_class):
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

    assert matcher_class().match(function_1)
    assert matcher_class('.').match(function_2)
    assert matcher_class('**').match(function_3)
    assert matcher_class('*', '**').match(function_4)
    assert matcher_class('.', '.').match(function_5)
    assert matcher_class('.', '.', '.').match(function_6)
    assert matcher_class('.', '.', 'c').match(function_7)
    assert matcher_class('.', '.', 'c', '*').match(function_8)
    assert matcher_class('.', '.', 'c', '*', '**').match(function_9)
    assert matcher_class('.', '.', 'c', 'c2', '*', '**').match(function_10)
    assert matcher_class('.', '.', '.', 'c', 'c2', '*', '**').match(function_11)
    assert matcher_class('c', 'c2').match(function_12)
