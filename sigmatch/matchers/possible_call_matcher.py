from typing import Any, Callable, Optional, List, cast
from inspect import Parameter, Signature, signature

from sigmatch import FunctionSignatureMatcher
from sigmatch.errors import SignatureNotFoundError, UnsupportedSignatureError, SignatureMismatchError
from sigmatch.matchers.abstract import AbstractSignatureMatcher

from dataclasses import dataclass


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
    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        #1. ТОЛЬКО ИМЕННЫЕ аргументы (множество)
        #2. ТОЛЬКО ПОЗИЦИОННЫЕ (множество)
        #3. ИМЕННЫЕ ИЛИ ПОЗИЦИОННЫЕ (список с именами и позициями, позиции значимы)
        #4. Бесконечные контейнеры АРГОВ и КВАРГОВ (два була)
        #
        #
        result = True
        baskets = self._get_baskets(function)


        have_to_be_positional = []
        for name in baskets.only_named:
            if len(have_to_be_positional) == self.number_of_position_args:
                break
            have_to_be_positional.append(name)

        for name in baskets.named_or_positional:
            if len(have_to_be_positional) == self.number_of_position_args:
                break
            have_to_be_positional.append(name)

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

        elif (self.number_of_position_args > len(baskets.only_posititional) + len(baskets.named_or_positional)) and not baskets.is_args:
            result = False

        elif (self.is_args and not baskets.is_args) or (self.is_kwargs and not baskets.is_kwargs):
            result = False

        if (not result) and raise_exception:
            raise SignatureMismatchError('The signature of the callable object does not match the expected one.')

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
