import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, Union

import toml
import yaml

from script_args_parser.arguments import Argument, argument_factory


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
