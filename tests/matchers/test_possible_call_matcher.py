import pytest
from full_match import match

from sigmatch import (
    IncorrectArgumentsOrderError,
    PossibleCallMatcher,
    SignatureMismatchError,
    SignatureNotFoundError,
    SignatureSeriesMatcher,
)


def test_there_should_be_star_in_signature_if_call_contains_it(transformed):
    @transformed
    def function_with_star_1(*args): ...
    @transformed
    def function_with_star_2(a, b, c, *args): ...

    @transformed
    def function_without_star_1(): ...
    @transformed
    def function_without_star_2(a, b, c): ...

    assert PossibleCallMatcher('*').match(function_with_star_1)
    assert PossibleCallMatcher('..., *').match(function_with_star_2)

    assert not PossibleCallMatcher('*').match(function_without_star_1)
    assert not PossibleCallMatcher('*').match(function_without_star_2)
    assert not PossibleCallMatcher('..., *').match(function_without_star_2)
    assert not PossibleCallMatcher('.., *').match(function_without_star_2)


def test_number_of_dots_in_call_cant_be_less_than_in_signature_if_signature_contains_star_and_dots_and_call_contains_only_star(transformed):
    @transformed
    def example(a, b, c, *args): ...

    assert PossibleCallMatcher('..., *').match(example)
    assert PossibleCallMatcher('...., *').match(example)
    assert PossibleCallMatcher('......., *').match(example)

    assert not PossibleCallMatcher('.., *').match(example)
    assert not PossibleCallMatcher('*').match(example)
    assert not PossibleCallMatcher('., *').match(example)

    with pytest.raises(SignatureMismatchError, match=match('This is a difficult situation, there is no guarantee that a call with a variable number of positional arguments will fill all the slots of positional arguments.')):
        PossibleCallMatcher('.., *').match(example, raise_exception=True)

    with pytest.raises(SignatureMismatchError, match=match('This is a difficult situation, there is no guarantee that a call with a variable number of positional arguments will fill all the slots of positional arguments.')):
        PossibleCallMatcher('*').match(example, raise_exception=True)

    with pytest.raises(SignatureMismatchError, match=match('This is a difficult situation, there is no guarantee that a call with a variable number of positional arguments will fill all the slots of positional arguments.')):
        PossibleCallMatcher('., *').match(example, raise_exception=True)


def test_dots_number_in_call_has_be_equal_to_signatures_one_if_signature_and_call_doesnt_contain_star(transformed):
    @transformed
    def example_1(a, b, c): ...
    @transformed
    def example_2(): ...

    assert PossibleCallMatcher('...').match(example_1)
    assert PossibleCallMatcher().match(example_2)

    assert not PossibleCallMatcher('....').match(example_1)
    assert not PossibleCallMatcher('.').match(example_2)


def test_dots_number_in_call_has_be_equal_or_more_to_signatures_one_if_call_doesnt_contain_star_but_signature_sontains(transformed):
    @transformed
    def example_1(a, b, c, *args): ...
    @transformed
    def example_2(*args): ...

    assert PossibleCallMatcher('...').match(example_1)
    assert PossibleCallMatcher().match(example_2)
    assert PossibleCallMatcher('....').match(example_1)
    assert PossibleCallMatcher('.........').match(example_1)
    assert PossibleCallMatcher('.').match(example_2)
    assert PossibleCallMatcher('.........').match(example_2)

    assert not PossibleCallMatcher('..').match(example_1)
    assert not PossibleCallMatcher('.').match(example_1)


def test_signature_has_to_contain_2stars_if_call_contains_2stars(transformed):
    @transformed
    def example_1(a, b, c, **args): ...
    @transformed
    def example_2(a, b, c=None, **args): ...
    @transformed
    def example_3(**args): ...

    @transformed
    def bad_example_1(a, b, c): ...
    @transformed
    def bad_example_2(a, b, c=None): ...
    @transformed
    def bad_example_3(): ...

    assert PossibleCallMatcher('..., **').match(example_1)
    assert PossibleCallMatcher('.., c, **').match(example_2)
    assert PossibleCallMatcher('**').match(example_3)
    assert PossibleCallMatcher('c, **').match(example_3)
    assert PossibleCallMatcher('a, b, c, **').match(example_3)

    assert not PossibleCallMatcher('**').match(bad_example_1)
    assert not PossibleCallMatcher('**').match(bad_example_2)
    assert not PossibleCallMatcher('**').match(bad_example_3)

    assert not PossibleCallMatcher('..., **').match(bad_example_1)
    assert not PossibleCallMatcher('.., c, **').match(bad_example_2)
    assert not PossibleCallMatcher('**').match(bad_example_3)


