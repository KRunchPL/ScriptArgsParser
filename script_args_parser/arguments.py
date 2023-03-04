"""
Defines arguments' types.
"""
import re
import shlex
from copy import deepcopy
from dataclasses import asdict, dataclass
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Optional, Type, Union


def _split_string_by_semicolon(argument_value: str) -> list[Any]:
    if argument_value == '':
        return ['']
    argument_value = ' ' + argument_value + ' '
    while argument_value.find(';;') != -1:
        argument_value = argument_value.replace(';;', '; ;', 1)
    parser = shlex.shlex(argument_value)
    parser.whitespace_split = True
    parser.whitespace = ';'
    return list(parser)


def _str_to_bool(value: str) -> bool:
    """
    Parse string into bool. It tries to match some predefined values.

    If none is matches, python bool(value) is used.

    :param value: string to be parsed into bool
    :return: bool value of a given string
    """
    if isinstance(value, str):
        if value.lower() in ['0', 'false', 'no']:
            return False
        if value.lower() in ['1', 'true', 'yes']:
            return True
    return bool(value)


_BASIC_TYPES_MAPPING: dict[str, Callable[[Any], Any]] = {
    'str': str,
    'int': int,
    'bool': _str_to_bool,
    'path': Path,
}  #: Built-in map: string value -> types to actual converter


CUSTOM_TYPES_MAPPING: dict[str, Callable[[Any], Any]] = {
}  #: Maps string values of types to actual converters


@dataclass
class Argument:
    """
    Stores information about single script argument.
    """

    name: str  #: custom name that the value will be stored at
    type: str  #: one of supported types (see README.md)
    description: str  #: user friendly description
    cli_arg: str  #: name of the cli option to set value
    required: bool = False  #: if set to True and the field is not set in any way, exception should be raised
    env_var: Optional[str] = None  #: name of the env var that will be used as a fallback when cli not set
    default_value: Optional[str] = None  #: default value if nothing else is set

    def __post_init__(self) -> None:
        """
        Perform post init argument processing.
        """
        if isinstance(self.required, str):  # type: ignore
            self.required = _str_to_bool(self.required)  # type: ignore

    def parse_value(self, argument_value: Any) -> Any:
        """
        Argument is simple type, no need to parse anything, so it just returns the value as it was.

        :param argument_value: found argument value
        :return: parsed argument value
        """
        return argument_value

    def convert_value(self, argument_value: Any) -> Any:
        """
        Cast argument value into proper type.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        return self.types_mapping[self.type](argument_value)

    def post_process(self, argument_value: Any, arguments: dict[str, Any]) -> Any:
        """
        Argument is simple type, there is no built-in post processing for it.

        :param argument_value: argument value
        :param arguments: values of all parsed arguments
        :return: new argument value
        """
        return argument_value

    @property
    def argparse_options(self) -> tuple[list[str], dict[str, Any]]:
        """
        Generate options to parse argument.

        :return: args and kwargs that can be used in argparse.ArgumentParser.add_argument
        """
        args = [self.cli_arg]
        kwargs: dict[str, Any] = {'dest': self.name}
        if self.type == 'switch':
            kwargs['action'] = 'store'
            kwargs['nargs'] = '?'
            kwargs['const'] = True
        return (args, kwargs)

    @property
    def types_mapping(self) -> dict[str, Callable[[Any], Any]]:
        """
        Generate single mapping for all avaliable types.

        :return: available types mapping
        """
        ret_val = deepcopy(_BASIC_TYPES_MAPPING)
        ret_val.update(CUSTOM_TYPES_MAPPING)
        return ret_val

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type is supported by Argument class.

        :param arg_type: argument type string
        :return: whether provided type is supported
        """
        lower_arg_type = arg_type.lower()
        return (
            arg_type in chain(_BASIC_TYPES_MAPPING, CUSTOM_TYPES_MAPPING)
            or lower_arg_type in chain(_BASIC_TYPES_MAPPING, CUSTOM_TYPES_MAPPING)
        )


@dataclass
class SwitchArgument(Argument):
    """
    Represents switch (bool) arguments.
    """

    @property
    def argparse_options(self) -> tuple[list[str], dict[str, Any]]:
        """
        Generate options to parse argument.

        :return: args and kwargs that can be used in argparse.ArgumentParser.add_argument
        """
        args = [self.cli_arg]
        kwargs = {
            'dest': self.name,
            'action': 'store',
            'nargs': '?',
            'const': True,
        }
        return (args, kwargs)

    def convert_value(self, argument_value: Any) -> bool:
        """
        Cast argument value into proper type.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        return _str_to_bool(argument_value)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type string describes a switch.

        :param arg_type: argument type string
        :return: whether provided type is a switch
        """
        return arg_type.lower() == 'switch'


