"""
Decorators that helps defining argument types.
"""
from typing import Any, Type, Union

from script_args_parser.arguments import CUSTOM_TYPES_MAPPING


def dataclass_argument(decorated: Type[Any]) -> Type[Any]:
    """
    Register decorated dataclass as supported argument type.

    :param decorated: dataclass to be registered

    :return: decorated class, but a little bit modified
    """
    def argument_factory(definition: Union[dict[str, Any], list[Any]]) -> Any:
        if isinstance(definition, dict):
            return decorated(**definition)
        if isinstance(definition, list):
            return decorated(*definition)
    CUSTOM_TYPES_MAPPING[decorated.__name__] = argument_factory
    return decorated
