from inspect import signature, Signature, Parameter
from typing import Callable, List, Any, Optional


class AbstractSignatureMatcher:
    def get_symbols_from_callable(self, function: Callable[..., Any]) -> List[str]:
        if not callable(function):
            raise ValueError('It is impossible to determine the signature of an object that is not being callable.')

        try:
            function_signature: Optional[Signature] = signature(function)
            parameters = list(function_signature.parameters.values())
            symbols = self.convert_parameters_to_symbols(parameters)
        except ValueError as e:
            symbols = self.special_signature_search(function)
            if symbols is None:
                raise ValueError() from e

        return symbols

    def convert_parameters_to_symbols(self, parameters: List[Parameter]) -> List[str]:
        result = []

        for parameter in parameters:
            if parameter.kind == Parameter.POSITIONAL_ONLY:
                if parameter.default == Parameter.empty:
                    result.append('.')
                else:
                    result.append('?')

            elif parameter.kind == Parameter.POSITIONAL_OR_KEYWORD:
                if parameter.default == Parameter.empty:
                    result.append('.')
                else:
                    result.append(parameter.name)

            elif parameter.kind == Parameter.KEYWORD_ONLY:
                result.append(parameter.name)

            elif parameter.kind == Parameter.VAR_POSITIONAL:
                result.append('*')

            elif parameter.kind == Parameter.VAR_KEYWORD:
                result.append('**')

        return result

    def special_signature_search(self, function: Callable[..., Any]) -> Optional[List[str]]:
        if function is next:
            return ['.', '?']
        elif function is anext:
            return ['.', '?']
        elif function is bool:
            return ['?']

        return None
