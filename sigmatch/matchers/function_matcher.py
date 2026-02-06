from typing import Any, Callable

from sigmatch.matchers.abstract import AbstractSignatureMatcher


class FunctionSignatureMatcher(AbstractSignatureMatcher):
    def _match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        return self._get_symbols_from_callable(function) == self.expected_signature
