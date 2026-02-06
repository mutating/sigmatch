from sigmatch import FunctionSignatureMatcher


def test_random_wrong_functions():
    def function_1():
        pass
    def function_2(arg):
        pass
    def function_3(**kwargs):
        pass
    def function_4(*args, **kwargs):
        pass
    def function_5(a, b):
        pass
    def function_6(a, b, c):
        pass
    def function_7(a, b, c=False):
        pass
    def function_8(a, b, c=False, *d):
        pass
    def function_9(a, b, c=False, *d, **e):
        pass
    def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
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


def test_random_wrong_async_functions():
    async def function_1():
        pass
    async def function_2(arg):
        pass
    async def function_3(**kwargs):
        pass
    async def function_4(*args, **kwargs):
        pass
    async def function_5(a, b):
        pass
    async def function_6(a, b, c):
        pass
    async def function_7(a, b, c=False):
        pass
    async def function_8(a, b, c=False, *d):
        pass
    async def function_9(a, b, c=False, *d, **e):
        pass
    async def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    async def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
    async def function_12(c=False, c2=False):
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

    assert not FunctionSignatureMatcher().match(lambda x: None)  # noqa: ARG005
    assert not FunctionSignatureMatcher('.').match(lambda x, y: None)  # noqa: ARG005
    assert not FunctionSignatureMatcher('*').match(lambda x, *y: None)  # noqa: ARG005
    assert not FunctionSignatureMatcher('**').match(lambda x, **y: None)  # noqa: ARG005


def test_random_wrong_generator_functions():
    def function_1():
        yield None
    def function_2(arg):  # noqa: ARG001
        yield None
    def function_3(**kwargs):  # noqa: ARG001
        yield None
    def function_4(*args, **kwargs):  # noqa: ARG001
        yield None
    def function_5(a, b):  # noqa: ARG001
        yield None
    def function_6(a, b, c):  # noqa: ARG001
        yield None
    def function_7(a, b, c=False):  # noqa: ARG001
        yield None
    def function_8(a, b, c=False, *d):  # noqa: ARG001
        yield None
    def function_9(a, b, c=False, *d, **e):  # noqa: ARG001
        yield None
    def function_10(a, b, c=False, c2=False, *d, **e):  # noqa: ARG001
        yield None
    def function_11(a, b, b2, c=False, c2=False, *d, **e):  # noqa: ARG001
        yield None
    def function_12(c=False, c2=False):  # noqa: ARG001
        yield None

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
