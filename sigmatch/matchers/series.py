from typing import Any, Callable, List

from printo import descript_data_object

from sigmatch import PossibleCallMatcher
from sigmatch.errors import SignatureMismatchError, SignatureNotFoundError
from sigmatch.matchers.abstract import AbstractSignatureMatcher


class SignatureSeriesMatcher(AbstractSignatureMatcher):
    def __init__(self, *matchers: AbstractSignatureMatcher) -> None:
        self.matchers: List[PossibleCallMatcher] = []

        for matcher in matchers:
            if isinstance(matcher, type(self)):
                self.matchers.extend(matcher.matchers)
            else:
                self.matchers.append(matcher)

    def __repr__(self) -> str:
        return descript_data_object(type(self).__name__, self.matchers, {})

    def __bool__(self) -> bool:
        return bool(self.matchers)

    def __hash__(self) -> int:
        return hash(self.matchers)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AbstractSignatureMatcher):
            return False

        if isinstance(other, PossibleCallMatcher):
            other = type(self)(other)

        return set(self.matchers) == set(other.matchers)

    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        if not self.matchers:
            return True

        result = False

        try:
            result = any(matcher.match(function, raise_exception=raise_exception) for matcher in self.matchers)
        except (SignatureNotFoundError, SignatureMismatchError) as e:
            if isinstance(e, SignatureNotFoundError) and raise_exception:
                raise
            if raise_exception:
                raise SignatureMismatchError('The signature failed one of the checks.') from e

        return result
