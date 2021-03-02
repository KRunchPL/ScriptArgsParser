import os
import pytest
from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[tuple]
description = "Tuple value"
cli_arg = "--some-tuple"
"""


@pytest.fixture
def toml_definition_single_str(toml_definition):
    return toml_definition+'type = "tuple[str]"\n'


@pytest.fixture
def toml_definition_str_int_bool(toml_definition):
    return toml_definition+'type = "tuple[str, int, bool]"\n'


@pytest.fixture
def toml_definition_triple_str(toml_definition):
    return toml_definition+'type = "tuple[str, str, str]"\n'


@pytest.fixture
def tuple_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_TUPLE_ENV_VALUE'] = ''
    yield 'UT_TUPLE_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition_single_str):
    cli = []
    parser = ArgumentsParser(toml_definition_single_str, cli)
    assert parser.arguments_values['tuple'] is None


def test_single_value(toml_definition_single_str):
    cli = ['--some-tuple', 'String Value']
    parser = ArgumentsParser(toml_definition_single_str, cli)
    assert parser.arguments_values['tuple'] == ['String Value']


def test_multiple_values_tuple(toml_definition_str_int_bool):
    cli = ['--some-tuple', 'String Value', '123', 'True']
    parser = ArgumentsParser(toml_definition_str_int_bool, cli)
    assert parser.arguments_values['tuple'] == ['String Value', 123, True]


def test_switch_but_no_value(toml_definition_single_str):
    cli = ['--some-tuple']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition_single_str, cli)


def test_no_cli_default_single_value(toml_definition_single_str):
    toml = toml_definition_single_str + 'default_value = "\'Some default\'"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['Some default']


def test_no_cli_default_multiple_values_tuple(toml_definition_str_int_bool):
    toml = toml_definition_str_int_bool + 'default_value = "\'Some default\' 123 True"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['Some default', 123, True]


def test_no_cli_env_single_empty_value(toml_definition_single_str, tuple_env_var):
    os.environ[tuple_env_var] = ''
    toml = toml_definition_single_str + f'default_value = "Some default"\nenv_var = "{tuple_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['']


def test_no_cli_env_single_value(toml_definition_single_str, tuple_env_var):
    os.environ[tuple_env_var] = '"Some from env"'
    toml = toml_definition_single_str + f'default_value = "Some default"\nenv_var = "{tuple_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['Some from env']


def test_no_cli_env_multiple_values_tuple(toml_definition_str_int_bool, tuple_env_var):
    os.environ[tuple_env_var] = '"Some from env" 123 True'
    toml = toml_definition_str_int_bool + f'default_value = "Some default"\nenv_var = "{tuple_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['Some from env', 123, True]


def test_not_enough_values_cli(toml_definition_str_int_bool):
    cli = ['--some-tuple', 'String Value', '123']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition_str_int_bool, cli)


def test_not_enough_values_default(toml_definition_str_int_bool):
    toml = toml_definition_str_int_bool + 'default_value = "\'Some default\' 123"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_not_enough_values_env(toml_definition_str_int_bool, tuple_env_var):
    os.environ[tuple_env_var] = '"Some from env" 123'
    toml = toml_definition_str_int_bool + f'env_var = "{tuple_env_var}"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_too_much_values_cli(toml_definition_str_int_bool):
    cli = ['--some-tuple', 'String Value', '123', 'True', 'Other']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition_str_int_bool, cli)


def test_too_much_values_default(toml_definition_str_int_bool):
    toml = toml_definition_str_int_bool + 'default_value = "\'Some default\', 123, True, Other"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_too_much_values_env(toml_definition_str_int_bool, tuple_env_var):
    os.environ[tuple_env_var] = '"Some from env" 123 True Other'
    toml = toml_definition_str_int_bool + f'env_var = "{tuple_env_var}"'
    cli = []
    with pytest.raises(RuntimeError):
        ArgumentsParser(toml, cli)


def test_multiple_empty_values_tuple(toml_definition_triple_str):
    cli = ['--some-tuple', '', '123', '']
    parser = ArgumentsParser(toml_definition_triple_str, cli)
    assert parser.arguments_values['tuple'] == ['', '123', '']


def test_no_cli_default_multiple_empty_values_tuple(toml_definition_triple_str):
    toml = toml_definition_triple_str + 'default_value = "\'\' 123 \'\' "'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['', '123', '']


def test_no_cli_env_multiple_empty_values_tuple(toml_definition_triple_str, tuple_env_var):
    os.environ[tuple_env_var] = '"" 123 "" '
    toml = toml_definition_triple_str + f'default_value = "Some default"\nenv_var = "{tuple_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['tuple'] == ['', '123', '']
