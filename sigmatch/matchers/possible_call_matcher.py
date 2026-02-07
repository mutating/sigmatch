from typing import Any, Callable

from sigmatch import FunctionSignatureMatcher
from sigmatch.errors import SignatureMismatchError
from sigmatch.matchers.abstract import AbstractSignatureMatcher


class PossibleCallMatcher(AbstractSignatureMatcher):
    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        callable_matcher = FunctionSignatureMatcher.from_callable(function, raise_exception=raise_exception)

        if callable_matcher.is_wrong and not raise_exception:
            return False

        result = True

        if self.is_kwargs and not callable_matcher.is_kwargs:
            result = False

        elif self.is_kwargs or callable_matcher.is_kwargs:
            call_arguments = set(self.names_of_named_args)
            for argument_name in callable_matcher.names_of_named_args:
                if argument_name not in call_arguments:
                    result = False
                    break

        elif set(self.names_of_named_args) != set(callable_matcher.names_of_named_args):
            result = False

        if self.is_args:
            if not callable_matcher.is_args:
                result = False
            if callable_matcher.number_of_position_args and (self.number_of_position_args < callable_matcher.number_of_position_args):
                if raise_exception:
                    raise SignatureMismatchError('This is a difficult situation, there is no guarantee that a call with a variable number of positional arguments will fill all the slots of positional arguments.')
                result = False
        elif callable_matcher.is_args:
            if self.number_of_position_args < callable_matcher.number_of_position_args:
                result = False
        elif self.number_of_position_args != callable_matcher.number_of_position_args:
            result = False

        return result
