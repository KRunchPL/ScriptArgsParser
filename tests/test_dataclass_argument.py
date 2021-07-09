from dataclasses import dataclass

import pytest

from script_args_parser.arguments import ListArgument
from script_args_parser.parser import Argument, ArgumentsParser
from script_args_parser.decorators import dataclass_argument


@dataclass_argument
@dataclass
class MyDataClass:
    value_1: str
    value_2: str

    def __eq__(self, o: object) -> bool:
        return isinstance(o, MyDataClass) and self.value_1 == o.value_1 and self.value_2 == o.value_2


@pytest.fixture
def single_arguments_definition():
    return [Argument(
        name='single',
        description='Single value',
        type='MyDataClass',
        cli_arg='--single-element',
    )]


@pytest.fixture
def list_arguments_definition():
    return [ListArgument(
        name='list',
        description='List value',
        type='list[MyDataClass]',
        cli_arg='--list-element',
    )]


def test_empty_list(list_arguments_definition):
    user_values = {
        'list': []
    }
    parser = ArgumentsParser(list_arguments_definition, user_values=user_values)
    assert parser.arguments_values['list'] == []


def test_list_single_value_as_list(list_arguments_definition):
    user_values = {
        'list': [
            ['1_something', '2_else']
        ]
    }
    parser = ArgumentsParser(list_arguments_definition, user_values=user_values)
    assert parser.list == [MyDataClass(value_1='1_something', value_2='2_else')]


def test_list_multiple_values_as_list(list_arguments_definition):
    user_values = {
        'list': [
            ['1_something', '2_else'],
            ['3_something', '4_else'],
        ]
    }
    parser = ArgumentsParser(list_arguments_definition, user_values=user_values)
    assert parser.list == [
        MyDataClass(value_1='1_something', value_2='2_else'),
        MyDataClass(value_1='3_something', value_2='4_else'),
    ]


def test_list_single_value_as_dict(list_arguments_definition):
    user_values = {
        'list': [
            {'value_2': '2_else', 'value_1': '1_something'},
        ]
    }
    parser = ArgumentsParser(list_arguments_definition, user_values=user_values)
    assert parser.list == [MyDataClass(value_1='1_something', value_2='2_else')]


def test_list_multiple_values_as_dict(list_arguments_definition):
    user_values = {
        'list': [
            {'value_2': '2_else', 'value_1': '1_something'},
            {'value_1': '3_something', 'value_2': '4_else'},
        ]
    }
    parser = ArgumentsParser(list_arguments_definition, user_values=user_values)
    assert parser.list == [
        MyDataClass(value_1='1_something', value_2='2_else'),
        MyDataClass(value_1='3_something', value_2='4_else'),
    ]


def test_object_as_list(single_arguments_definition):
    user_values = {
        'single': ['1_something', '2_else'],
    }
    parser = ArgumentsParser(single_arguments_definition, user_values=user_values)
    assert parser.single == MyDataClass(value_1='1_something', value_2='2_else')


def test_object_as_dict(single_arguments_definition):
    user_values = {
        'single': {'value_2': '2_else', 'value_1': '1_something'},
    }
    parser = ArgumentsParser(single_arguments_definition, user_values=user_values)
    assert parser.single == MyDataClass(value_1='1_something', value_2='2_else')
