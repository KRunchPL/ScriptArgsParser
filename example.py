from script_args_parser import ArgumentsParser


parser = ArgumentsParser.from_files('example-parameters.toml', yaml_config='example-config.yaml')
print(parser.arguments_values)
print(parser.name)
