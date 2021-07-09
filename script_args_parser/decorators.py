from typing import Any, Type, Union

from script_args_parser.arguments import CUSTOM_TYPES_MAPPING


def dataclass_argument(decorated: Type) -> Type:
    def argument_factory(definition: Union[dict, list]) -> Any:
        if isinstance(definition, dict):
            return decorated(**definition)
        if isinstance(definition, list):
            return decorated(*definition)
    decorated.__argument_factory = argument_factory
    CUSTOM_TYPES_MAPPING[decorated.__name__] = decorated.__argument_factory
    return decorated
