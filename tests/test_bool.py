import os
import pytest
from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[bool]
description = "Bool value"
type = "bool"
cli_arg = "--some-bool"
"""


@pytest.fixture
def bool_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_BOOL_ENV_VALUE'] = ''
    yield 'UT_BOOL_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
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
def test_single_value(toml_definition, cli_value, expected_value):
    cli = ['--some-bool', cli_value]
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['bool'] == expected_value


@pytest.mark.parametrize('first_cli_value, second_cli_value, expected_value', [
    ('True', 'False', False),
    ('False', 'False', False),
    ('False', 'True', True),
    ('True', 'True', True),
])
def test_multiple_values(toml_definition, first_cli_value, second_cli_value, expected_value):
    cli = ['--some-bool', first_cli_value, '--some-bool', second_cli_value]
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['bool'] == expected_value


def test_switch_but_no_value(toml_definition):
    cli = ['--some-bool']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


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
def test_no_cli_default_set(toml_definition, default_value, expected_value):
    toml = toml_definition + f'default_value = "{default_value}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
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
def test_no_cli_env_set(toml_definition, bool_env_var, env_value, expected_value):
    os.environ[bool_env_var] = env_value
    toml = toml_definition + f'default_value = "Some default"\nenv_var = "{bool_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['bool'] == expected_value
