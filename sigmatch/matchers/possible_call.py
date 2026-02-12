from dataclasses import dataclass
from itertools import chain, combinations
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Generator, List, Optional, Tuple, cast

from printo import descript_data_object

from sigmatch.errors import (
    IncorrectArgumentsOrderError,
    SignatureMismatchError,
    SignatureNotFoundError,
    UnsupportedSignatureError,
)
from sigmatch.matchers.abstract import AbstractSignatureMatcher


@dataclass
class Argument:
    name: str


@dataclass
class Baskets:
    only_named: List[str]
    only_posititional: List[str]
    named_or_positional: List[str]
    with_defaults: List[str]
    is_args: bool
    is_kwargs: bool


class PossibleCallMatcher(AbstractSignatureMatcher):
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

        self.is_wrong = False

    def __repr__(self) -> str:
        return descript_data_object(type(self).__name__, (self._get_signature_string(),), {}, filters={0: lambda x: x != ''})

    def __eq__(self, other: Any) -> bool:
        from sigmatch.matchers.series import SignatureSeriesMatcher  # noqa: PLC0415

        if isinstance(other, SignatureSeriesMatcher):
            return other == self

        if not isinstance(other, type(self)):
            return False

        return self.expected_signature == other.expected_signature

    def __hash__(self) -> int:
        return hash(tuple(self.expected_signature))

    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        result = True
        baskets = self._get_baskets(function)

        have_to_be_positional: List[str] = []

        reverse_counter_or_number_of_position_args = self.number_of_position_args

        for name in baskets.only_posititional:
            if not reverse_counter_or_number_of_position_args:
                break
            have_to_be_positional.append(name)
            reverse_counter_or_number_of_position_args -= 1

        for name in baskets.named_or_positional:
            if not reverse_counter_or_number_of_position_args:
                break
            have_to_be_positional.append(name)
            reverse_counter_or_number_of_position_args -= 1

        for name in self.names_of_named_args:
            if name in have_to_be_positional:
                result = False
            if name in baskets.only_named:
                baskets.only_named.remove(name)
            elif name in baskets.named_or_positional:
                baskets.named_or_positional.remove(name)
            elif baskets.is_kwargs:
                pass
            else:
                result = False

        for name in baskets.only_named:
            if name not in baskets.with_defaults:
                result = False

        still_have_to_be_passed = [name for name in baskets.only_posititional + baskets.named_or_positional if name not in baskets.with_defaults]

        if self.number_of_position_args < len(still_have_to_be_passed):
            if raise_exception:
                raise SignatureMismatchError('This is a difficult situation, there is no guarantee that a call with a variable number of positional arguments will fill all the slots of positional arguments.')
            result = False

        elif ((self.number_of_position_args > len(baskets.only_posititional) + len(baskets.named_or_positional)) and not baskets.is_args) or (self.is_args and not baskets.is_args) or (self.is_kwargs and not baskets.is_kwargs):
            result = False

        return result

    @classmethod
    def _get_baskets(cls, function: Callable[..., Any]) -> Baskets:
        try:
            function_signature: Optional[Signature] = signature(function)
            parameters = list(cast(Signature, function_signature).parameters.values())
            return cls._convert_parameters_to_baskets(parameters)
        except ValueError as e:
            raise SignatureNotFoundError('For some functions, it is not possible to extract the signature, and this is one of them.') from e

    @staticmethod
    def _convert_parameters_to_baskets(parameters: List[Parameter]) -> Baskets:
        only_named = []
        only_posititional = []
        named_or_positional = []
        with_defaults = []
        is_args = False
        is_kwargs = False

        for parameter in parameters:

            if parameter.kind == Parameter.POSITIONAL_ONLY:
                only_posititional.append(parameter.name)

            elif parameter.kind == Parameter.POSITIONAL_OR_KEYWORD:
                named_or_positional.append(parameter.name)

            elif parameter.kind == Parameter.KEYWORD_ONLY:
                only_named.append(parameter.name)

            elif parameter.kind == Parameter.VAR_POSITIONAL:
                is_args = True

            elif parameter.kind == Parameter.VAR_KEYWORD:
                is_kwargs = True

            else:  # pragma: no cover
                raise UnsupportedSignatureError('Reading signatures of this kind of arguments is not supported yet.')

            if parameter.default != parameter.empty:
                with_defaults.append(parameter.name)


        return Baskets(
            only_named=only_named,
            only_posititional=only_posititional,
            named_or_positional=named_or_positional,
            with_defaults=with_defaults,
            is_args=is_args,
            is_kwargs=is_kwargs,
        )

    def _convert_symbols(self, args: Tuple[str, ...]) -> List[str]:
        result = []

        for item in args:
            if item:
                splitted_item = item.split(',')
                for chunk in splitted_item:
                    stripped_chunk = chunk.strip()
                    if stripped_chunk and all(x=='.' for x in stripped_chunk):
                        for dot in stripped_chunk:
                            result.append(dot)
                    else:
                        result.append(stripped_chunk)

        self._check_expected_signature(result)
        return self._order_signature(result)

    def _order_signature(self, symbols: List[str]) -> List[str]:
        named_symbols = sorted(x for x in symbols if x.isidentifier())
        dots = (x for x in symbols if x == '.')
        args_and_kwargs = (x for x in symbols if x in ('*', '**'))

        return [*dots, *named_symbols, *args_and_kwargs]

    def _check_expected_signature(self, expected_signature: List[str]) -> None:
        met_name = False
        met_star = False
        met_double_star = False
        all_met_names = set()

        for item in expected_signature:
            if not item.isidentifier() and item not in ('.', '*', '**'):
                raise ValueError(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**" strings. You used "{item}".')

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

            else:  # pragma: no cover
                raise IncorrectArgumentsOrderError(f'What does it mean, this point in expected signature: "{item}"?')

    def _get_signature_string(self) -> str:
        positional_args = ''.join(['.' for x in range(self.number_of_position_args)])
        named_args = ', '.join(sorted([x for x in self.expected_signature if x.isidentifier()]))
        star = '*' if self.is_args else ''
        double_star = '**' if self.is_kwargs else ''

        return ', '.join([x for x in (positional_args, named_args, star, double_star) if x])

    @classmethod
    def from_callable(cls, function: Callable[..., Any], raise_exception: bool = False) -> 'SignatureSeriesMatcher':  # type: ignore[name-defined] # noqa: F821
        from sigmatch.matchers.series import SignatureSeriesMatcher  # noqa: PLC0415

        try:
            baskets = cls._get_baskets(function)
        except SignatureNotFoundError:
            if not raise_exception:
                return SignatureSeriesMatcher()
            raise

        dots_variations = list(cls._produce_combinations_with_dots(baskets.named_or_positional, 0))
        matchers = []

        for variation in dots_variations:
            for exclude_this_names in cls._make_powerset_of_excludes(baskets.with_defaults):
                for add_args in [False] + [x for x in [baskets.is_args] if x]:
                    for add_kwargs in [False] + [x for x in [baskets.is_kwargs] if x]:
                        all_call_arguments = []
                        all_call_arguments.append('.' * (len(baskets.only_posititional) + variation.count('.')))
                        all_call_arguments.extend([x for x in variation if x != '.' and x not in exclude_this_names])
                        all_call_arguments.extend([x for x in baskets.only_named if x not in exclude_this_names])

                        if add_args:
                            all_call_arguments.append('*')
                        if add_kwargs:
                            all_call_arguments.append('**')

                        matchers.append(cls(*all_call_arguments))

        return SignatureSeriesMatcher(*matchers)

    @classmethod
    def _produce_combinations_with_dots(cls, iterable: List[str], index: int) -> Generator[List[str], List[str], None]:
        if index == len(iterable):
            yield []

        else:

            for element in (iterable[index], '.'):
                for tail in cls._produce_combinations_with_dots(iterable, index + 1):
                    yield [element, *tail]

    @staticmethod
    def _make_powerset_of_excludes(some_names: List[str]):
        return chain.from_iterable(
            combinations(some_names, batch_size) for batch_size in range(len(some_names) + 1)
        )
