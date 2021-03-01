import os
import pytest
from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[integer]
description = "Integer value"
type = "int"
cli_arg = "--some-integer"
"""


@pytest.fixture
def integer_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_INTEGER_ENV_VALUE'] = ''
    yield 'UT_INTEGER_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['integer'] is None


def test_single_value(toml_definition):
    cli = ['--some-integer', '123']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['integer'] == 123


def test_multiple_values(toml_definition):
    cli = ['--some-integer', '123', '--some-integer', '1410']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['integer'] == 1410


def test_switch_but_no_value(toml_definition):
    cli = ['--some-integer']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


def test_no_cli_default_set(toml_definition):
    toml = toml_definition + 'default_value = "123"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['integer'] == 123


def test_no_cli_env_set(toml_definition, integer_env_var):
    os.environ[integer_env_var] = '1410'
    toml = toml_definition + f'default_value = "123"\nenv_var = "{integer_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['integer'] == 1410


def test_value_not_parsable(toml_definition):
    cli = ['--some-integer', '123_not']
    with pytest.raises(ValueError):
        ArgumentsParser(toml_definition, cli)


def test_default_value_not_parsable(toml_definition):
    toml = toml_definition + 'default_value = "123_not"'
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(toml, cli)


def test_env_value_not_parsable(toml_definition, integer_env_var):
    os.environ[integer_env_var] = '1410_not'
    toml = toml_definition + f'default_value = "123"\nenv_var = "{integer_env_var}"'
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(toml, cli)


def test_value_empty_string(toml_definition):
    cli = ['--some-integer', '']
    with pytest.raises(ValueError):
        ArgumentsParser(toml_definition, cli)


def test_default_value_empty_string(toml_definition):
    toml = toml_definition + 'default_value = ""'
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(toml, cli)


def test_env_value_empty_string(toml_definition, integer_env_var):
    os.environ[integer_env_var] = ''
    toml = toml_definition + f'default_value = "123"\nenv_var = "{integer_env_var}"'
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(toml, cli)
