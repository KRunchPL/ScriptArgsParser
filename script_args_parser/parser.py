import os
import re
import shlex
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import toml
import yaml


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
            self.required = str_to_bool(self.required)
        self.is_list = False
        self.list_type: Optional[str] = None
        self.is_tuple = False
        self.tuple_types: Optional[list[str]] = None
        list_match = re.match(r'list\[(.+)\]', self.type)
        if list_match is not None:
            self.is_list = True
            self.list_type = list_match[1]
        tuple_match = re.search(r'tuple\[(.+?)\]', self.type)
        if tuple_match is not None:
            self.is_tuple = True
            self.tuple_types = [x.strip() for x in tuple_match[1].split(',')]

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
        if self.is_list:
            kwargs['action'] = 'append'
        if self.is_tuple:
            kwargs['nargs'] = len(self.tuple_types)
        return (args, kwargs)


def str_to_bool(value: str) -> bool:
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


class ArgumentsParser:
    """
    Parses arguments according to given toml definition and cli parameters.
    Values for arguments are stored in arguments_values dictionary.

    :param arguments_definitions: toml string containing arguments definition
    :param cli_params: list of cli parameters, if not given sys.arg[1:] is used
    """
    TYPES_MAPPING = {
        'str': str,
        'int': int,
        'bool': str_to_bool,
        'switch': str_to_bool,
        'path': Path,
    }  #: Maps string values of types to actual converters

    def __init__(
        self, arguments: list[Argument], cli_params: Optional[list[str]] = None,
        user_values: Optional[dict[str, Any]] = None
    ) -> None:
        self.user_values = user_values or {}
        self.arguments = arguments
        self.arguments_values = self._read_cli_arguments(cli_params)
        self._fallback_values()
        self._calculate_lists_and_tuples()
        self._convert_values()
        self._validate_required()

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

        with arguments_file.open('r') as args_file:
            arguments = cls._parse_toml_definitions(args_file.read())

        user_values = None
        if yaml_config is not None:
            with yaml_config.open('r') as yaml_file:
                user_values = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        return cls(arguments, cli_params, user_values)

    @staticmethod
    def _parse_toml_definitions(toml_string: str) -> list[Argument]:
        parsed_toml = toml.loads(toml_string)
        return [Argument(name=arg_name, **arg_def) for arg_name, arg_def in parsed_toml.items()]

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

    def _calculate_lists_and_tuples(self) -> None:
        for argument in self.arguments:
            argument_value = self.arguments_values[argument.name]
            if not argument.is_list and not argument.is_tuple:
                continue
            if argument_value is None or not isinstance(argument_value, str):
                continue
            if argument.is_list and not argument.is_tuple:
                self.arguments_values[argument.name] = self._parse_list(argument, argument_value)
            elif not argument.is_list and argument.is_tuple:
                self.arguments_values[argument.name] = self._parse_tuple(argument, argument_value)
            elif argument.is_list and argument.is_tuple:
                self.arguments_values[argument.name] = self._parse_list_of_tuples(argument, argument_value)

    def _convert_values(self) -> None:
        for argument in self.arguments:
            argument_value = self.arguments_values[argument.name]
            if argument_value is None:
                continue
            if argument.is_list and not argument.is_tuple:
                self.arguments_values[argument.name] = [
                    self.TYPES_MAPPING[argument.list_type](x) for x in argument_value
                ]
            elif not argument.is_list and argument.is_tuple:
                converters = [self.TYPES_MAPPING[x] for x in argument.tuple_types]
                self.arguments_values[argument.name] = [
                    conv(value) for conv, value in zip(converters, argument_value)
                ]
            elif argument.is_list and argument.is_tuple:
                converters = [self.TYPES_MAPPING[x] for x in argument.tuple_types]
                self.arguments_values[argument.name] = [
                    [conv(value) for conv, value in zip(converters, list_elem_value)]
                    for list_elem_value in argument_value
                ]
            else:
                self.arguments_values[argument.name] = self.TYPES_MAPPING[argument.type](argument_value)

    def _parse_tuple(self, argument: Argument, argument_value: str) -> list[Any]:
        ret_val = shlex.split(argument_value)
        if len(ret_val) == 0:
            return ['']
        expected_number = len(argument.tuple_types)
        actual_number = len(ret_val)
        if actual_number != expected_number:
            raise RuntimeError(
                f'Tuple {argument.name} expected {expected_number} values and got {actual_number}: '
                f'{argument_value}.'
            )
        return ret_val

    def _split_list(self, argument: Argument, argument_value: str) -> list[Any]:
        if argument_value == '':
            return ['']
        argument_value = ' ' + argument_value + ' '
        while argument_value.find(';;') != -1:
            argument_value = argument_value.replace(';;', '; ;', 1)
        parser = shlex.shlex(argument_value)
        parser.whitespace_split = True
        parser.whitespace = ';'
        return list(parser)

    def _parse_list(self, argument: Argument, argument_value: str) -> list[Any]:
        ret_val = []
        for value in self._split_list(argument, argument_value):
            parsed_value = shlex.split(value)
            if len(parsed_value) == 0:
                ret_val.append('')
            else:
                ret_val.append(parsed_value[0])
        return ret_val

    def _parse_list_of_tuples(self, argument: Argument, argument_value: str) -> list[Any]:
        ret_val = []
        for value in self._split_list(argument, argument_value):
            parsed_value = self._parse_tuple(argument, value)
            ret_val.append(parsed_value)
        return ret_val

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
