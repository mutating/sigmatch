from typing import Any, Callable

from sigmatch.errors import SignatureMismatchError
from sigmatch.matchers.abstract import AbstractSignatureMatcher


class FunctionSignatureMatcher(AbstractSignatureMatcher):
    def match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        if not callable(function):
            if raise_exception:
                raise ValueError('It is impossible to determine the signature of an object that is not being callable.')
            return False

        result = self._get_symbols_from_callable(function) == self.expected_signature

        if not result and raise_exception:
            raise SignatureMismatchError('The signature of the callable object does not match the expected one.')
        return result
