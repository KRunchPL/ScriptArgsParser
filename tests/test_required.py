import os
from tempfile import NamedTemporaryFile

import pytest
import toml

from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_file_path_required():
    mappings = {
        'first_arg': {
            'type': 'str',
            'description': 'Some fancy description',
            'cli_arg': '--cli-option-name',
            'required': True,
            'env_var': 'UT_NOT_EXISITNG'
        }
    }
    toml_file = NamedTemporaryFile(mode='w', delete=False)
    try:
        toml.dump(mappings, toml_file)
        toml_file.close()
        yield toml_file.name
    finally:
        os.unlink(toml_file.name)


@pytest.fixture
def toml_file_path_not_required():
    mappings = {
        'first_arg': {
            'type': 'str',
            'description': 'Some fancy description',
            'cli_arg': '--cli-option-name',
            'required': False,
        }
    }
    toml_file = NamedTemporaryFile(mode='w', delete=False)
    try:
        toml.dump(mappings, toml_file)
        toml_file.close()
        yield toml_file.name
    finally:
        os.unlink(toml_file.name)


def test_is_required_is_present(toml_file_path_required):
    parser = ArgumentsParser.from_files(toml_file_path_required, ['--cli-option-name', 'value'])
    assert parser.first_arg == 'value'


def test_is_required_not_present(toml_file_path_required):
    with pytest.raises(RuntimeError):
        ArgumentsParser.from_files(toml_file_path_required, [])


def test_not_required_is_present(toml_file_path_not_required):
    parser = ArgumentsParser.from_files(toml_file_path_not_required, ['--cli-option-name', 'value'])
    assert parser.first_arg == 'value'


def test_not_required_not_present(toml_file_path_not_required):
    parser = ArgumentsParser.from_files(toml_file_path_not_required, [])
    assert parser.first_arg is None
