from inspect import signature, Signature, Parameter
from typing import Callable, List, Any, Optional

from sigmatch.errors import IncorrectArgumentsOrderError


class AbstractSignatureMatcher:
    def __init__(self, *args: str) -> None:
        for item in args:
            if not isinstance(item, str):
                raise TypeError(f'Only strings can be used as symbolic representation of function parameters. You used "{item}" ({type(item).__name__}).')

        symbols = self._convert_symbols(args)

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

    def _convert_symbols(self, args: Tuple[str, ...]) -> List[str]:
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

        self._check_expected_signature(result)
        return result

    def _get_symbols_from_callable(self, function: Callable[..., Any]) -> List[str]:
        if not callable(function):
            raise ValueError('It is impossible to determine the signature of an object that is not being callable.')

        try:
            function_signature: Optional[Signature] = signature(function)
            parameters = list(function_signature.parameters.values())
            symbols = self._convert_parameters_to_symbols(parameters)
        except ValueError as e:
            symbols = self._special_signature_search(function)
            if symbols is None:
                raise ValueError() from e

        return symbols

    def _convert_parameters_to_symbols(self, parameters: List[Parameter]) -> List[str]:
        result = []

        for parameter in parameters:
            if parameter.kind == Parameter.POSITIONAL_ONLY:
                if parameter.default == Parameter.empty:
                    result.append('.')
                else:
                    result.append('?')

            elif parameter.kind == Parameter.POSITIONAL_OR_KEYWORD:
                if parameter.default == Parameter.empty:
                    result.append('.')
                else:
                    result.append(parameter.name)

            elif parameter.kind == Parameter.KEYWORD_ONLY:
                result.append(parameter.name)

            elif parameter.kind == Parameter.VAR_POSITIONAL:
                result.append('*')

            elif parameter.kind == Parameter.VAR_KEYWORD:
                result.append('**')

        return result

    def _special_signature_search(self, function: Callable[..., Any]) -> Optional[List[str]]:
        if function is next:
            return ['.', '?']
        elif function is anext:
            return ['.', '?']
        elif function is bool:
            return ['?']

        return None

    def _check_expected_signature(self, expected_signature: List[str]) -> None:
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
