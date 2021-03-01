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
