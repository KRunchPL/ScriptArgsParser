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


def test_getattr(toml_file_path):
    parser = ArgumentsParser.from_files(toml_file_path, ['--cli-option-name', 'value'])
    assert parser.first_arg == 'value'


def test_getattr_wrong_attr(toml_file_path):
    parser = ArgumentsParser.from_files(toml_file_path, ['--cli-option-name', 'value'])
    with pytest.raises(AttributeError) as exc:
        parser.not_existing_arg
    assert 'not_existing_arg' in str(exc)