def test_signature_cannot_contain_other_names_arguments_except_calls_one_if_signature_and_call_contain_2stars_and_call_contain_named_arguments(transformed):
    @transformed
    def example(a=None, b=None, c=None, **args): ...

    assert PossibleCallMatcher('a, b, c, **').match(example)
    assert PossibleCallMatcher('a, b, c, d, **').match(example)
    assert PossibleCallMatcher('a, b, **').match(example)

def test_signature_cannot_contain_other_names_arguments_except_calls_one_if_signature_and_call_contain_2stars_and_call_doesnt_contain_named_arguments(transformed):
    @transformed
    def example_1(**args): ...
    @transformed
    def example_2(a=None, b=None, c=None, **args): ...

    assert PossibleCallMatcher('**').match(example_1)
    assert PossibleCallMatcher('**').match(example_2)
    assert PossibleCallMatcher('a, b, **').match(example_2)
    assert PossibleCallMatcher('a, b, d, **').match(example_2)

    assert not PossibleCallMatcher('., a, b, d, **').match(example_2)


def test_named_arguments_are_same_if_call_and_signature_dont_contain_2stars(transformed):
    @transformed
    def example_1(a=None, b=None, c=None): ...
    @transformed
    def example_2(): ...

    @transformed
    def example_3(x, a=None, b=None, c=None): ...
    @transformed
    def example_4(x): ...

    assert PossibleCallMatcher('a, b, c').match(example_1)
    assert PossibleCallMatcher().match(example_2)
    assert PossibleCallMatcher('., a, b, c').match(example_3)
    assert PossibleCallMatcher('., a, b').match(example_3)
    assert PossibleCallMatcher('.').match(example_4)
    assert PossibleCallMatcher('a, b').match(example_1)
    assert PossibleCallMatcher('a, c').match(example_1)

    assert not PossibleCallMatcher('a, b, c, d').match(example_1)
    assert not PossibleCallMatcher('a').match(example_2)
    assert not PossibleCallMatcher('., a, b, c, d').match(example_3)
    assert not PossibleCallMatcher('., a').match(example_4)


def test_signature_contains_only_known_named_arguments_if_call_dont_contain_2stars_but_signature_yes(transformed):
    @transformed
    def example(a=None, b=None, c=None, **args): ...

    assert PossibleCallMatcher('a, b, c').match(example)
    assert PossibleCallMatcher('a, b, c, d').match(example)
    assert PossibleCallMatcher('a, b, c, d, e').match(example)
    assert PossibleCallMatcher('a, b').match(example)
    assert PossibleCallMatcher('a, c').match(example)
    assert PossibleCallMatcher('b, c').match(example)
    assert PossibleCallMatcher().match(example)


def test_random_functions(transformed):
    @transformed
    def function_1(): ...
    @transformed
    def function_2(arg): ...
    @transformed
    def function_3(**kwargs): ...
    @transformed
    def function_4(*args, **kwargs): ...
    @transformed
    def function_5(a, b): ...
    @transformed
    def function_6(a, b, c): ...
    @transformed
    def function_7(a, b, c=False): ...
    @transformed
    def function_8(a, b, c=False, *d): ...
    @transformed
    def function_9(a, b, c=False, *d, **e): ...
    @transformed
    def function_10(a, b, c=False, c2=False, *d, **e): ...
    @transformed
    def function_11(a, b, b2, c=False, c2=False, *d, **e): ...
    @transformed
    def function_12(c=False, c2=False): ...

    assert PossibleCallMatcher('., **').match(function_4)
    assert PossibleCallMatcher('..').match(function_7)
    assert PossibleCallMatcher('.., c').match(function_8)
    assert PossibleCallMatcher('.., c2, *, **').match(function_10)
    assert PossibleCallMatcher('c').match(function_12)

    assert not PossibleCallMatcher('.').match(function_1)
    assert not PossibleCallMatcher('c').match(function_2)
    assert not PossibleCallMatcher('., **').match(function_3)
    assert not PossibleCallMatcher('., c').match(function_5)
    assert not PossibleCallMatcher('..').match(function_6)
    assert not PossibleCallMatcher('., c', '*', '**').match(function_9)
    assert not PossibleCallMatcher('.', '.', 'c2', '*', '**').match(function_11)


