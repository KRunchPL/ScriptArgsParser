# Script Arguments Parser

This library is meant to provide an easy way to consume arguments for scripts in more complex scenarios without writing too much code.

## Why something more?

In Python there are a lot of ways to consume cli parameters, starting from built-in parsers finishing at libraries like docopt. But unfortunately during my adventure I encountered a few problems that were not solvable just by using one of them. Few of those problems:

* use environment variable as a fallback when cli option not specified;
* convert given variable according to argument definition;
* all argument information (cli option, fallback env var, conversion type, default value etc.) defined in one place;
* definitions written outside the code, so the script is kept clean and simple;
* more complex conversion types build in.

## Main features

* Parameters defined in both human- and computer-readable format outside of the code, in one place
* Argument values converted to given format (predefined or custom)
* Environmental variable fallback
* Default values
* Human readable errors

## Planned work

Work that still need to be done prior to v1.0

[ ] Add more list of tuples tests
[ ] Write complex test cases
[ ] Allow non-cli arguments
[ ] Document possible types
[ ] Add path type
[ ] Add logging
[ ] Allow custom argument types
[ ] Generate usage
[ ] Error handling
[ ] Default and envs for list
[ ] Default and envs for tuple
[ ] TOML file validation
[ ] Create from path
[ ] CI/CD

## Contributing

Right now I would like to finish what I planned by myself and release version 1.0. If you have any suggestions or you have found bugs, feel free to submit an issue and I will take a look at it as soon as possible.

## Development

Development documentation can be found [here](README-DEV.md)
