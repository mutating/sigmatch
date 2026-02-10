from sigmatch import FunctionSignatureMatcher


def test_random_wrong_functions(transformed):
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

    assert not FunctionSignatureMatcher('.').match(function_1)
    assert not FunctionSignatureMatcher('c').match(function_2)
    assert not FunctionSignatureMatcher('.', '**').match(function_3)
    assert not FunctionSignatureMatcher('.', '**').match(function_4)
    assert not FunctionSignatureMatcher('.', 'c').match(function_5)
    assert not FunctionSignatureMatcher('.', '.').match(function_6)
    assert not FunctionSignatureMatcher('.', '.').match(function_7)
    assert not FunctionSignatureMatcher('.', '.', 'c').match(function_8)
    assert not FunctionSignatureMatcher('.', 'c', '*', '**').match(function_9)
    assert not FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_10)
    assert not FunctionSignatureMatcher('.', '.', 'c2', '*', '**').match(function_11)
    assert not FunctionSignatureMatcher('c').match(function_12)
