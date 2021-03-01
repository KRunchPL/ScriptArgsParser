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
