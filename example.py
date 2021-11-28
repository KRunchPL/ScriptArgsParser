"""
Usage example.
"""

from dataclasses import dataclass

from script_args_parser import ArgumentsParser, dataclass_argument


@dataclass_argument
@dataclass
class MyDataClass:
    """
    Example dataclass used as argument.
    """

    value_1: str
    value_2: str


parser = ArgumentsParser.from_files('example-parameters.toml', yaml_config='example-config.yaml')
print(parser.arguments_values)
print(f'Favorite colors: {parser.favorite_colors}')
