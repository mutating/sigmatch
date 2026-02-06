import pytest
from full_match import match

from sigmatch import PossibleCallMatcher


def test_there_should_be_star_in_signature_if_call_contains_it():
    def function_with_star_1(*args): ...
    def function_with_star_2(a, b, c, *args): ...

    def function_without_star_1(): ...
    def function_without_star_2(a, b, c): ...

    assert PossibleCallMatcher('*').match(function_with_star_1)
    assert PossibleCallMatcher('..., *').match(function_with_star_2)

    assert not PossibleCallMatcher('*').match(function_without_star_1, raise_exception=False)
    assert not PossibleCallMatcher('*').match(function_without_star_2, raise_exception=False)
    assert not PossibleCallMatcher('..., *').match(function_without_star_2, raise_exception=False)
    assert not PossibleCallMatcher('.., *').match(function_without_star_2, raise_exception=False)