def test_strict_match_for_random_functions(transformed):
    @transformed
    def function_1(): ...
    @transformed
    def function_2(arg): ...
    @transformed
    def function_3(**kwargs): ...
    @transformed
    def function_4(*args, **kwargs): ...
    @transformed
    def function_5(a, b): ...
    @transformed
    def function_6(a, b, c): ...
    @transformed
    def function_7(a, b, c=False): ...
    @transformed
    def function_8(a, b, c=False, *d): ...
    @transformed
    def function_9(a, b, c=False, *d, **e): ...
    @transformed
    def function_10(a, b, c=False, c2=False, *d, **e): ...
    @transformed
    def function_11(a, b, b2, c=False, c2=False, *d, **e): ...
    @transformed
    def function_12(c=False, c2=False): ...

    assert PossibleCallMatcher().match(function_1)
    assert PossibleCallMatcher('.').match(function_2)
    assert PossibleCallMatcher('**').match(function_3)
    assert PossibleCallMatcher('*', '**').match(function_4)
    assert PossibleCallMatcher('.', '.').match(function_5)
    assert PossibleCallMatcher('.', '.', '.').match(function_6)
    assert PossibleCallMatcher('.', '.', 'c').match(function_7)
    assert PossibleCallMatcher('.', '.', 'c', '*').match(function_8)
    assert PossibleCallMatcher('.', '.', 'c', '*', '**').match(function_9)
    assert PossibleCallMatcher('.', '.', 'c', 'c2', '*', '**').match(function_10)
    assert PossibleCallMatcher('.', '.', '.', 'c', 'c2', '*', '**').match(function_11)
    assert PossibleCallMatcher('c', 'c2').match(function_12)

    assert PossibleCallMatcher('.').match(lambda x: None)  # noqa: ARG005
    assert PossibleCallMatcher('.', '.').match(lambda x, y: None)  # noqa: ARG005
    assert PossibleCallMatcher('.', '*').match(lambda x, *y: None)  # noqa: ARG005
    assert PossibleCallMatcher('.', '**').match(lambda x, **y: None)  # noqa: ARG005


def test_only_positional_parameters():
    def function_1(a, /): ...
    def function_2(a, b, /, z): ...

    assert PossibleCallMatcher('.').match(function_1)

    assert not PossibleCallMatcher().match(function_1)
    assert not PossibleCallMatcher('a').match(function_1)
    assert not PossibleCallMatcher('b').match(function_1)
    assert not PossibleCallMatcher('..').match(function_1)
    assert not PossibleCallMatcher('*').match(function_1)
    assert not PossibleCallMatcher('**').match(function_1)

    assert PossibleCallMatcher('...').match(function_2)
    assert PossibleCallMatcher('.., z').match(function_2)

    assert not PossibleCallMatcher().match(function_2)
    assert not PossibleCallMatcher('.., b').match(function_2)
    assert not PossibleCallMatcher('., b, z').match(function_2)
    assert not PossibleCallMatcher('., z, *').match(function_2)
    assert not PossibleCallMatcher('., z, **').match(function_2)


def test_only_keyword_parameters():
    def function_1(*, a): ...
    def function_2(a, *, b, z): ...

    assert PossibleCallMatcher('a').match(function_1)

    assert not PossibleCallMatcher('.').match(function_1)
    assert not PossibleCallMatcher().match(function_1)
    assert not PossibleCallMatcher('...').match(function_1)
    assert not PossibleCallMatcher('*').match(function_1)
    assert not PossibleCallMatcher('**').match(function_1)
    assert not PossibleCallMatcher('a, *').match(function_1)

    assert PossibleCallMatcher('a, b, z').match(function_2)
    assert PossibleCallMatcher('., b, z').match(function_2)

    assert not PossibleCallMatcher('.., b, z').match(function_2)
    assert not PossibleCallMatcher('.., z').match(function_2)
    assert not PossibleCallMatcher('...').match(function_2)
    assert not PossibleCallMatcher('.., *').match(function_2)
    assert not PossibleCallMatcher('., *').match(function_2)
    assert not PossibleCallMatcher('*').match(function_2)
    assert not PossibleCallMatcher('**').match(function_2)


def test_raise_exception():
    def function_1(): ...
    def function_2(a, *, b, z): ...

    with pytest.raises(SignatureMismatchError, match=match('The signature of the callable object does not match the expected one.')):
        PossibleCallMatcher('.').match(function_1, raise_exception=True)

    with pytest.raises(SignatureMismatchError, match=match('The signature of the callable object does not match the expected one.')):
        PossibleCallMatcher('.., b, z').match(function_2, raise_exception=True)


