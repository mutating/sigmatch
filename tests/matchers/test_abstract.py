import pytest
from full_match import match

from sigmatch import (
    PossibleCallMatcher,
)


def test_match_not_callable(matcher_class):
    assert not matcher_class().match(123, raise_exception=False)
    assert not matcher_class().match(123)

    with pytest.raises(ValueError, match=match('It is impossible to determine the signature of an object that is not being callable.')):
        matcher_class().match(123, raise_exception=True)


def test_eq_the_same_class_other_objects(matcher_class):
    assert matcher_class() != 5
    assert matcher_class() != 'kek'


def test_raise_exception_if_not_callable(matcher_class):
    with pytest.raises(ValueError, match=match('It is impossible to determine the signature of an object that is not being callable.')):
        matcher_class().match('kek', raise_exception=True)


def test_it_works_with_class_based_callables(matcher_class, transformed):
    class LocalCallable:
        @transformed
        def __call__(self):
            pass

    assert matcher_class().match(LocalCallable)
    assert not PossibleCallMatcher('.').match(LocalCallable)


def test_empty_class_as_callable(matcher_class):
    class Kek:
        pass

    assert matcher_class().match(Kek)
    assert not PossibleCallMatcher('.').match(Kek)
