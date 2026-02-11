from abc import ABC, abstractmethod
from typing import Tuple, Any, Callable

from sigmatch.errors import (
    SignatureMismatchError,
    SignatureNotFoundError,
)


class AbstractSignatureMatcher(ABC):
    def __add__(self, other: 'AbstractSignatureMatcher') -> 'SignatureSeriesMatcher':
        from sigmatch.matchers.series import SignatureSeriesMatcher  # noqa: PLC0415

        matchers = []

        for matcher in (self, other):
            if isinstance(matcher, SignatureSeriesMatcher):
                matchers.extend(matcher.matchers)
            else:
                matchers.append(matcher)

        return SignatureSeriesMatcher(*matchers)

    @abstractmethod
    def __hash__(self) -> int:
        ...

    def __and__(self, other: 'AbstractSignatureMatcher') -> 'SignatureSeriesMatcher':
        from sigmatch.matchers.series import SignatureSeriesMatcher  # noqa: PLC0415

        both: Tuple[SignatureSeriesMatcher, SignatureSeriesMatcher] = tuple([x if isinstance(x, SignatureSeriesMatcher) else SignatureSeriesMatcher(x) for x in (self, other)])

        intersection = sorted(set(both[0].matchers) & set(both[1].matchers), key=lambda x: x._get_signature_string())

        return SignatureSeriesMatcher(*intersection)

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
