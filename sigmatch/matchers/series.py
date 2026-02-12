from typing import Any, Callable, Generator, List

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
                self.matchers.append(matcher)  # type: ignore[arg-type]

        self.matchers = sorted(set(self.matchers), key=lambda x: x._get_signature_string())

    def __repr__(self) -> str:
        return descript_data_object(type(self).__name__, tuple(self.matchers), {})

    def __bool__(self) -> bool:
        return bool(self.matchers)

    def __hash__(self) -> int:
        return hash(tuple(self.matchers))

    def __len__(self) -> int:
        return len(self.matchers)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AbstractSignatureMatcher):
            return False

        if isinstance(other, PossibleCallMatcher):
            other = type(self)(other)

        return set(self.matchers) == set(other.matchers)

    def __contains__(self, item: AbstractSignatureMatcher) -> bool:
        if not isinstance(item, AbstractSignatureMatcher):
            return False

        if isinstance(item, type(self)):
            if len(item) > len(self):
                return False
            return len(item & self) == len(item)

        return type(self)(item) in self

    def __iter__(self) -> Generator[PossibleCallMatcher, None, None]:
        yield from self.matchers

    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        if not self.matchers:
            return False

        result = False

        try:
            result = any(matcher.match(function, raise_exception=raise_exception) for matcher in self.matchers)
        except (SignatureNotFoundError, SignatureMismatchError) as e:
            if isinstance(e, SignatureNotFoundError) and raise_exception:
                raise
            if raise_exception:
                raise SignatureMismatchError('The signature failed one of the checks.') from e

        return result