@dataclass
class PathArgument(Argument):
    """
    Represents path arguments.
    """

    parent_path: Optional[str] = None  #: name of an argument holding parent path

    def convert_value(self, argument_value: Any) -> Path:
        """
        Cast argument value into proper type.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        return Path(argument_value)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type string describes a path.

        :param arg_type: argument type string
        :return: whether provided type is a path
        """
        return arg_type.lower() == 'path'

    def post_process(self, argument_value: Path, arguments: dict[str, Any]) -> Path:
        """
        Prepend the path with parent path if required.

        :param argument_value: argument value
        :param arguments: values of all parsed arguments
        :return: new argument value

        :raises ValueError: if parent path is not a path
        """
        if self.parent_path is not None:
            if not isinstance(parent_path_value := arguments.get(self.parent_path), Path):
                raise ValueError(f'Parent path has to be a Path not {type(parent_path_value)}')
            return parent_path_value / argument_value
        else:
            return argument_value


@dataclass
class IntArgument(Argument):
    """
    Represents integer argument.
    """

    post_operations: Optional[str] = None  #: expression to calulate final value; {value} will be substituted

    def convert_value(self, argument_value: Any) -> int:
        """
        Cast argument value into proper type.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        return int(argument_value)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type string describes an integer.

        :param arg_type: argument type string
        :return: whether provided type is an integer
        """
        return arg_type.lower() == 'int'

    def post_process(self, argument_value: int, arguments: dict[str, Any]) -> int:
        """
        Evaluate the post operations to establish new argument value.

        :param argument_value: argument value
        :param arguments: values of all parsed arguments
        :return: new argument value
        """
        if self.post_operations is not None:
            return int(eval(self.post_operations.format(value=argument_value)))
        else:
            return argument_value


class ListArgument(Argument):
    """
    Represents argument that is a list of values of the same type.
    """

    _TYPE_REGEX = re.compile(r'list\[(.+)\]')

    def __post_init__(self) -> None:
        """
        Perform post init argument processing.

        :raises ValueError: if the argument type does not match list type regex
        """
        super().__post_init__()
        match = self._TYPE_REGEX.match(self.type)
        if match is None:
            raise ValueError(f'List type has to match regexp {self._TYPE_REGEX.pattern}. Found {self.type}.')
        self.items_type = match[1]

    def parse_value(self, argument_value: Union[str, list[str]]) -> list[Any]:
        """
        Parse the value into list of values.

        :param argument_value: read value of the argument
        :return: parsed value of argument

        :raises TypeError: the input value is of not supported type
        """
        if isinstance(argument_value, list):
            return argument_value
        elif not isinstance(argument_value, str):
            raise TypeError(
                f'Value for list type has to be either list or string. Found {type(argument_value)}.'
            )
        ret_val: list[str] = []
        for value in _split_string_by_semicolon(argument_value):
            parsed_value = shlex.split(value)
            if len(parsed_value) == 0:
                ret_val.append('')
            else:
                ret_val.append(parsed_value[0])
        return ret_val

    def convert_value(self, argument_value: list[Any]) -> list[Any]:
        """
        Cast argument list values into proper type.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        return [
            self.types_mapping[self.items_type](x) for x in argument_value
        ]

    @property
    def argparse_options(self) -> tuple[list[str], dict[str, Any]]:
        """
        Generate options to parse argument.

        :return: args and kwargs that can be used in argparse.ArgumentParser.add_argument
        """
        args = [self.cli_arg]
        kwargs = {
            'dest': self.name,
            'action': 'append',
        }
        return (args, kwargs)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type string describes a list.

        :param arg_type: argument type string
        :return: whether provided type is a list
        """
        return arg_type.lower().startswith('list[')


