import pytest

from sigmatch import FunctionSignatureMatcher, PossibleCallMatcher


@pytest.fixture(params=[FunctionSignatureMatcher, PossibleCallMatcher])
def matcher_class(request):
    return request.param
