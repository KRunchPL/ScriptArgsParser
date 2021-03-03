import os
from tempfile import NamedTemporaryFile

import pytest
import toml

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


def test_setattr(toml_file_path):
    parser = ArgumentsParser.from_files(toml_file_path, ['--cli-option-name', 'value'])
    assert parser.first_arg == 'value'
    parser.first_arg = 123
    assert parser.first_arg == 123
    assert parser.arguments_values['first_arg'] == 123
