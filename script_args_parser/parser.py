import os
import re
import shlex
from argparse import ArgumentParser
from copy import deepcopy
from dataclasses import asdict, dataclass
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Optional, Union

import toml
import yaml


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
    Parses string into bool. It tries to match some predefined values.
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


_BASIC_TYPES_MAPPING: dict[str, Callable] = {
    'str': str,
    'int': int,
    'bool': _str_to_bool,
    'path': Path,
}  #: Built-in map: string value -> types to actual converter

CUSTOM_TYPES_MAPPING: dict[str, Callable] = {
}  #: Maps string values of types to actual converters


@dataclass
class Argument:
    """
    Stores information about single script arguments
    """
    name: str  #: custom name that the value will be stored at
    type: str  #: one of supported types (see README.md)
    description: str  #: user friendly description
    cli_arg: str  #: name of the cli option to set value
    required: bool = False  #: if set to True and the field is not set in any way, exception should be raised
    env_var: Optional[str] = None  #: name of the env var that will be used as a fallback when cli not set
    default_value: Optional[str] = None  #: default value if nothing else is set

    def __post_init__(self):
        if isinstance(self.required, str):
            self.required = _str_to_bool(self.required)

    def parse_value(self, argument_value: Any) -> Any:
        return argument_value

    def convert_value(self, argument_value: Any) -> Any:
        return self.types_mapping[self.type](argument_value)

    def post_process(self, argument_value: Any, arguments: dict[str, Any]) -> Any:
        return argument_value

    @property
    def argparse_options(self) -> dict:
        """
        :return: args and kwargs that can be used in argparse.ArgumentParser.add_argument
        """
        args = [self.cli_arg]
        kwargs = {'dest': self.name}
        if self.type == 'switch':
            kwargs['action'] = 'store'
            kwargs['nargs'] = '?'
            kwargs['const'] = True
        return (args, kwargs)

    @property
    def types_mapping(self) -> dict[str, Callable]:
        ret_val = deepcopy(_BASIC_TYPES_MAPPING)
        ret_val.update(CUSTOM_TYPES_MAPPING)
        return ret_val

    @staticmethod
    def matcher(arg_type: str) -> bool:
        return arg_type in _BASIC_TYPES_MAPPING or arg_type in CUSTOM_TYPES_MAPPING


@dataclass
class SwitchArgument(Argument):
    @property
    def argparse_options(self) -> dict:
        """
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
        return _str_to_bool(argument_value)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        return arg_type == 'switch'


@dataclass
class PathArgument(Argument):
    def convert_value(self, argument_value: Any) -> Path:
        return Path(argument_value)

    @staticmethod
    def matcher(arg_type: str) -> bool:
        return arg_type == 'path'


class ListArgument(Argument):
    _TYPE_REGEX = re.compile(r'list\[(.+)\]')

    def __post_init__(self):
        super().__post_init__()
        match = self._TYPE_REGEX.match(self.type)
        if match is None:
            raise ValueError(f'List type has to match regexp {self._TYPE_REGEX.pattern}. Found {self.type}.')
        self.items_type = match[1]

    def parse_value(self, argument_value: Union[str, list]) -> list[Any]:
        if isinstance(argument_value, list):
            return argument_value
        elif not isinstance(argument_value, str):
            raise TypeError(
                f'Value for list type has to be either list or string. Found {type(argument_value)}.'
            )
        ret_val = []
        for value in _split_string_by_semicolon(argument_value):
            parsed_value = shlex.split(value)
            if len(parsed_value) == 0:
                ret_val.append('')
            else:
                ret_val.append(parsed_value[0])
        return ret_val

    def convert_value(self, argument_value: list[Any]) -> list[Any]:
        return [
            self.types_mapping[self.items_type](x) for x in argument_value
        ]

    @property
    def argparse_options(self) -> dict:
        """
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
        return arg_type.startswith('list[')


class TupleArgument(Argument):
    _TYPE_REGEX = re.compile(r'tuple\[(.+)\]')

    def __post_init__(self):
        super().__post_init__()
        match = self._TYPE_REGEX.match(self.type)
        if match is None:
            raise ValueError(f'Tuple type has to match regexp {self._TYPE_REGEX.pattern}. Found {self.type}.')
        self.items_types = [x.strip() for x in match[1].split(',')]

    def parse_value(self, argument_value: Union[str, list]) -> list[Any]:
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
        converters = [self.types_mapping[x] for x in self.items_types]
        return [
            conv(value) for conv, value in zip(converters, argument_value)
        ]

    @property
    def argparse_options(self) -> dict:
        """
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
        return arg_type.startswith('tuple[')


class ListOfTuplesArgument(Argument):
    _TYPE_REGEX = re.compile(r'list\[(tuple\[(.+)\])\]')

    def __post_init__(self):
        super().__post_init__()
        match = self._TYPE_REGEX.match(self.type)
        if match is None:
            raise ValueError(
                f'List of tuples type has to match regexp {self._TYPE_REGEX.pattern}. Found {self.type}.'
            )
        definition = asdict(self)
        definition['type'] = match[1]
        self.tuple_argument = TupleArgument(**definition)

    def parse_value(self, argument_value: Union[str, list]) -> list[list[Any]]:
        if isinstance(argument_value, list):
            return argument_value
        elif not isinstance(argument_value, str):
            raise TypeError(
                f'Value for list of tuples has to be either list or string. Found {type(argument_value)}.'
            )
        ret_val = []
        for value in _split_string_by_semicolon(argument_value):
            ret_val.append(self.tuple_argument.parse_value(value))
        return ret_val

    def convert_value(self, argument_value: list[list[Any]]) -> list[list[Any]]:
        return [self.tuple_argument.convert_value(item_value) for item_value in argument_value]

    @property
    def argparse_options(self) -> dict:
        """
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
        return arg_type.startswith('list[tuple[')


