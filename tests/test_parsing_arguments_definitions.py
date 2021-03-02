import os
from dataclasses import asdict
from tempfile import NamedTemporaryFile

import toml

from script_args_parser import ArgumentsParser


def assert_argument_values(name, mapping_dict, argument_dict):
    assert name == argument_dict['name']
    for k, v in mapping_dict.items():
        assert argument_dict[k] == v


def test_single_arg():
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
        parser = ArgumentsParser.from_files(toml_file.name, [])
        assert_argument_values('first_arg', mappings['first_arg'], asdict(parser.arguments[0]))
    finally:
        os.unlink(toml_file.name)


def test_multiple_args():
    mappings = {
        'first_arg': {
            'type': 'str',
            'description': 'Some fancy description',
            'cli_arg': '--cli-option-name',
            'env_var': 'ENV_VAR_NAME',
            'default_value': 'first_default'
        },
        'second_arg': {
            'type': 'tuple[int, bool, path]',
            'description': 'Some fancy description',
            'cli_arg': '--cli-option-name-for-tuple',
            'env_var': 'ENV_VAR_NAME_TUPLE',
            'default_value': '10 True .'
        }
    }
    toml_file = NamedTemporaryFile(mode='w', delete=False)
    try:
        toml.dump(mappings, toml_file)
        toml_file.close()
        parser = ArgumentsParser.from_files(toml_file.name, [])
        for i, mapping in enumerate(mappings.items()):
            name, mapp = mapping
            assert_argument_values(name, mapp, asdict(parser.arguments[i]))
    finally:
        os.unlink(toml_file.name)
