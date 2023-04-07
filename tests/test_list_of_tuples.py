import os

import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.arguments import ListOfTuplesArgument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_LIST_TUPLES_ENV_VALUE'


@pytest.fixture
def arguments_definition():
    return [ListOfTuplesArgument(
        name='list_of_tuples',
        description='List of tuples value',
        type='list[tuple[str, int, str]]',
        cli_arg='--some-tuple',
    )]


@pytest.fixture
def arguments_definition_str():
    return [ListOfTuplesArgument(
        name='list_of_tuples',
        description='List of tuples value',
        type='list[tuple[str]]',
        cli_arg='--some-tuple',
    )]


@pytest.fixture
def arguments_definition_str_with_env(arguments_definition_str, env_var_name):
    arguments_definition_str[0].default_value = '10'
    arguments_definition_str[0].env_var = env_var_name
    return arguments_definition_str


def test_no_value(arguments_definition):
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list_of_tuples'] is None


def test_single_value(arguments_definition):
    cli: list[str] = ['--some-tuple', 'String Value', '123', 'Value']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list_of_tuples'] == [['String Value', 123, 'Value']]


def test_multiple_values(arguments_definition):
    cli: list[str] = [
        '--some-tuple', 'String Value', '123', 'Value',
        '--some-tuple', 'Another Value', '1410', 'Other Value',
    ]
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list_of_tuples'] == [
        ['String Value', 123, 'Value'],
        ['Another Value', 1410, 'Other Value']
    ]


def test_switch_but_no_value(arguments_definition):
    cli: list[str] = ['--some-tuple', 'String Value', '123', 'Value', '--some-tuple']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


def test_not_enough_values_cli(arguments_definition):
    cli: list[str] = ['--some-tuple', 'String Value', '123']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


def test_too_much_values_cli(arguments_definition):
    cli: list[str] = ['--some-tuple', 'String Value', '123', 'True', 'Other']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


@pytest.mark.parametrize('default_value, expected_list', [
    ('v1 123 v2', [['v1', 123, 'v2']]),
    ('v1 123 v2; v3 1410 v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 "1410" v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 " 1410 " v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2;   v3 1410   v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 1410 "v4 "', [['v1', 123, 'v2'], ['v3', 1410, 'v4 ']]),
])
def test_no_cli_default_set(arguments_definition, default_value, expected_list):
    arguments_definition[0].default_value = default_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list_of_tuples'] == expected_list


def test_no_cli_default_not_enough_values(arguments_definition):
    arguments_definition[0].default_value = 'v1 123 v2; v3 1410'
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition, cli)


def test_no_cli_default_too_much_values(arguments_definition):
    arguments_definition[0].default_value = 'v1 123 v2 xx; v3 1410 v4'
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition, cli)


def test_no_cli_default_set_single_empty_tuple(arguments_definition_str):
    arguments_definition_str[0].default_value = 'v1;;v2'
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_str, cli)
    assert parser.arguments_values['list_of_tuples'] == [['v1'], [''], ['v2']]


@pytest.mark.parametrize('env_value, expected_list', [
    ('v1 123 v2', [['v1', 123, 'v2']]),
    ('v1 123 v2; v3 1410 v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 "1410" v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 " 1410 " v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2;   v3 1410   v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 1410 "v4 "', [['v1', 123, 'v2'], ['v3', 1410, 'v4 ']]),
])
def test_no_cli_env_set(arguments_definition_with_env, env_var, env_value, expected_list):
    os.environ[env_var] = env_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_with_env, cli)
    assert parser.arguments_values['list_of_tuples'] == expected_list


def test_no_cli_env_not_enough_values(arguments_definition_with_env, env_var):
    os.environ[env_var] = 'v1 123 v2; v3 1410'
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition_with_env, cli)


def test_no_cli_env_too_much_values(arguments_definition_with_env, env_var):
    os.environ[env_var] = 'v1 123 v2 xx; v3 1410 v4'
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition_with_env, cli)


def test_no_cli_env_set_single_empty_tuple(arguments_definition_str_with_env, env_var):
    os.environ[env_var] = 'v1;;v2'
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_str_with_env, cli)
    assert parser.arguments_values['list_of_tuples'] == [['v1'], [''], ['v2']]
