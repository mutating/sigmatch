from abc import ABC, abstractmethod
from typing import Any, Callable

from sigmatch.errors import (
    SignatureMismatchError,
    SignatureNotFoundError,
)


class AbstractSignatureMatcher(ABC):
    def match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        if not callable(function):
            if raise_exception:
                raise ValueError('It is impossible to determine the signature of an object that is not being callable.')
            return False

        try:
            result = self._match(function, raise_exception=raise_exception)
        except SignatureNotFoundError:
            if raise_exception:
                raise
            result = False

        if not result and raise_exception:
            raise SignatureMismatchError('The signature of the callable object does not match the expected one.')
        return result

    @abstractmethod
    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        ...  # pragma: no cover