class TupleArgument(Argument):
    """
    Represents argument that is a tuple of values.
    """

    _TYPE_REGEX = re.compile(r'tuple\[(.+)\]')

    def __post_init__(self) -> None:
        """
        Perform post init argument processing.

        :raises ValueError: if the argument type does not match tuple type regex
        """
        super().__post_init__()
        match = self._TYPE_REGEX.match(self.type)
        if match is None:
            raise ValueError(f'Tuple type has to match regexp {self._TYPE_REGEX.pattern}. Found {self.type}.')
        self.items_types = [x.strip() for x in match[1].split(',')]

    def parse_value(self, argument_value: Union[str, list[str]]) -> list[Any]:
        """
        Parse the value into list of values.

        :param argument_value: read value of the argument
        :return: parsed value of argument

        :raises TypeError: input value is of not supported type
        :raises RuntimeError: number of tuple items is dfifferent than declared
        """
        if isinstance(argument_value, list):
            return argument_value
        elif not isinstance(argument_value, str):
            raise TypeError(
                f'Value for tuple type has to be either list or string. Found {type(argument_value)}.'
            )
        ret_val = shlex.split(argument_value)
        if len(ret_val) == 0:
            return ['']
        expected_number = len(self.items_types)
        actual_number = len(ret_val)
        if actual_number != expected_number:
            raise RuntimeError(
                f'Tuple {self.name} expected {expected_number} values and got {actual_number}: '
                f'{argument_value}.'
            )
        return ret_val

    def convert_value(self, argument_value: list[Any]) -> list[Any]:
        """
        Cast tuple items into proper types.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        converters = [self.types_mapping[x] for x in self.items_types]
        return [
            conv(value) for conv, value in zip(converters, argument_value)
        ]

    @property
    def argparse_options(self) -> tuple[list[str], dict[str, Any]]:
        """
        Generate options to parse argument.

        :return: args and kwargs that can be used in argparse.ArgumentParser.add_argument
        """
        args = [self.cli_arg]
        kwargs = {
            'dest': self.name,
            'nargs': len(self.items_types),
        }
        return (args, kwargs)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type string describes a tuple.

        :param arg_type: argument type string
        :return: whether provided type is a tuple
        """
        return arg_type.lower().startswith('tuple[')


class ListOfTuplesArgument(Argument):
    """
    Represents argument that is a list of tuples.
    """

    _TYPE_REGEX = re.compile(r'list\[(tuple\[(.+)\])\]')

    def __post_init__(self) -> None:
        """
        Perform post init argument processing.

        :raises ValueError: if the argument type does not match list of tuples type regex
        """
        super().__post_init__()
        match = self._TYPE_REGEX.match(self.type)
        if match is None:
            raise ValueError(
                f'List of tuples type has to match regexp {self._TYPE_REGEX.pattern}. Found {self.type}.'
            )
        definition = asdict(self)
        definition['type'] = match[1]
        self.tuple_argument = TupleArgument(**definition)

    def parse_value(self, argument_value: Union[str, Union[list[list[Any]], str]]) -> list[list[Any]]:
        """
        Parse the value into list of list of values.

        :param argument_value: read value of the argument
        :return: parsed value of argument

        :raises TypeError: input value is of not supported type
        """
        if isinstance(argument_value, list):
            return argument_value
        elif not isinstance(argument_value, str):
            raise TypeError(
                f'Value for list of tuples has to be either list or string. Found {type(argument_value)}.'
            )
        ret_val: list[list[Any]] = []
        for value in _split_string_by_semicolon(argument_value):
            ret_val.append(self.tuple_argument.parse_value(value))
        return ret_val

    def convert_value(self, argument_value: list[list[Any]]) -> list[list[Any]]:
        """
        Cast tuples' items into proper types.

        :param argument_value: parsed argument value
        :return: casted argument value
        """
        return [self.tuple_argument.convert_value(item_value) for item_value in argument_value]

    @property
    def argparse_options(self) -> tuple[list[str], dict[str, Any]]:
        """
        Generate options to parse argument.

        :return: args and kwargs that can be used in argparse.ArgumentParser.add_argument
        """
        args = [self.cli_arg]
        kwargs = {
            'dest': self.name,
            'nargs': len(self.tuple_argument.items_types),
            'action': 'append',
        }
        return (args, kwargs)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        """
        Check whether given type string describes a list of tuples.

        :param arg_type: argument type string
        :return: whether provided type is a list of tuples
        """
        return arg_type.lower().startswith('list[tuple[')


_BUILT_IN_ARGUMENTS_TYPES: list[Type[Argument]] = [
    ListOfTuplesArgument, ListArgument, TupleArgument, SwitchArgument, PathArgument, IntArgument, Argument
]
CUSTOM_ARGUMENTS_TYPES: list[Type[Argument]] = []


def argument_factory(name: str, definition: dict[str, Any]) -> Argument:
    """
    Create argument based on definition.

    :raises ValueError: when the type does not match any known handler

    :param name: name of created argument
    :param definition: definition of created argument
    :return: created argument
    """
    for argument_class in chain(CUSTOM_ARGUMENTS_TYPES, _BUILT_IN_ARGUMENTS_TYPES):
        if argument_class.matcher(definition['type']):
            return argument_class(name=name, **definition)
    raise ValueError(f'Unknown argument type: {definition["type"]}')
