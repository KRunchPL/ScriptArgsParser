import os
import pytest

from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[is_there]
description = "Switch"
type = "switch"
cli_arg = "--bool-switch"
"""


@pytest.fixture
def switch_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_SWITCH_ENV_VALUE'] = ''
    yield 'UT_SWITCH_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_switch_no_fallback(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['is_there'] is None


def test_single_switch(toml_definition):
    cli = ['--bool-switch']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['is_there'] is True


def test_multiple_switches(toml_definition):
    cli = ['--bool-switch', '--bool-switch']
    parser = ArgumentsParser(toml_definition, cli)
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
def test_switch_with_value(toml_definition, cli_value, expected_value):
    cli = ['--bool-switch', str(cli_value)]
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['is_there'] == expected_value


def test_no_switch_default_true(toml_definition):
    toml = toml_definition + 'default_value = "True"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['is_there'] is True


def test_no_switch_default_false(toml_definition):
    toml = toml_definition + 'default_value = "False"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['is_there'] is False


def test_no_switch_env_true(toml_definition, switch_env_var):
    os.environ[switch_env_var] = 'True'
    toml = toml_definition + f'default_value = "False"\nenv_var = "{switch_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['is_there'] is True


def test_no_switch_env_false(toml_definition, switch_env_var):
    os.environ[switch_env_var] = 'False'
    toml = toml_definition + f'default_value = "True"\nenv_var = "{switch_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    print(parser.arguments_values)
    assert parser.arguments_values['is_there'] is False
