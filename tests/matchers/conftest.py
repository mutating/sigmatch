import pytest
from transfunctions import transfunction

from sigmatch import FunctionSignatureMatcher, PossibleCallMatcher


@pytest.fixture(params=[FunctionSignatureMatcher, PossibleCallMatcher])
def matcher_class(request):
    return request.param


@pytest.fixture(params=['async', 'sync', 'generator'])
def transformed(request):
    def transformator_function(function):
        if request.param == 'sync':
            return function
        if request.param == 'async':
            return transfunction(function, check_decorators=False).get_async_function()
        if request.param == 'generator':
            return transfunction(function, check_decorators=False).get_generator_function()
    return transformator_function
