"""
Provides fixtures common for different test modules.
"""
import os
from collections.abc import Generator

import pytest

from script_args_parser.arguments import Argument


@pytest.fixture
def arguments_definition_with_env(arguments_definition: list[Argument], env_var_name: str) -> list[Argument]:
    """
    Set first argument default value and environment variable name.

    :param arguments_definition: definition of arguments to be modified
    :param env_var_name: name of environment variable to be used

    :return: the list given as arguments_definition parameter with first argument modified
    """
    arguments_definition[0].default_value = '10'
    arguments_definition[0].env_var = env_var_name
    return arguments_definition


@pytest.fixture
def env_var(env_var_name: str) -> Generator[str, None, None]:
    """
    Modify environment by adding a variable with provided name.

    :param env_var_name: name of environment variable to be added

    :yield: the name of environment variable that was added
    """
    old_environ = dict(os.environ)
    os.environ[env_var_name] = ''
    yield env_var_name
    os.environ.clear()
    os.environ.update(old_environ)
