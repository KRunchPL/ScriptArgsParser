# Scripts Arguments Parser

This library is meant to provide an easy way to consume arguments for scripts in more complex scenarios.

## Why something more?

In Python there are a lot of ways to consume cli parameters, even apart from built-in parsers. But unfortunately during my adventure I encountered a few problems that were not solvable just by using one of them. Therefore this library has been created.

## Main features

* Parameters are defined in both human- and computer-readable format
* Argument values are being converted to given format (predefined or custom)
* Environmental variable fallback is supported
* Default value is supported
* Human readable errors are returned

## Planned work

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
