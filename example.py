from script_args_parser import ArgumentsParser


with open('example-parameters.toml', 'r') as params_file:
    toml_definition = params_file.read()

parser = ArgumentsParser(toml_definition)
print(parser.arguments_values)
