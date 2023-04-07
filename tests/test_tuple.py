import os

import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.arguments import TupleArgument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_TUPLE_ENV_VALUE'


@pytest.fixture
def arguments_definition_single_str():
    return [TupleArgument(
        name='tuple',
        description='Tuple value',
        type='tuple[str]',
        cli_arg='--some-tuple',
    )]


@pytest.fixture
def arguments_definition_triple_str():
    return [TupleArgument(
        name='tuple',
        description='Tuple value',
        type='tuple[str, str, str]',
        cli_arg='--some-tuple',
    )]


@pytest.fixture
def arguments_definition_str_int_bool():
    return [TupleArgument(
        name='tuple',
        description='Tuple value',
        type='tuple[str, int, bool]',
        cli_arg='--some-tuple',
    )]


@pytest.fixture
def arguments_definition_single_str_with_env(arguments_definition_single_str, env_var_name):
    arguments_definition_single_str[0].default_value = '10'
    arguments_definition_single_str[0].env_var = env_var_name
    return arguments_definition_single_str


@pytest.fixture
def arguments_definition_triple_str_with_env(arguments_definition_triple_str, env_var_name):
    arguments_definition_triple_str[0].default_value = '10'
    arguments_definition_triple_str[0].env_var = env_var_name
    return arguments_definition_triple_str


@pytest.fixture
def arguments_definition_str_int_bool_with_env(arguments_definition_str_int_bool, env_var_name):
    arguments_definition_str_int_bool[0].default_value = '10'
    arguments_definition_str_int_bool[0].env_var = env_var_name
    return arguments_definition_str_int_bool


def test_no_value(arguments_definition_single_str):
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_single_str, cli)
    assert parser.arguments_values['tuple'] is None


def test_single_value(arguments_definition_single_str):
    cli: list[str] = ['--some-tuple', 'String Value']
    parser = ArgumentsParser(arguments_definition_single_str, cli)
    assert parser.arguments_values['tuple'] == ['String Value']


def test_switch_but_no_value(arguments_definition_single_str):
    cli: list[str] = ['--some-tuple']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition_single_str, cli)


def test_not_enough_values_cli(arguments_definition_triple_str):
    cli: list[str] = ['--some-tuple', 'String Value', '123']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition_triple_str, cli)


def test_too_much_values_cli(arguments_definition_triple_str):
    cli: list[str] = ['--some-tuple', 'String Value', '123', 'True', 'Other']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition_triple_str, cli)


@pytest.mark.parametrize('cli_values, expected_list', [
    (['String Value', '123', 'True'], ['String Value', 123, True]),
    (['', '123', 'True'], ['', 123, True]),
    (['', '123', ''], ['', 123, False]),
])
def test_parsing_values(arguments_definition_str_int_bool, cli_values, expected_list):
    cli: list[str] = ['--some-tuple'] + cli_values
    parser = ArgumentsParser(arguments_definition_str_int_bool, cli)
    assert parser.arguments_values['tuple'] == expected_list


@pytest.mark.parametrize('default_value, expected_value', [
    ('String_Value', 'String_Value'),
    ('"String Value"', 'String Value'),
    ("'String Value'", 'String Value'),
])
def test_no_cli_default_single_value(arguments_definition_single_str, default_value, expected_value):
    arguments_definition_single_str[0].default_value = default_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_single_str, cli)
    assert parser.arguments_values['tuple'] == [expected_value]


def test_no_cli_default_not_enough_values(arguments_definition_triple_str):
    arguments_definition_triple_str[0].default_value = "'Some default' 123"
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition_triple_str, cli)


def test_no_cli_default_too_much_values(arguments_definition_triple_str):
    arguments_definition_triple_str[0].default_value = "'Some default', 123, True, Other"
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition_triple_str, cli)


@pytest.mark.parametrize('default_value, expected_list', [
    ("'String Value' 123 True", ['String Value', 123, True]),
    ("'' 123 True", ['', 123, True]),
    ("'' '123' ''", ['', 123, False]),
])
def test_no_cli_default_parsing_values(arguments_definition_str_int_bool, default_value, expected_list):
    arguments_definition_str_int_bool[0].default_value = default_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_str_int_bool, cli)
    assert parser.arguments_values['tuple'] == expected_list


@pytest.mark.parametrize('env_value, expected_value', [
    ('String_Value', 'String_Value'),
    ('"String Value"', 'String Value'),
    ("'String Value'", 'String Value'),
    ('', ''),
])
def test_no_cli_env_single_value(
    arguments_definition_single_str_with_env, env_var, env_value, expected_value
):
    os.environ[env_var] = env_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_single_str_with_env, cli)
    assert parser.arguments_values['tuple'] == [expected_value]


def test_no_cli_env_not_enough_values(arguments_definition_triple_str_with_env, env_var):
    os.environ[env_var] = "'Some default' 123"
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition_triple_str_with_env, cli)


def test_no_cli_env_too_much_values(arguments_definition_triple_str_with_env, env_var):
    os.environ[env_var] = "'Some default', 123, True, Other"
    cli: list[str] = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(arguments_definition_triple_str_with_env, cli)


@pytest.mark.parametrize('env_value, expected_list', [
    ("'String Value' 123 True", ['String Value', 123, True]),
    ("'' 123 True", ['', 123, True]),
    ("'' '123' ''", ['', 123, False]),
])
def test_no_cli_env_parsing_values(
    arguments_definition_str_int_bool_with_env, env_var, env_value, expected_list
):
    os.environ[env_var] = env_value
    cli: list[str] = []
    parser = ArgumentsParser(arguments_definition_str_int_bool_with_env, cli)
    assert parser.arguments_values['tuple'] == expected_list
