from typing import Callable, Tuple, List, Any, Optional

from sigmatch.matchers.abstract import AbstractSignatureMatcher
from sigmatch.errors import SignatureMismatchError, IncorrectArgumentsOrderError, SignatureNotFoundError


class FunctionSignatureMatcher(AbstractSignatureMatcher):
    """
    An object of this class contains a "cast" of the expected signature of the called object.
    It can then be applied to the actual called object (by the .match() method) to see if their signatures match the expected one.
    """

    def __init__(self, *args: str) -> None:
        """
        Initializing an object is creating a "cast" of the expected function signature.

        4 types of objects are accepted as arguments (they are all strings):

        1. '.' - corresponds to an ordinary positional argument without a default value.
        2. 'some_argument_name' - corresponds to an argument with a default value. The content of the string is the name of the argument.
        3. '*' - corresponds to packing multiple positional arguments without default values (*args).
        4. '**' - corresponds to packing several named arguments with default values (**kwargs).

        For example, for a function titled like this:

        def func(a, b, c=5, *d, **e):
            ...

        ... such a "cast" will match:

        FunctionSignatureMatcher('.', '.', 'c', '*', '**')
        """
        symbols = self.convert_symbols(args)

        self.check_expected_signature(symbols)
        self.expected_signature = symbols
        self.is_args = '*' in symbols
        self.is_kwargs = '**' in symbols
        self.number_of_position_args = len([x for x in symbols if x == '.'])
        self.number_of_named_args = len([x for x in symbols if x.isidentifier()])
        self.names_of_named_args = list(set([x for x in symbols if x.isidentifier()]))

    def __repr__(self) -> str:
        positional_args = ''.join(['.' for x in range(self.number_of_position_args)])
        named_args = ', '.join([x for x in self.expected_signature if x.isidentifier()])
        star = '*' if self.is_args else ''
        double_star = '**' if self.is_kwargs else ''

        content = ', '.join([x for x in (positional_args, named_args, star, double_star) if x])
        quoted_content = f'"{content}"' if content else ''

        return f'{type(self).__name__}({quoted_content})'

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self.expected_signature == other.expected_signature

    def match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        """We check that the signature of the function passed as an argument corresponds to the "cast" obtained during initialization of the SignatureMatcher object."""
        if not callable(function):
            if raise_exception:
                raise ValueError('It is impossible to determine the signature of an object that is not being callable.')
            return False

        result = self.get_symbols_from_callable(function) == self.expected_signature

        if not result and raise_exception:
            raise SignatureMismatchError('The signature of the callable object does not match the expected one.')
        return result

    def convert_symbols(self, args: Tuple[str, ...]) -> List[str]:
        result = []

        for item in args:
            splitted_item = item.split(',')
            for chunk in splitted_item:
                stripped_chunk = chunk.strip()
                if stripped_chunk and all(x=='.' for x in stripped_chunk):
                    for dot in stripped_chunk:
                        result.append(dot)
                else:
                    result.append(stripped_chunk)

        return result

    def check_expected_signature(self, expected_signature: List[str]) -> None:
        met_name = False
        met_star = False
        met_double_star = False
        all_met_names = set()

        for item in expected_signature:
            if not item.isidentifier() and item not in ('.', '*', '**'):
                raise ValueError(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**", "?" strings. You used "{item}".')

            if item == '.':
                if met_name or met_star or met_double_star:
                    raise IncorrectArgumentsOrderError('Positional arguments must be specified first.')

            elif item.isidentifier():
                met_name = True
                if met_star or met_double_star:
                    raise IncorrectArgumentsOrderError('Keyword arguments can be specified after positional ones, but before unpacking.')
                if item in all_met_names:
                    raise IncorrectArgumentsOrderError(f'The same argument name cannot occur twice. You have a repeat of "{item}".')
                all_met_names.add(item)

            elif item == '*':
                if met_star:
                    raise IncorrectArgumentsOrderError('Unpacking of the same type (*args in this case) can be specified no more than once.')
                met_star = True
                if met_double_star:
                    raise IncorrectArgumentsOrderError('Unpacking positional arguments should go before unpacking keyword arguments.')

            elif item == '**':
                if met_double_star:
                    raise IncorrectArgumentsOrderError('Unpacking of the same type (**kwargs in this case) can be specified no more than once.')
                met_double_star = True
