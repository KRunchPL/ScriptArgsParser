import os
from pathlib import Path

import pytest

from script_args_parser import ArgumentsParser
from script_args_parser.arguments import PathArgument
from tests.common_fixtures import *  # noqa: F401, F403


@pytest.fixture
def env_var_name():
    return 'UT_PATH_ENV_VALUE'


@pytest.fixture
def arguments_definition():
    return [PathArgument(
        name='path',
        description='Path value',
        type='path',
        cli_arg='--file-path',
    )]


@pytest.fixture
def arguments_definition_with_parent():
    return [
        PathArgument(
            name='p_path',
            description='Parent path value',
            type='path',
            cli_arg='--parent-path',
            default_value='my_parent',
        ),
        PathArgument(
            name='path',
            description='Path value',
            type='path',
            cli_arg='--file-path',
            parent_path='p_path',
        ),
    ]


def test_no_value(arguments_definition):
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['path'] is None


def test_value_empty_string(arguments_definition):
    cli = ['--file-path', '']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['path'] == Path('.')


@pytest.mark.parametrize('cli_value, expected_value', [
    ('./LICENSE', Path('./LICENSE')),
    ('', Path('.')),
])
def test_single_value(arguments_definition, cli_value, expected_value):
    cli = ['--file-path', cli_value]
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['path'] == expected_value


def test_multiple_values(arguments_definition):
    cli = ['--file-path', './LICENSE', '--file-path', './README.md']
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['path'] == Path('./README.md')


def test_switch_but_no_value(arguments_definition):
    cli = ['--file-path']
    with pytest.raises(SystemExit):
        ArgumentsParser(arguments_definition, cli)


@pytest.mark.parametrize('default_value, expected_value', [
    ('./LICENSE', Path('./LICENSE')),
    ('', Path('.')),
])
def test_no_cli_default_set(arguments_definition, default_value, expected_value):
    arguments_definition[0].default_value = default_value
    cli = []
    parser = ArgumentsParser(arguments_definition, cli)
    assert parser.arguments_values['path'] == expected_value


@pytest.mark.parametrize('env_value, expected_value', [
    ('./LICENSE', Path('./LICENSE')),
    ('', Path('.')),
])
def test_no_cli_env_set(arguments_definition_with_env, env_var, env_value, expected_value):
    os.environ[env_var] = env_value
    cli = []
    parser = ArgumentsParser(arguments_definition_with_env, cli)
    assert parser.arguments_values['path'] == expected_value


@pytest.mark.parametrize('cli_value, expected_value', [
    ('./LICENSE', Path('my_parent/LICENSE')),
    ('', Path('my_parent')),
])
def test_single_value_with_parent(arguments_definition_with_parent, cli_value, expected_value):
    cli = ['--file-path', cli_value]
    parser = ArgumentsParser(arguments_definition_with_parent, cli)
    assert parser.arguments_values['path'] == expected_value
