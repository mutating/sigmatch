from typing import Callable, Any

from printo import descript_data_object

from sigmatch.errors import SignatureNotFoundError, SignatureMismatchError
from sigmatch.matchers.abstract import AbstractSignatureMatcher


class SignatureSeriesMatcher(AbstractSignatureMatcher):
    def __init__(self, *matchers: AbstractSignatureMatcher) -> None:
        self.matchers = matchers

    def __repr__(self) -> str:
        return descript_data_object(type(self).__name__, self.matchers, {})

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
