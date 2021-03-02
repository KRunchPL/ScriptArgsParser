import os
from pathlib import Path

import pytest

from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[path]
description = "Path value"
type = "path"
cli_arg = "--file-path"
"""


@pytest.fixture
def path_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_PATH_ENV_VALUE'] = ''
    yield 'UT_PATH_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['path'] is None


def test_single_value(toml_definition):
    cli = ['--file-path', './LICENSE']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['path'] == Path('./LICENSE')


def test_multiple_values(toml_definition):
    cli = ['--file-path', './LICENSE', '--file-path', './README.md']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['path'] == Path('./README.md')


def test_switch_but_no_value(toml_definition):
    cli = ['--file-path']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


def test_no_cli_default_set(toml_definition):
    toml = toml_definition + 'default_value = "./LICENSE"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['path'] == Path('./LICENSE')


def test_no_cli_env_set(toml_definition, path_env_var):
    os.environ[path_env_var] = './LICENSE'
    toml = toml_definition + f'default_value = "Some default"\nenv_var = "{path_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['path'] == Path('./LICENSE')


def test_value_empty_string(toml_definition):
    cli = ['--file-path', '']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['path'] == Path('.')


def test_default_value_empty_string(toml_definition):
    toml = toml_definition + 'default_value = ""'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['path'] == Path('.')


def test_env_value_empty_string(toml_definition, path_env_var):
    os.environ[path_env_var] = ''
    toml = toml_definition + f'default_value = ""\nenv_var = "{path_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['path'] == Path('.')
