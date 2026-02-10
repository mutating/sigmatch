import pytest
from full_match import match

from sigmatch import (
    IncorrectArgumentsOrderError,
    SignatureNotFoundError,
)


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
    ('to_split', 'output'),
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
def test_strings_with_multiple_items(to_split, output, matcher_class):
    assert matcher_class(*to_split).expected_signature == output


@pytest.mark.parametrize(
    ('before', 'after', 'message'),
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
    with pytest.raises(ValueError, match=match(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**" strings. You used "{bad_string}".')):
        matcher_class('.', bad_string)


def test_bad_string_with_spaces_as_parameter(matcher_class):
    with pytest.raises(ValueError, match=match('Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**" strings. You used "".')):
        matcher_class('.', '   ')


def test_if_parameter_is_not_string(matcher_class):
    with pytest.raises(TypeError, match=match('Only strings can be used as symbolic representation of function parameters. You used "1" (int).')):
        matcher_class('.', 1, '.')


def test_raise_exception_if_not_callable(matcher_class):
    with pytest.raises(ValueError, match=match('It is impossible to determine the signature of an object that is not being callable.')):
        matcher_class().match('kek', raise_exception=True)


def test_strict_match_for_random_functions(matcher_class, transformed):
    @transformed
    def function_1():
        pass
    @transformed
    def function_2(arg):
        pass
    @transformed
    def function_3(**kwargs):
        pass
    @transformed
    def function_4(*args, **kwargs):
        pass
    @transformed
    def function_5(a, b):
        pass
    @transformed
    def function_6(a, b, c):
        pass
    @transformed
    def function_7(a, b, c=False):
        pass
    @transformed
    def function_8(a, b, c=False, *d):
        pass
    @transformed
    def function_9(a, b, c=False, *d, **e):
        pass
    @transformed
    def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    @transformed
    def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
    @transformed
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

    assert matcher_class('.').match(lambda x: None)  # noqa: ARG005
    assert matcher_class('.', '.').match(lambda x, y: None)  # noqa: ARG005
    assert matcher_class('.', '*').match(lambda x, *y: None)  # noqa: ARG005
    assert matcher_class('.', '**').match(lambda x, **y: None)  # noqa: ARG005


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'raise_exception': False},
    ],
)
def test_not_raise_exception_if_dismatch_and_flag_is_false(options, matcher_class):
    assert not matcher_class().match(lambda x: None, **options)  # noqa: ARG005


def test_it_works_with_class_based_callables(matcher_class, transformed):
    class LocalCallable:
        @transformed
        def __call__(self):
            pass

    assert matcher_class().match(LocalCallable)
    assert not matcher_class('.').match(LocalCallable)


def test_empty_class_as_callable(matcher_class):
    class Kek:
        pass

    assert matcher_class().match(Kek)
    assert not matcher_class('.').match(Kek)


def test_class_with_init_as_callable(matcher_class):
    class Kek:
        def __init__(self, a, b, c):
            pass

    assert matcher_class('.', '.', '.').match(Kek)
    assert not matcher_class().match(Kek)


def test_class_with_call_dunder_object_is_callable(matcher_class, transformed):
    class Kek:
        @transformed
        def __call__(self, a, b, c):
            pass

    assert matcher_class('.', '.', '.').match(Kek())
    assert not matcher_class().match(Kek())


def test_check_method(matcher_class, transformed):
    class Kek:
        @transformed
        def kek(self, a, b, c):
            pass

    assert matcher_class('.', '.', '.').match(Kek().kek)
    assert not matcher_class().match(Kek().kek)


@pytest.mark.parametrize(
    'function',
    [
        next,
    ],
)
def test_special_functions(function, matcher_class):
    assert not matcher_class('.').match(function)
    assert not matcher_class().match(function)
    assert not matcher_class('..').match(function)

    with pytest.raises(SignatureNotFoundError, match=match('For some functions, it is not possible to extract the signature, and this is one of them.')):
        matcher_class('.').match(function, raise_exception=True)
