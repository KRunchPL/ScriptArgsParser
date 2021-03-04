# Script Arguments Parser

This library is meant to provide an easy way to consume arguments for scripts in more complex scenarios without writing too much code.

## Why something more?

In Python there are a lot of ways to consume cli parameters, starting from built-in parsers finishing at libraries like docopt. But unfortunately during my adventure I encountered a few problems that were not solvable just by using one of them. Few of those problems:

* get values from multiple sources: cli, config file, environment variable, default;
* convert given variable according to argument definition;
* all argument information (cli option, fallback env var, conversion type, default value etc.) defined in one place;
* definitions written outside the code, so the script is kept clean and simple;
* more complex conversion types build in.

## Main features

* Parameters defined in both human- and computer-readable format outside of the code, in one place
* Argument values converted to given format (predefined or custom)
* Config file fallback
* Environmental variable fallback
* Default values
* Human readable errors

## Usage

One of the goals of this library was to minimize amount of the code. Therefore whole usage looks like this:

```python
from script_args_parser import ArgumentsParser

args = ArgumentsParser.from_files('example-parameters.toml', yaml_config='example-config.yaml')
print(args.name)
print(args.age)
```

Above script will read arguments definition from `example-parameters.toml` and try to read their values in following order:

1. from cli options,
2. from config file (`example-config.yaml` in example),
3. from environment variables,
4. default values.

In any argument does not have value defined it will be None, unless it is required, so it will raise an exception.

When all values are established, parser will convert them to specified type.

### Arguments definition

The list of script arguments is provided in toml file. Example argument can look like this:
```toml
[name]
description = "Some fancy description"  # required
type = "str"   # required
cli_arg = "--cli-opt"  # required
env_var = "ENV_VAR_NAME"
required = false
default_value = "I got you"
```

#### description **(mandatory)**

Human readable description of an argument.

#### type **(mandatory)**

Parser will use this field to convert value of the argument from string to one that is specified.

Some more complex types are also changing the way cli options are parsed.

For detailed description of possible values and their meaning, see [Types section](#types).

#### cli_arg **(mandatory)**

Name of the cli option throught which value can be set.

#### env_var

Name of environment variable that will be used to read value if not specified by CLI or config file.

For the format used by more complex types see [Types section](#types).

#### required

By default False. If set to true, the parser will raise an error if value will not be found anywhere.

Can be specified as boolean value (true, false) or by string ('true', 'false', 'yes', 'no', '1', '0').

#### default_value

Value that will be used if not specified by CLI, config file or environment variable.

For the format used by more complex types see [Types section](#types).

### Types

This is the list of built-in types supported.

#### String

Type field value: `str`

No special operations are performed.

#### Integer

Type field value: `int`

Value will be parsed to integer, if not possible, exception will be raised.

#### Boolean

Type field value: `bool`

Some strings has been defined to be matched to specific values (case insensitive):

* True can be specified as: true, yes, 1;
* False can be specified as: false, no, 0;

All other values will be converted to bool using Python rules.

#### Switch

Type field value: `switch`

Behaves in the same way as `bool` but additionaly cli option can be passed without an argument and will be considered True.

#### Path

Type field value: `path`

Will be converted into `pathlib.Path` object. Worth noticing is that empty string will be equivalent of current directory.

#### List

Type field value: `list[<simple type>]`

Will produce a list of elements with given simple types (any that was described above).

When this type is specified, multiple cli options should be used to pass list elements:
```
script.py --child-name John --child-name David
```

In default value or environment variable use semicolon to split values:
```
default_value = "John; David; 'Some;Very;Strange;Name'"
```

#### Tuple

Type field value: `tuple[<simple type>, <optional simple type>, ...]`

Example type field value: `tuple[str]`, `tuple[int, str, bool]`.

Will produce a list with given amount of values of simple types elements.

When this type is specified, cli options should be used once but with multiple values. For  `tuple[str, str, str]`
```
script.py --all-my-names John Maria "De'naban"
```

In default value or environment variable separate values with space:
```
default_value = "John Maria "De'naban"
```

#### List of tuples

Type field value: `list[tuple[<simple type>, <optional simple type>, ...]]`

Combining list and tuple types. Will produce a list of lists.

For cli use:
```
script.py --child John 16 --child David 18 --child Maria 21
```

For default values and enviroment variables use:
```
default_value = "John 16; David 18; Maria 21"
```

Above examples for `list[tuple[str, int]]` will produce:

```python
[['John', 16], ['David', 18], ['Maria', 21]]
```

## Planned work

Work that still need to be done prior to v1.0

- [x] Default and envs for list
- [x] Default and envs for tuple
- [x] Default and envs for list of tuples
- [x] Add more list of tuples tests
- [x] Add path type (with tests)
- [x] Create from path
- [x] Support config file
- [x] Document possible types
- [ ] Write some complex test cases
- [ ] Allow non-cli arguments
- [ ] Add logging
- [ ] Allow custom argument types
- [ ] Generate usage
- [ ] Error handling
- [ ] TOML file validation
- [ ] CI/CD

## Contributing

Right now I would like to finish what I planned by myself and release version 1.0. If you have any suggestions or you have found bugs, feel free to submit an issue and I will take a look at it as soon as possible.

## Development

Development documentation can be found [here](README-DEV.md)
