import pytest
from full_match import match

from sigmatch import PossibleCallMatcher, SignatureMismatchError, SignatureNotFoundError
from sigmatch.matchers.series import SignatureSeriesMatcher


def test_sum_is_flat():
    first = PossibleCallMatcher('.')
    second = PossibleCallMatcher('.')
    third = PossibleCallMatcher('.')

    assert list((first + second + third).matchers) == [first, second, third]


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'raise_exception': False},
    ],
)
def test_not_raise_exception_if_dismatch_and_flag_is_false(options):
    assert not (PossibleCallMatcher() + PossibleCallMatcher('..')).match(lambda x: None, **options)  # noqa: ARG005


def test_class_with_init_as_callable(matcher_class):
    class Kek:
        def __init__(self, a, b, c):
            pass

    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(Kek)
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(Kek)


def test_class_with_call_dunder_object_is_callable(matcher_class, transformed):
    class Kek:
        @transformed
        def __call__(self, a, b, c):
            pass

    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(Kek())
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(Kek())


@pytest.mark.parametrize(
    'function',
    [
        next,
    ],
)
def test_special_functions(function, matcher_class):
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function)
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(function)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('..')).match(function)

    with pytest.raises(SignatureNotFoundError, match=match('For some functions, it is not possible to extract the signature, and this is one of them.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function, raise_exception=True)


def test_check_method(transformed):
    class Kek:
        @transformed
        def kek(self, a, b, c):
            pass

    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(Kek().kek)
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(Kek().kek)


def test_repr():
    assert repr(SignatureSeriesMatcher()) == 'SignatureSeriesMatcher()'
    assert repr(PossibleCallMatcher('.') + PossibleCallMatcher('..')) == "SignatureSeriesMatcher(PossibleCallMatcher('.'), PossibleCallMatcher('..'))"


def test_throughput_check():
    assert (PossibleCallMatcher() + PossibleCallMatcher('..')).match(lambda x, y: None)

    assert not (PossibleCallMatcher() + PossibleCallMatcher('...')).match(lambda x, y: None)
    assert not (PossibleCallMatcher() + PossibleCallMatcher('...')).match(next)


    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        (PossibleCallMatcher() + PossibleCallMatcher('...')).match(lambda x, y: None, raise_exception=True)


@pytest.mark.parametrize(
    'function',
    [
        next,
    ],
)
def test_special_functions(function):
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function)
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(function)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('..')).match(function)

    with pytest.raises(SignatureNotFoundError, match=match('For some functions, it is not possible to extract the signature, and this is one of them.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function, raise_exception=True)
