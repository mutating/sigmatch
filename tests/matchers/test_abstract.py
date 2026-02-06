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
