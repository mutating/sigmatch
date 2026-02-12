import pytest
from full_match import match

from sigmatch import PossibleCallMatcher, SignatureMismatchError, SignatureNotFoundError
from sigmatch.matchers.series import SignatureSeriesMatcher


def test_sum_is_flat():
    first = PossibleCallMatcher('.')
    second = PossibleCallMatcher('..')
    third = PossibleCallMatcher('...')

    assert list((first + second + third).matchers) == [first, second, third]


def test_deduplication():
    assert PossibleCallMatcher('.') + PossibleCallMatcher('.') == SignatureSeriesMatcher(PossibleCallMatcher('.'))
    assert (PossibleCallMatcher('.') + PossibleCallMatcher('.')).matchers == [PossibleCallMatcher('.')]


def test_order():
    assert (PossibleCallMatcher('.') + PossibleCallMatcher('..')).matchers == [PossibleCallMatcher('.'), PossibleCallMatcher('..')]
    assert (PossibleCallMatcher('..') + PossibleCallMatcher('.')).matchers == [PossibleCallMatcher('.'), PossibleCallMatcher('..')]


def test_include_another_series():
    assert SignatureSeriesMatcher(PossibleCallMatcher('.') + PossibleCallMatcher('..')).matchers == [PossibleCallMatcher('.'), PossibleCallMatcher('..')]


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'raise_exception': False},
    ],
)
def test_not_raise_exception_if_dismatch_and_flag_is_false(options):
    assert not (PossibleCallMatcher() + PossibleCallMatcher('..')).match(lambda x: None, **options)  # noqa: ARG005


def test_class_with_init_as_callable():
    class Kek:
        def __init__(self, a, b, c):
            pass

    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(Kek)
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(Kek)


def test_class_with_call_dunder_object_is_callable(transformed):
    class Kek:
        @transformed
        def __call__(self, a, b, c):
            pass

    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(Kek())
    assert not SignatureSeriesMatcher(PossibleCallMatcher()).match(Kek())


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
    assert (PossibleCallMatcher() + PossibleCallMatcher('..')).match(lambda x, y: None)  # noqa: ARG005

    assert not (PossibleCallMatcher() + PossibleCallMatcher('...')).match(lambda x, y: None)  # noqa: ARG005
    assert not (PossibleCallMatcher() + PossibleCallMatcher('...')).match(next)


    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        (PossibleCallMatcher() + PossibleCallMatcher('...')).match(lambda x, y: None, raise_exception=True)  # noqa: ARG005


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


def test_bool():
    assert not SignatureSeriesMatcher()
    assert SignatureSeriesMatcher(PossibleCallMatcher('..'))
    assert SignatureSeriesMatcher(PossibleCallMatcher())
    assert SignatureSeriesMatcher(PossibleCallMatcher(), PossibleCallMatcher('..'))


def test_eq():
    assert SignatureSeriesMatcher() == SignatureSeriesMatcher()
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')) == SignatureSeriesMatcher(PossibleCallMatcher('..'))
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')) == SignatureSeriesMatcher(PossibleCallMatcher('..'), PossibleCallMatcher('..'))
    assert SignatureSeriesMatcher(PossibleCallMatcher(), PossibleCallMatcher('..')) == SignatureSeriesMatcher(PossibleCallMatcher(), PossibleCallMatcher('..'))
    assert SignatureSeriesMatcher(PossibleCallMatcher('..'), PossibleCallMatcher()) == SignatureSeriesMatcher(PossibleCallMatcher(), PossibleCallMatcher('..'))

    assert SignatureSeriesMatcher() != SignatureSeriesMatcher(PossibleCallMatcher('..'))
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')) != SignatureSeriesMatcher()
    assert SignatureSeriesMatcher(PossibleCallMatcher('.')) != SignatureSeriesMatcher(PossibleCallMatcher('..'))
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')) != SignatureSeriesMatcher(PossibleCallMatcher('.'))


def test_hash():
    assert hash(PossibleCallMatcher('.') + PossibleCallMatcher('..')) == hash((PossibleCallMatcher('.'), PossibleCallMatcher('..')))

    assert {
        PossibleCallMatcher('.') + PossibleCallMatcher('..'): 'lol',
        PossibleCallMatcher('.') + PossibleCallMatcher('...'): 'kek',
    }[PossibleCallMatcher('.') + PossibleCallMatcher('..')] == 'lol'


def test_len():
    assert len(SignatureSeriesMatcher()) == 0

    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('.')) == 1
    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('.') + PossibleCallMatcher('.')) == 1
    assert len(PossibleCallMatcher('..') + PossibleCallMatcher('..')) == 1
    assert len(PossibleCallMatcher('a, c') + PossibleCallMatcher('c, a')) == 1

    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('..') + PossibleCallMatcher('...')) == 3
    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('a') + PossibleCallMatcher('c')) == 3
    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('..') + PossibleCallMatcher('...') + PossibleCallMatcher('..., *')) == 4

    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('..') + PossibleCallMatcher('..')) == 2
    assert len(PossibleCallMatcher('.') + PossibleCallMatcher('a') + PossibleCallMatcher('c') + PossibleCallMatcher('c')) == 3


