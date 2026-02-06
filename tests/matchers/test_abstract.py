import pytest
from full_match import match

from sigmatch import FunctionSignatureMatcher, PossibleCallMatcher


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
