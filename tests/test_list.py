import os
import pytest
from script_args_parser import ArgumentsParser


@pytest.fixture
def toml_definition():
    return """
[list]
description = "List value"
type = "list[int]"
cli_arg = "--list-element"
"""


@pytest.fixture
def toml_definition_str():
    return """
[list]
description = "List value"
type = "list[str]"
cli_arg = "--list-element"
"""


@pytest.fixture
def list_env_var():
    old_environ = dict(os.environ)
    os.environ['UT_LIST_ENV_VALUE'] = ''
    yield 'UT_LIST_ENV_VALUE'
    os.environ.clear()
    os.environ.update(old_environ)


def test_no_value(toml_definition):
    cli = []
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['list'] is None


def test_single_value(toml_definition):
    cli = ['--list-element', '123']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['list'] == [123]


def test_multiple_values(toml_definition):
    cli = ['--list-element', '123', '--list-element', '1410']
    parser = ArgumentsParser(toml_definition, cli)
    assert parser.arguments_values['list'] == [123, 1410]


def test_switch_but_no_value(toml_definition):
    cli = ['--list-element']
    with pytest.raises(SystemExit):
        ArgumentsParser(toml_definition, cli)


@pytest.mark.skip('Not implemented')
def test_no_cli_default_set_single_value(toml_definition):
    toml = toml_definition + 'default_value = "123"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == [123]


@pytest.mark.skip('Not implemented')
def test_no_cli_default_set_multiple_values(toml_definition):
    toml = toml_definition + 'default_value = "123, 1410"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == [123, 1410]


@pytest.mark.skip('Not implemented')
def test_no_cli_env_set_single_value(toml_definition, list_env_var):
    os.environ[list_env_var] = '123'
    toml = toml_definition + f'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == [123]


@pytest.mark.skip('Not implemented')
def test_no_cli_env_set_multiple_values(toml_definition, list_env_var):
    os.environ[list_env_var] = '123, 1410'
    toml = toml_definition + f'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == [123, 1410]


def test_single_empty_value(toml_definition_str):
    cli = ['--list-element', '']
    parser = ArgumentsParser(toml_definition_str, cli)
    assert parser.arguments_values['list'] == ['']


def test_multiple_empty_values(toml_definition_str):
    cli = ['--list-element', '', '--list-element', '1410', '--list-element', '']
    parser = ArgumentsParser(toml_definition_str, cli)
    assert parser.arguments_values['list'] == ['', '1410', '']


@pytest.mark.skip('Not implemented')
def test_no_cli_default_set_single_empty_value(toml_definition_str):
    toml = toml_definition_str + 'default_value = ""'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == ['']


@pytest.mark.skip('Not implemented')
def test_no_cli_default_set_multiple_empty_values(toml_definition_str):
    toml = toml_definition_str + 'default_value = ", 1410, "'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == ['', '1410', '']


@pytest.mark.skip('Not implemented')
def test_no_cli_env_set_single_empty_value(toml_definition_str, list_env_var):
    os.environ[list_env_var] = ''
    toml = toml_definition_str + f'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == ['']


@pytest.mark.skip('Not implemented')
def test_no_cli_env_set_multiple_empty_values(toml_definition_str, list_env_var):
    os.environ[list_env_var] = ', 1410, '
    toml = toml_definition_str + f'default_value = "10"\nenv_var = "{list_env_var}"'
    cli = []
    parser = ArgumentsParser(toml, cli)
    assert parser.arguments_values['list'] == ['', '1410', '']
