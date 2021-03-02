import os
import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.parser import Argument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_SWITCH_ENV_VALUE'


@pytest.fixture
def arguments_definition():
    return [Argument(
        name='is_there',
        description='Switch',
        type='switch',
        cli_arg='--bool-switch',
    )]


def test_no_value(arguments_definition):
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['is_there'] is None


def test_single_switch(arguments_definition):
    cli = ['--bool-switch']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['is_there'] is True


def test_multiple_switches(arguments_definition):
    cli = ['--bool-switch', '--bool-switch']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['is_there'] is True


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
def test_switch_with_value(arguments_definition, cli_value, expected_value):
    cli = ['--bool-switch', str(cli_value)]
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['is_there'] == expected_value


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
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['is_there'] == expected_value


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
    cli = []
    parser = ArgumentsParser(arguments_definition_with_env, cli)
    assert parser.arguments_values['is_there'] == expected_value
