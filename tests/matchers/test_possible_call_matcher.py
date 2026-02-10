import pytest
from full_match import match

from sigmatch import PossibleCallMatcher, SignatureMismatchError


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

    assert PossibleCallMatcher('.', '**').match(function_4)
    assert PossibleCallMatcher('.', '.').match(function_7)
    assert PossibleCallMatcher('.', '.', 'c').match(function_8)
    assert PossibleCallMatcher('.', '.', 'c2', '*', '**').match(function_10)
    assert PossibleCallMatcher('c').match(function_12)

    assert not PossibleCallMatcher('.').match(function_1)
    assert not PossibleCallMatcher('c').match(function_2)
    assert not PossibleCallMatcher('.', '**').match(function_3)
    assert not PossibleCallMatcher('.', 'c').match(function_5)
    assert not PossibleCallMatcher('.', '.').match(function_6)
    assert not PossibleCallMatcher('.', 'c', '*', '**').match(function_9)
    assert not PossibleCallMatcher('.', '.', 'c2', '*', '**').match(function_11)
