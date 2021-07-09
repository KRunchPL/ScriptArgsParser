import os
import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.arguments import ListArgument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_LIST_ENV_VALUE'


@pytest.fixture
def arguments_definition():
    return [ListArgument(
        name='list',
        description='List value',
        type='list[str]',
        cli_arg='--list-element',
    )]


@pytest.fixture
def arguments_definition_int():
    return [ListArgument(
        name='list',
        description='List value',
        type='list[int]',
        cli_arg='--list-element',
    )]


@pytest.fixture
def arguments_definition_int_with_env(arguments_definition_int, env_var_name):
    arguments_definition_int[0].default_value = '10'
    arguments_definition_int[0].env_var = env_var_name
    return arguments_definition_int


def test_no_value(arguments_definition):
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list'] is None


def test_single_value(arguments_definition):
    cli = ['--list-element', '123']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list'] == ['123']


def test_multiple_values(arguments_definition):
    cli = ['--list-element', '123', '--list-element', '1410']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list'] == ['123', '1410']


def test_single_empty_value(arguments_definition):
    cli = ['--list-element', '']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list'] == ['']


def test_multiple_empty_values(arguments_definition):
    cli = ['--list-element', '', '--list-element', '1410', '--list-element', '']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list'] == ['', '1410', '']


def test_switch_but_no_value(arguments_definition):
    cli = ['--list-element']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


@pytest.mark.parametrize('default_value, expected_list', [
    ('123', ['123']),
    ('123; 1410', ['123', '1410']),
    ('', ['']),
    (';1410;', ['', '1410', '']),
    ('; 1410;', ['', '1410', '']),
    (';1410 ;', ['', '1410', '']),
    (' ;1410;', ['', '1410', '']),
    (' ; 1410;', ['', '1410', '']),
    (' ;1410 ;', ['', '1410', '']),
    (';1410; ', ['', '1410', '']),
    ('; 1410; ', ['', '1410', '']),
    (';1410 ; ', ['', '1410', '']),
    (' ;1410; ', ['', '1410', '']),
    (' ; 1410; ', ['', '1410', '']),
    (' ;1410 ; ', ['', '1410', '']),
    (';', ['', '']),
    (';;;;;', ['', '', '', '', '', '']),
    (';     ;;;;', ['', '', '', '', '', '']),
    (' ; ;; ;;', ['', '', '', '', '', '']),
    ("'123'", ['123']),
    ("'123'; 1410", ['123', '1410']),
    ("''", ['']),
    (" '  c '  ", ['  c ']),
    (" '  c ' ;  ;   '  ' ", ['  c ', '', '  ']),
    ('"123"', ['123']),
    ('"123"; 1410', ['123', '1410']),
    ('""', ['']),
    (' "  c "  ', ['  c ']),
    (' "  c " ;  ;   "  " ', ['  c ', '', '  ']),
])
def test_no_cli_default_set(arguments_definition, default_value, expected_list):
    arguments_definition[0].default_value = default_value
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['list'] == expected_list


@pytest.mark.parametrize('default_value, expected_list', [
    ('123', [123]),
    ('123; 1410', [123, 1410]),
])
def test_no_cli_default_set_parsing(arguments_definition_int, default_value, expected_list):
    arguments_definition_int[0].default_value = default_value
    cli = []
    parser = ArgumentsParser(arguments_definition_int, cli)
    assert parser.arguments_values['list'] == expected_list


@pytest.mark.parametrize('env_value, expected_list', [
    ('123', ['123']),
    ('123; 1410', ['123', '1410']),
    ('', ['']),
    (';1410;', ['', '1410', '']),
    ('; 1410;', ['', '1410', '']),
    (';1410 ;', ['', '1410', '']),
    (' ;1410;', ['', '1410', '']),
    (' ; 1410;', ['', '1410', '']),
    (' ;1410 ;', ['', '1410', '']),
    (';1410; ', ['', '1410', '']),
    ('; 1410; ', ['', '1410', '']),
    (';1410 ; ', ['', '1410', '']),
    (' ;1410; ', ['', '1410', '']),
    (' ; 1410; ', ['', '1410', '']),
    (' ;1410 ; ', ['', '1410', '']),
    (';', ['', '']),
    (';;;;;', ['', '', '', '', '', '']),
    (';     ;;;;', ['', '', '', '', '', '']),
    (' ; ;; ;;', ['', '', '', '', '', '']),
    ("'123'", ['123']),
    ("'123'; 1410", ['123', '1410']),
    ("''", ['']),
    (" '  c '  ", ['  c ']),
    (" '  c ' ;  ;   '  ' ", ['  c ', '', '  ']),
    ('"123"', ['123']),
    ('"123"; 1410', ['123', '1410']),
    ('""', ['']),
    (' "  c "  ', ['  c ']),
    (' "  c " ;  ;   "  " ', ['  c ', '', '  ']),
])
def test_no_cli_env_set(arguments_definition_with_env, env_var, env_value, expected_list):
    os.environ[env_var] = env_value
    cli = []
    parser = ArgumentsParser(arguments_definition_with_env, cli)
    assert parser.arguments_values['list'] == expected_list


@pytest.mark.parametrize('env_value, expected_list', [
    ('123', [123]),
    ('123; 1410', [123, 1410]),
    ('123; "1410"; 2020', [123, 1410, 2020]),
    ('123; " 1410 "; 2020', [123, 1410, 2020]),
])
def test_no_cli_env_set_multiple_values(arguments_definition_int_with_env, env_var, env_value, expected_list):
    os.environ[env_var] = env_value
    cli = []
    parser = ArgumentsParser(arguments_definition_int_with_env, cli)
    assert parser.arguments_values['list'] == expected_list