def test_contains():
    assert SignatureSeriesMatcher() in SignatureSeriesMatcher()
    assert (PossibleCallMatcher('.') + PossibleCallMatcher('..')) in (PossibleCallMatcher('.') + PossibleCallMatcher('..'))
    assert (PossibleCallMatcher('.') + PossibleCallMatcher('..')) in (PossibleCallMatcher('.') + PossibleCallMatcher('..') + PossibleCallMatcher('...'))

    assert PossibleCallMatcher('.') in SignatureSeriesMatcher(PossibleCallMatcher('.'))
    assert PossibleCallMatcher('.') in SignatureSeriesMatcher(PossibleCallMatcher('.'), PossibleCallMatcher('..'))
    assert PossibleCallMatcher('.') in SignatureSeriesMatcher(PossibleCallMatcher('.'), PossibleCallMatcher('a, c'))

    assert PossibleCallMatcher('.') not in SignatureSeriesMatcher()

    assert (PossibleCallMatcher('.') + PossibleCallMatcher('..') + PossibleCallMatcher('...')) not in (PossibleCallMatcher('.') + PossibleCallMatcher('..'))

    assert 1 not in (PossibleCallMatcher('.') + PossibleCallMatcher('..'))
    assert '.' not in (PossibleCallMatcher('.') + PossibleCallMatcher('..'))


def test_iter():
    assert list(SignatureSeriesMatcher()) == []
    assert list(PossibleCallMatcher('.') + PossibleCallMatcher('..')) == [PossibleCallMatcher('.'), PossibleCallMatcher('..')]
    assert list(PossibleCallMatcher('.') + PossibleCallMatcher('..')  + PossibleCallMatcher('..')) == [PossibleCallMatcher('.'), PossibleCallMatcher('..')]
    assert list(PossibleCallMatcher('.') + PossibleCallMatcher('..')  + PossibleCallMatcher('...')) == [PossibleCallMatcher('.'), PossibleCallMatcher('..'), PossibleCallMatcher('...')]


def test_empty_class_as_callable():
    class Kek:
        pass

    assert not SignatureSeriesMatcher().match(Kek)
    assert SignatureSeriesMatcher(PossibleCallMatcher()).match(Kek)


def test_it_works_with_class_based_callables(transformed):
    class LocalCallable:
        @transformed
        def __call__(self):
            pass

    assert not SignatureSeriesMatcher().match(LocalCallable)
    assert SignatureSeriesMatcher(PossibleCallMatcher()).match(LocalCallable)


def test_match(transformed):  # noqa: PLR0915
    @transformed
    def function_1(): ...
    @transformed
    def function_2(a, b): ...
    @transformed
    def function_3(a, b, c=None): ...
    @transformed
    def function_4(a, b, c=None, *args): ...
    @transformed
    def function_5(a, b, c=None, **kwargs): ...

    for callable_to_check in (function_1, function_2, function_3, function_4, function_5):
        assert PossibleCallMatcher.from_callable(callable_to_check).match(callable_to_check)

    assert not SignatureSeriesMatcher().match(function_1)
    assert not SignatureSeriesMatcher().match(function_2)
    assert not SignatureSeriesMatcher().match(function_3)
    assert not SignatureSeriesMatcher().match(function_4)
    assert not SignatureSeriesMatcher().match(function_5)

    assert SignatureSeriesMatcher(PossibleCallMatcher()).match(function_1)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_1)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('..............')).match(function_1)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('a, b')).match(function_1)
    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_1, raise_exception=True)
    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        SignatureSeriesMatcher(PossibleCallMatcher('a, b')).match(function_1, raise_exception=True)

    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b')).match(function_2)
    assert SignatureSeriesMatcher(PossibleCallMatcher('., b')).match(function_2)
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')).match(function_2)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_2)
    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_2, raise_exception=True)

    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b')).match(function_3)
    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b, c')).match(function_3)
    assert SignatureSeriesMatcher(PossibleCallMatcher('., b')).match(function_3)
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')).match(function_3)
    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(function_3)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_3)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('..............')).match(function_3)
    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_3, raise_exception=True)

    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b')).match(function_4)
    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b, c')).match(function_4)
    assert SignatureSeriesMatcher(PossibleCallMatcher('., b')).match(function_4)
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')).match(function_4)
    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(function_4)
    assert SignatureSeriesMatcher(PossibleCallMatcher('..............')).match(function_4)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_4)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('a, b, c, d')).match(function_4)
    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_4, raise_exception=True)

    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b')).match(function_5)
    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b, c')).match(function_5)
    assert SignatureSeriesMatcher(PossibleCallMatcher('a, b, c, d')).match(function_5)
    assert SignatureSeriesMatcher(PossibleCallMatcher('., b')).match(function_5)
    assert SignatureSeriesMatcher(PossibleCallMatcher('..')).match(function_5)
    assert SignatureSeriesMatcher(PossibleCallMatcher('...')).match(function_5)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('..............')).match(function_5)
    assert not SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_5)
    with pytest.raises(SignatureMismatchError, match=match('The signature failed one of the checks.')):
        SignatureSeriesMatcher(PossibleCallMatcher('.')).match(function_5, raise_exception=True)
