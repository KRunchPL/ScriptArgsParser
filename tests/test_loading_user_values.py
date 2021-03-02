import os
from tempfile import NamedTemporaryFile

import pytest
import toml
import yaml

from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_file_path():
    mappings = {
        'first_arg': {
            'type': 'str',
            'description': 'Some fancy description',
            'cli_arg': '--cli-option-name',
            'env_var': 'ENV_VAR_NAME',
            'default_value': 'first_default'
        }
    }
    toml_file = NamedTemporaryFile(mode='w', delete=False)
    try:
        toml.dump(mappings, toml_file)
        toml_file.close()
        yield toml_file.name
    finally:
        os.unlink(toml_file.name)


def test_yaml(toml_file_path):
    values = {
        'string_arg': 'some (not so) random string',
        'int_arg': 123,
        'int_arg_as_string': '123',
        'path_arg': '.',
        'list_arg': [123, 156, 1956],
        'list_of_tuples_arg': [[123, 156], [12, 14], [145, 140]],
    }
    yaml_file = NamedTemporaryFile(mode='w', delete=False)
    try:
        yaml.dump(values, yaml_file)
        yaml_file.close()
        parser = ArgumentsParser.from_files(toml_file_path, [], yaml_config=yaml_file.name)
        assert parser.user_values == values
    finally:
        os.unlink(yaml_file.name)
