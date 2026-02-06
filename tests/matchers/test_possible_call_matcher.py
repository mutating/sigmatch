import pytest
from full_match import match

from sigmatch import PossibleCallMatcher


def test_match_not_callable():
    assert not PossibleCallMatcher('.').match(123, raise_exception=False)
    assert not PossibleCallMatcher('.').match(123)

    with pytest.raises(ValueError, match=match('It is impossible to determine the signature of an object that is not being callable.')):
        PossibleCallMatcher('.').match(123, raise_exception=True)
