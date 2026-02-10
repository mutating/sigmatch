import pytest
from full_match import match

from sigmatch import (
    IncorrectArgumentsOrderError,
    SignatureNotFoundError,
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
    assert not PossibleCallMatcher('.').match(LocalCallable)


def test_empty_class_as_callable(matcher_class):
    class Kek:
        pass

    assert matcher_class().match(Kek)
    assert not PossibleCallMatcher('.').match(Kek)


def test_class_with_init_as_callable(matcher_class):
    class Kek:
        def __init__(self, a, b, c):
            pass

    assert PossibleCallMatcher('.', '.', '.').match(Kek)
    assert not matcher_class().match(Kek)


def test_class_with_call_dunder_object_is_callable(matcher_class, transformed):
    class Kek:
        @transformed
        def __call__(self, a, b, c):
            pass

    assert PossibleCallMatcher('.', '.', '.').match(Kek())
    assert not matcher_class().match(Kek())


def test_check_method(matcher_class, transformed):
    class Kek:
        @transformed
        def kek(self, a, b, c):
            pass

    assert PossibleCallMatcher('.', '.', '.').match(Kek().kek)
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

    with pytest.raises(SignatureNotFoundError, match=match('For some functions, it is not possible to extract the signature, and this is one of them.')):
        PossibleCallMatcher('.').match(function, raise_exception=True)