_BUILT_IN_ARGUMENTS_TYPES = [
    ListOfTuplesArgument, ListArgument, TupleArgument, SwitchArgument, PathArgument, Argument
]
CUSTOM_ARGUMENTS_TYPES = []


def argument_factory(name: str, definition: dict) -> Argument:
    lower_type = definition['type'].lower()
    for argument_class in chain(CUSTOM_ARGUMENTS_TYPES, _BUILT_IN_ARGUMENTS_TYPES):
        if argument_class.matcher(lower_type):
            return argument_class(name=name, **definition)
    raise ValueError(f'Unknown argument type: {definition["type"]}')


class ArgumentsParser:
    """
    Parses arguments according to given toml definition and cli parameters.
    Values for arguments are stored in arguments_values dictionary.

    :param arguments_definitions: toml string containing arguments definition
    :param cli_params: list of cli parameters, if not given sys.arg[1:] is used
    """
    def __init__(
        self, arguments: list[Argument], cli_params: Optional[list[str]] = None,
        user_values: Optional[dict[str, Any]] = None
    ) -> None:
        self.user_values = user_values or {}
        self.arguments = arguments
        self.arguments_values = self._read_cli_arguments(cli_params)
        self._fallback_values()
        self._parse_values()
        self._convert_values()
        self._validate_required()
        self._post_process()

    def __getattr__(self, name: str) -> Any:
        if name != 'arguments_values' and name in self.arguments_values:
            return self.arguments_values[name]
        raise AttributeError(f'No attribute named "{name}"')

    def __setattr__(self, name: str, value: Any) -> None:
        if name != 'arguments_values' and name in getattr(self, 'arguments_values', {}):
            self.arguments_values[name] = value
        else:
            super().__setattr__(name, value)

    @classmethod
    def from_files(
        cls, arguments_file: Union[str, Path], cli_params: Optional[list[str]] = None,
        yaml_config: Optional[Union[str, Path]] = None
    ) -> 'ArgumentsParser':
        if isinstance(arguments_file, str):
            arguments_file = Path(arguments_file)
        if isinstance(yaml_config, str):
            yaml_config = Path(yaml_config)
        arguments = cls._parse_toml_definitions(arguments_file.read_text())
        if yaml_config is None:
            user_values = None
        else:
            user_values = yaml.load(yaml_config.read_text(), Loader=yaml.SafeLoader)
        return cls(arguments, cli_params, user_values)

    @staticmethod
    def _parse_toml_definitions(toml_string: str) -> list[Argument]:
        parsed_toml = toml.loads(toml_string)
        return [argument_factory(arg_name, arg_def) for arg_name, arg_def in parsed_toml.items()]

    def _read_cli_arguments(self, cli_params: list[str] = None) -> dict[str, Any]:
        cli_parser = ArgumentParser()
        for argument in self.arguments:
            args, kwargs = argument.argparse_options
            cli_parser.add_argument(*args, **kwargs)
        return vars(cli_parser.parse_args(cli_params))

    def _fallback_values(self) -> None:
        for argument in self.arguments:
            if self.arguments_values[argument.name] is None:
                self.arguments_values[argument.name] = self.user_values.get(argument.name)
            if self.arguments_values[argument.name] is None and argument.env_var is not None:
                self.arguments_values[argument.name] = os.getenv(argument.env_var)
            if self.arguments_values[argument.name] is None and argument.default_value is not None:
                self.arguments_values[argument.name] = argument.default_value

    def _parse_values(self) -> None:
        for argument in self.arguments:
            if (argument_value := self.arguments_values[argument.name]) is not None:
                self.arguments_values[argument.name] = argument.parse_value(argument_value)

    def _convert_values(self) -> None:
        for argument in self.arguments:
            if (argument_value := self.arguments_values[argument.name]) is not None:
                self.arguments_values[argument.name] = argument.convert_value(argument_value)

    def _validate_required(self) -> None:
        for arg in self.arguments:
            if arg.required and self.arguments_values[arg.name] is None:
                error_msg = f'No value supplied for argument "{arg.name}". You can set it in config file'
                if arg.cli_arg is not None:
                    error_msg += f' or by using cli option: "{arg.cli_arg}"'
                if arg.env_var is not None:
                    error_msg += f' or by setting env variable: "{arg.env_var}"'
                error_msg += '.'
                raise RuntimeError(error_msg)

    def _post_process(self) -> None:
        for argument in self.arguments:
            self.arguments_values[argument.name] = argument.post_process(
                self.arguments_values[argument.name],
                self.arguments_values,
            )
