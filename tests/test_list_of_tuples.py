import os
import pytest
from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[list_of_tuples]
description = "List of tuples value"
type = "list[tuple[str, int, str]]"
cli_arg = "--some-tuple"
"""


@pytest.fixture
def list_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_LIST_TUPLES_ENV_VALUE'] = ''
    yield 'UT_LIST_TUPLES_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['list_of_tuples'] is None


def test_single_value(toml_definition):
    cli = ['--some-tuple', 'String Value', '123', 'Value']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['list_of_tuples'] == [['String Value', 123, 'Value']]


def test_multiple_values(toml_definition):
    cli = [
        '--some-tuple', 'String Value', '123', 'Value',
        '--some-tuple', 'Another Value', '1410', 'Other Value',
    ]
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['list_of_tuples'] == [
        ['String Value', 123, 'Value'],
        ['Another Value', 1410, 'Other Value']
    ]


def test_switch_but_no_value(toml_definition):
    cli = ['--some-tuple', 'String Value', '123', 'Value', '--some-tuple']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


def test_not_enough_values_cli(toml_definition):
    cli = ['--some-tuple', 'String Value', '123']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


def test_too_much_values_cli(toml_definition):
    cli = ['--some-tuple', 'String Value', '123', 'True', 'Other']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


@pytest.mark.parametrize('default_value, expected_list', [
    ('v1 123 v2', [['v1', 123, 'v2']]),
    ('v1 123 v2; v3 1410 v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 \\"1410\\" v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 \\" 1410 \\" v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2;   v3 1410   v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 1410 \\"v4 \\"', [['v1', 123, 'v2'], ['v3', 1410, 'v4 ']]),
])
def test_no_cli_default_set(toml_definition, default_value, expected_list):
    toml = toml_definition + f'default_value = "{default_value}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list_of_tuples'] == expected_list


def test_no_cli_default_not_enough_values(toml_definition):
    toml = toml_definition + 'default_value = "v1 123 v2; v3 1410"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_no_cli_default_too_much_values(toml_definition):
    toml = toml_definition + 'default_value = "v1 123 v2 xx; v3 1410 v4"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


@pytest.mark.parametrize('env_value, expected_list', [
    ('v1 123 v2', [['v1', 123, 'v2']]),
    ('v1 123 v2; v3 1410 v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 "1410" v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 " 1410 " v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2;   v3 1410   v4', [['v1', 123, 'v2'], ['v3', 1410, 'v4']]),
    ('v1 123 v2; v3 1410 "v4 "', [['v1', 123, 'v2'], ['v3', 1410, 'v4 ']]),
])
def test_no_cli_env_set(toml_definition, list_env_var, env_value, expected_list):
    os.environ[list_env_var] = env_value
    toml = toml_definition + f'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list_of_tuples'] == expected_list


def test_no_cli_env_not_enough_values(toml_definition, list_env_var):
    os.environ[list_env_var] = 'v1 123 v2; v3 1410'
    toml = toml_definition + 'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_no_cli_env_too_much_values(toml_definition, list_env_var):
    os.environ[list_env_var] = 'v1 123 v2 xx; v3 1410 v4'
    toml = toml_definition + 'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_no_cli_env_set_single_empty_tuple(list_env_var):
    toml = f"""
[list_of_tuples]
description = "List of tuples value"
type = "list[tuple[str]]"
cli_arg = "--some-tuple"
env_var = "{list_env_var}"
"""
    os.environ[list_env_var] = 'v1;;v2'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list_of_tuples'] == [['v1'], [''], ['v2']]
