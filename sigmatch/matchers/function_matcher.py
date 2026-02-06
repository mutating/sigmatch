from typing import Any, Callable

from sigmatch.matchers.abstract import AbstractSignatureMatcher, SignatureNotFoundError


class FunctionSignatureMatcher(AbstractSignatureMatcher):
    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        try:
            return self._get_symbols_from_callable(function) == self.expected_signature
        except SignatureNotFoundError:
            if not raise_exception:
                return False
            raise
