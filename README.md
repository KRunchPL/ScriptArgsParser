# Script Arguments Parser

This library is meant to provide an easy way to consume arguments for scripts in more complex scenarios without writing too much code.

[![license](https://img.shields.io/github/license/KRunchPL/script-args-parser.svg)](https://github.com/KRunchPL/script-args-parser/blob/master/LICENSE)
[![latest release](https://img.shields.io/github/release/KRunchPL/script-args-parser.svg)](https://github.com/KRunchPL/script-args-parser/releases/latest) [![latest release date](https://img.shields.io/github/release-date/KRunchPL/script-args-parser.svg)](https://github.com/KRunchPL/script-args-parser/releases)

[![PyPI version](https://img.shields.io/pypi/v/script-args-parser)](https://pypi.org/project/script-args-parser/) [![Python](https://img.shields.io/pypi/pyversions/script-args-parser)](https://pypi.org/project/script-args-parser/)

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

If any argument does not have value defined it will be None, unless it is required, so it will raise an exception.

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

##### Post operations

Additional parameter `post_operations` can be used. It stores the expression that will be evaluated after the value is read. The result of evaluation will be used as a value. The `{value}` token in expression will be substituted with the value provided by the user.

For example when a program requires value in seconds, but the user will always want to specify minutes the `post_operations` can be: `"{value} * 60"`.

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

##### Parent path

Additional parameter `parent_path` can be used. It shall contain a name of another path argument. Current path will be prepended with the value of `parent_path`.

With given toml file the default value of `picture_name` will be `'images/beautiful.jpg'`.

```toml
[pictures_folder]
description = "Path to folder with pictures"
type = "path"
cli_arg = "--pictures-folder"
default = "./images"

[picture_name]
description = "Name of a picture file"
type = "path"
cli_arg = "--picture-name"
parent_path = "pictures_folder"
default = "beautiful.jpg"
```

It is possible to make a hierarchy of paths, but keep in mind that the arguments are evaluated in order that they are defined in toml file, so with below toml file the `picture_name` will have value `'the_best_user\beautiful.jpg'` even though `user_folder` will be `pictures_folder\user_folder`.

```toml
[pictures_folder]
description = "Path to folder with pictures"
type = "path"
cli_arg = "--pictures-folder"
default = "./images"

[picture_name]
description = "Name of a picture file"
type = "path"
cli_arg = "--picture-name"
parent_path = "user_folder"
default = "beautiful.jpg"

[user_folder]
description = "Name of a user folder file"
type = "path"
cli_arg = "--user-folder"
parent_path = "pictures_folder"
default = "the_best_user"
```

#### List

Type field value: `list[<simple type>]`

Will produce a list of elements with given simple types (any that was described above).

When this type is specified, multiple cli options should be used to pass list elements:

```shell script
script.py --child-name John --child-name David
```

In default value or environment variable use semicolon to split values:

```toml
default_value = "John; David; 'Some;Very;Strange;Name'"
```

#### Tuple

Type field value: `tuple[<simple type>, <optional simple type>, ...]`

Example type field value: `tuple[str]`, `tuple[int, str, bool]`.

Will produce a list with given amount of values of simple types elements.

When this type is specified, cli options should be used once but with multiple values. For  `tuple[str, str, str]`

```shell script
script.py --all-my-names John Maria "De'naban"
```

In default value or environment variable separate values with space:

```toml
default_value = "John Maria "De'naban"
```

#### List of tuples

Type field value: `list[tuple[<simple type>, <optional simple type>, ...]]`

Combining list and tuple types. Will produce a list of lists.

For cli use:

```shell script
script.py --child John 16 --child David 18 --child Maria 21
```

For default values and enviroment variables use:

```toml
default_value = "John 16; David 18; Maria 21"
```

Above examples for `list[tuple[str, int]]` will produce:

```python
[['John', 16], ['David', 18], ['Maria', 21]]
```

#### Dataclass argument

Type field value: `<name of the dataclass>`

Parses a list or a dict to user defined dataclass.

In order for the dataclass to be used it has to be decorated with `script_args_parser.decorators.dataclass_argument`.

With given Python code and toml definition:

```python
@dataclass_argument
@dataclass
class MyDataClass:
    value_1: str
    value_2: str
```

```toml
[two_values]
description = "Some two string values"
type = "MyDataClass"
cli_arg = "--two-values"
```

The following yaml input files can be used

```yaml
two_values:
  - first_value
  - second value
```

or

```yaml
two_values:
  value_1: first_value
  value_2: second value
```

The type can also be used as a list type argument like:

```toml
[two_values]
description = "Some two string values"
type = "list[MyDataClass]"
cli_arg = "--two-values"
```

NOTE: Currently cli or env values are not supported for this type.

## Planned work

Work that still need to be done prior to v1.0

* [x] Default and envs for list
* [x] Default and envs for tuple
* [x] Default and envs for list of tuples
* [x] Add more list of tuples tests
* [x] Add path type (with tests)
* [x] Create from path
* [x] Support config file
* [x] Document possible types
* [ ] Add support for env and cli values for dataclass type
* [ ] Write some complex test cases
* [ ] Allow non-cli arguments
* [ ] Add logging
* [ ] Allow custom argument types
* [ ] Generate usage
* [ ] Error handling
* [ ] TOML file validation
* [ ] CI/CD

## Contributing

Right now I would like to finish what I planned by myself and release version 1.0. If you have any suggestions or you have found bugs, feel free to submit an issue and I will take a look at it as soon as possible. To save your and my time on discussions please provide a good description for them.

## Development

Development documentation can be found [here](README-DEV.md)
