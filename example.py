from script_args_parser import ArgumentsParser


parser = ArgumentsParser.from_files('example-parameters.toml')
print(parser.arguments_values)
