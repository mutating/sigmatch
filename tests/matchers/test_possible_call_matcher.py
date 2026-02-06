import pytest
from full_match import match

from sigmatch import PossibleCallMatcher, SignatureMismatchError


def test_there_should_be_star_in_signature_if_call_contains_it():
    def function_with_star_1(*args): ...
    def function_with_star_2(a, b, c, *args): ...

    def function_without_star_1(): ...
    def function_without_star_2(a, b, c): ...

    assert PossibleCallMatcher('*').match(function_with_star_1)
    assert PossibleCallMatcher('..., *').match(function_with_star_2)

    assert not PossibleCallMatcher('*').match(function_without_star_1)
    assert not PossibleCallMatcher('*').match(function_without_star_2)
    assert not PossibleCallMatcher('..., *').match(function_without_star_2)
    assert not PossibleCallMatcher('.., *').match(function_without_star_2)


def test_number_of_dots_in_call_cant_be_less_than_in_signature_if_signature_contains_star_and_dots_and_call_contains_only_star():
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


def test_dots_number_in_call_has_be_equal_to_signatures_one_if_signature_and_call_doesnt_contain_star():
    def example_1(a, b, c): ...
    def example_2(): ...

    assert PossibleCallMatcher('...').match(example_1)
    assert PossibleCallMatcher().match(example_2)

    assert not PossibleCallMatcher('....').match(example_1)
    assert not PossibleCallMatcher('.').match(example_2)


def test_dots_number_in_call_has_be_equal_or_more_to_signatures_one_if_call_doesnt_contain_star_but_signature_sontains():
    def example_1(a, b, c, *args): ...
    def example_2(*args): ...

    assert PossibleCallMatcher('...').match(example_1)
    assert PossibleCallMatcher().match(example_2)
    assert PossibleCallMatcher('....').match(example_1)
    assert PossibleCallMatcher('.........').match(example_1)
    assert PossibleCallMatcher('.').match(example_2)
    assert PossibleCallMatcher('.........').match(example_2)

    assert not PossibleCallMatcher('..').match(example_1)
    assert not PossibleCallMatcher('.').match(example_1)


def test_signature_has_to_contain_2stars_if_call_contains_2stars():
    def example_1(a, b, c, **args): ...
    def example_2(a, b, c=None, **args): ...
    def example_3(**args): ...

    def bad_example_1(a, b, c): ...
    def bad_example_2(a, b, c=None): ...
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
