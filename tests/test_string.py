import os
import pytest
from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[string]
description = "String value"
type = "str"
cli_arg = "--some-string"
"""


@pytest.fixture
def string_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_STRING_ENV_VALUE'] = ''
    yield 'UT_STRING_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['string'] is None


def test_single_value(toml_definition):
    cli = ['--some-string', 'String Value']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['string'] == 'String Value'


def test_multiple_values(toml_definition):
    cli = ['--some-string', 'String Value', '--some-string', 'New Value']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['string'] == 'New Value'


def test_switch_but_no_value(toml_definition):
    cli = ['--some-string']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


def test_no_cli_default_set(toml_definition):
    toml = toml_definition + 'default_value = "Some default"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['string'] == 'Some default'


def test_no_cli_env_set(toml_definition, string_env_var):
    os.environ[string_env_var] = 'Some from env'
    toml = toml_definition + f'default_value = "Some default"\nenv_var = "{string_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['string'] == 'Some from env'


def test_value_empty_string(toml_definition):
    cli = ['--some-string', '']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['string'] == ''


def test_default_value_empty_string(toml_definition):
    toml = toml_definition + 'default_value = ""'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['string'] == ''


def test_env_value_empty_string(toml_definition, string_env_var):
    os.environ[string_env_var] = ''
    toml = toml_definition + f'default_value = ""\nenv_var = "{string_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['string'] == ''