def test_repr():
    assert repr(PossibleCallMatcher()) == 'PossibleCallMatcher()'
    assert repr(PossibleCallMatcher('.')) == "PossibleCallMatcher('.')"
    assert repr(PossibleCallMatcher('...')) == "PossibleCallMatcher('...')"
    assert repr(PossibleCallMatcher('..., kek')) == "PossibleCallMatcher('..., kek')"
    assert repr(PossibleCallMatcher('kek')) == "PossibleCallMatcher('kek')"
    assert repr(PossibleCallMatcher('kek, lol')) == "PossibleCallMatcher('kek, lol')"
    assert repr(PossibleCallMatcher('lol, kek')) == "PossibleCallMatcher('kek, lol')"
    assert repr(PossibleCallMatcher('kek, lol, *')) == "PossibleCallMatcher('kek, lol, *')"
    assert repr(PossibleCallMatcher('*')) == "PossibleCallMatcher('*')"
    assert repr(PossibleCallMatcher('*, **')) == "PossibleCallMatcher('*, **')"
    assert repr(PossibleCallMatcher('**')) == "PossibleCallMatcher('**')"
    assert repr(PossibleCallMatcher('..., kek, *, **')) == "PossibleCallMatcher('..., kek, *, **')"


def test_eq_the_same_class():
    assert PossibleCallMatcher() == PossibleCallMatcher()
    assert PossibleCallMatcher('.') == PossibleCallMatcher('.')
    assert PossibleCallMatcher('..., kek, *, **') == PossibleCallMatcher('..., kek, *, **')
    assert PossibleCallMatcher('..., kek, *, **') == PossibleCallMatcher('...', 'kek', '*', '**')

    assert PossibleCallMatcher('.') != PossibleCallMatcher()
    assert PossibleCallMatcher('..., kek, *, **') != PossibleCallMatcher('...', 'kek', '*')

    assert PossibleCallMatcher('a, c') == PossibleCallMatcher('c, a')


def test_eq_different_classes():
    assert SignatureSeriesMatcher(PossibleCallMatcher()) == PossibleCallMatcher()
    assert PossibleCallMatcher() == SignatureSeriesMatcher(PossibleCallMatcher())
    assert SignatureSeriesMatcher(PossibleCallMatcher('.')) == PossibleCallMatcher('.')
    assert PossibleCallMatcher('.') == SignatureSeriesMatcher(PossibleCallMatcher('.'))

    assert SignatureSeriesMatcher(PossibleCallMatcher('.')) != PossibleCallMatcher()
    assert PossibleCallMatcher() != SignatureSeriesMatcher(PossibleCallMatcher('.'))
    assert SignatureSeriesMatcher(PossibleCallMatcher('.')) != PossibleCallMatcher('..')
    assert PossibleCallMatcher('..') != SignatureSeriesMatcher(PossibleCallMatcher('.'))


