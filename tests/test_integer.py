import os
import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.parser import Argument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_INTEGER_ENV_VALUE'


@pytest.fixture
def arguments_definition():
    return [Argument(
        name='integer',
        description='Integer value',
        type='int',
        cli_arg='--some-integer',
    )]


def test_no_value(arguments_definition):
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['integer'] is None


def test_value_empty_string(arguments_definition):
    cli = ['--some-integer', '']
    with pytest.raises(ValueError):
        ArgumentsParser(arguments_definition, cli)


def test_single_value(arguments_definition):
    cli = ['--some-integer', '123']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['integer'] == 123


def test_multiple_values(arguments_definition):
    cli = ['--some-integer', '123', '--some-integer', '1410']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['integer'] == 1410


def test_switch_but_no_value(arguments_definition):
    cli = ['--some-integer']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


def test_value_not_parsable(arguments_definition):
    cli = ['--some-integer', '123_not']
    with pytest.raises(ValueError):
        ArgumentsParser(arguments_definition, cli)


def test_no_cli_default_set_empty_string(arguments_definition):
    arguments_definition[0].default_value = ''
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(arguments_definition, cli)


def test_no_cli_default_set(arguments_definition):
    arguments_definition[0].default_value = '123'
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['integer'] == 123


def test_no_cli_default_set_not_parsable(arguments_definition):
    arguments_definition[0].default_value = '123_not'
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(arguments_definition, cli)


def test_no_cli_env_set_empty_string(arguments_definition_with_env, env_var):
    os.environ[env_var] = ''
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(arguments_definition_with_env, cli)


def test_no_cli_env_set(arguments_definition_with_env, env_var):
    os.environ[env_var] = '1410'
    cli = []
    parser = ArgumentsParser(arguments_definition_with_env, cli)
    assert parser.arguments_values['integer'] == 1410


def test_no_cli_env_set_not_parsable(arguments_definition_with_env, env_var):
    os.environ[env_var] = '1410_not'
    cli = []
    with pytest.raises(ValueError):
        ArgumentsParser(arguments_definition_with_env, cli)
