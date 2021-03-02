import os

import pytest


@pytest.fixture
def arguments_definition_with_env(arguments_definition, env_var_name):
    arguments_definition[0].default_value = '10'
    arguments_definition[0].env_var = env_var_name
    return arguments_definition


@pytest.fixture
def env_var(env_var_name):
    old_environ = dict(os.environ)
    os.environ[env_var_name] = ''
    yield env_var_name
    os.environ.clear()
    os.environ.update(old_environ)