@pytest.mark.parametrize(
    ('to_split', 'output'),
    [
        (['lol, kek'], ['kek', 'lol']),
        (['kek, lol'], ['kek', 'lol']),
        (['., .'], ['.', '.']),
        (['., *'], ['.', '*']),
        (['., kek, *, **'], ['.', 'kek', '*', '**']),
        (['., kek , *, **'], ['.', 'kek', '*', '**']),
        (['., kek           , *, **'], ['.', 'kek', '*', '**']),

        (['lol,kek'], ['kek', 'lol']),
        (['kek,lol'], ['kek', 'lol']),
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
def test_strings_with_multiple_items(to_split, output):
    assert PossibleCallMatcher(*to_split).expected_signature == output


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
def test_wrong_order(before, message, after):
    with pytest.raises(IncorrectArgumentsOrderError, match=match(message)):
        PossibleCallMatcher(before, after)


@pytest.mark.parametrize(
    'bad_string', [
        '88',
        '/',
        '$',
        'keko kek',
    ],
)
def test_other_bad_string_as_parameter(bad_string):
    with pytest.raises(ValueError, match=match(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**" strings. You used "{bad_string}".')):
        PossibleCallMatcher('.', bad_string)


def test_bad_string_with_spaces_as_parameter():
    with pytest.raises(ValueError, match=match('Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**" strings. You used "".')):
        PossibleCallMatcher('.', '   ')


def test_if_parameter_is_not_string():
    with pytest.raises(TypeError, match=match('Only strings can be used as symbolic representation of function parameters. You used "1" (int).')):
        PossibleCallMatcher('.', 1, '.')


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'raise_exception': False},
    ],
)
def test_not_raise_exception_if_dismatch_and_flag_is_false(options):
    assert not PossibleCallMatcher().match(lambda x: None, **options)  # noqa: ARG005


def test_class_with_init_as_callable():
    class Kek:
        def __init__(self, a, b, c):
            pass

    assert PossibleCallMatcher('...').match(Kek)
    assert not PossibleCallMatcher().match(Kek)


def test_class_with_call_dunder_object_is_callable(transformed):
    class Kek:
        @transformed
        def __call__(self, a, b, c):
            pass

    assert PossibleCallMatcher('...').match(Kek())
    assert not PossibleCallMatcher().match(Kek())


@pytest.mark.parametrize(
    'function',
    [
        next,
    ],
)
def test_special_functions(function):
    assert not PossibleCallMatcher('.').match(function)
    assert not PossibleCallMatcher().match(function)
    assert not PossibleCallMatcher('..').match(function)

    with pytest.raises(SignatureNotFoundError, match=match('For some functions, it is not possible to extract the signature, and this is one of them.')):
        PossibleCallMatcher('.').match(function, raise_exception=True)


def test_check_method(transformed):
    class Kek:
        @transformed
        def kek(self, a, b, c):
            pass

    assert PossibleCallMatcher('...').match(Kek().kek)
    assert not PossibleCallMatcher().match(Kek().kek)


def test_hash():
    assert hash(PossibleCallMatcher('.')) == hash(('.',))

    assert {
        PossibleCallMatcher('.'): 'lol',
        PossibleCallMatcher('..'): 'kek',
    }[PossibleCallMatcher('.')] == 'lol'


def test_from_callable_in_simple_way(transformed):
    @transformed
    def some_function(a, b, c): ...

    possibles = PossibleCallMatcher.from_callable(some_function)

    assert len(possibles) == 8

    assert PossibleCallMatcher('., a, b') in possibles
    assert PossibleCallMatcher('., a, c') in possibles
    assert PossibleCallMatcher('., b, c') in possibles
    assert PossibleCallMatcher('.., a') in possibles
    assert PossibleCallMatcher('.., b') in possibles
    assert PossibleCallMatcher('.., c') in possibles
    assert PossibleCallMatcher('...') in possibles
    assert PossibleCallMatcher('a, b, c') in possibles

    assert PossibleCallMatcher('a, b, c, d') not in possibles

def test_from_callable_empty_case(transformed):
    @transformed
    def some_function(): ...

    possibles = PossibleCallMatcher.from_callable(some_function)

    assert len(possibles) == 1

    assert PossibleCallMatcher() in possibles

    assert PossibleCallMatcher('.') not in possibles
    assert PossibleCallMatcher('a') not in possibles


def test_from_callable_without_variables(transformed):
    @transformed
    def some_function_1(*, a, b): ...

    @transformed
    def some_function_2(a, b, /): ...

    assert len(PossibleCallMatcher.from_callable(some_function_1)) == 1
    assert len(PossibleCallMatcher.from_callable(some_function_2)) == 1


def test_from_callable_with_stars(transformed):
    @transformed
    def some_function_1(a, b, *args): ...

    @transformed
    def some_function_2(a, b, **kwargs): ...

    assert len(PossibleCallMatcher.from_callable(some_function_1)) == 4

    assert PossibleCallMatcher('., b, *') in PossibleCallMatcher.from_callable(some_function_1)
    assert PossibleCallMatcher('., a, *') in PossibleCallMatcher.from_callable(some_function_1)
    assert PossibleCallMatcher('.., *') in PossibleCallMatcher.from_callable(some_function_1)
    assert PossibleCallMatcher('a, b, *') in PossibleCallMatcher.from_callable(some_function_1)

    assert len(PossibleCallMatcher.from_callable(some_function_2)) == 4

    assert PossibleCallMatcher('., b, **') in PossibleCallMatcher.from_callable(some_function_2)
    assert PossibleCallMatcher('., a, **') in PossibleCallMatcher.from_callable(some_function_2)
    assert PossibleCallMatcher('.., **') in PossibleCallMatcher.from_callable(some_function_2)
    assert PossibleCallMatcher('a, b, **') in PossibleCallMatcher.from_callable(some_function_2)


def test_from_callable_when_callable_is_wrong():
    assert PossibleCallMatcher.from_callable(next) == SignatureSeriesMatcher()

    with pytest.raises(SignatureNotFoundError, match=match('For some functions, it is not possible to extract the signature, and this is one of them.')):
        PossibleCallMatcher.from_callable(next, raise_exception=True)
