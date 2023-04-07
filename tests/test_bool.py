import os

import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.arguments import Argument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_BOOL_ENV_VALUE'


@pytest.fixture
def arguments_definition():
    return [Argument(
        name='bool',
        description='Bool value',
        type='bool',
        cli_arg='--some-bool',
    )]


def test_no_value(arguments_definition):
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['bool'] is None


@pytest.mark.parametrize('cli_value, expected_value', [
    ('True', True),
    ('1', True),
    ('False', False),
    ('0', False),
    ('123', True),
    ('None', True),
    ('some string', True),
    ('', False),
])
def test_single_value(arguments_definition, cli_value, expected_value):
    cli = ['--some-bool', cli_value]
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['bool'] == expected_value


@pytest.mark.parametrize('first_cli_value, second_cli_value, expected_value', [
    ('True', 'False', False),
    ('False', 'False', False),
    ('False', 'True', True),
    ('True', 'True', True),
])
def test_multiple_values(arguments_definition, first_cli_value, second_cli_value, expected_value):
    cli = ['--some-bool', first_cli_value, '--some-bool', second_cli_value]
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['bool'] == expected_value


def test_switch_but_no_value(arguments_definition):
    cli = ['--some-bool']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


@pytest.mark.parametrize('default_value, expected_value', [
    ('True', True),
    ('1', True),
    ('False', False),
    ('0', False),
    ('123', True),
    ('None', True),
    ('some string', True),
    ('', False),
])
def test_no_cli_default_set(arguments_definition, default_value, expected_value):
    arguments_definition[0].default_value = default_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['bool'] == expected_value


@pytest.mark.parametrize('env_value, expected_value', [
    ('True', True),
    ('1', True),
    ('False', False),
    ('0', False),
    ('123', True),
    ('None', True),
    ('some string', True),
    ('', False),
])
def test_no_cli_env_set(arguments_definition_with_env, env_var, env_value, expected_value):
    os.environ[env_var] = env_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_with_env, cli)
    assert parser.arguments_values['bool'] == expected_value
