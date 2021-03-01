# Developer information

This file contains developer information for the repository.

## Python

Python part of the code should follow those base guidelines:
* used Python version is >=3.9.0;
* all the code should pass linting,
* every configuration should be put into setup.cfg file if possible.

### Dependencies

Project us using [Poetry](https://python-poetry.org/) to manage dependencies and building package.

To install Poetry on your system follow the guide here: [Poetry Installation](https://python-poetry.org/docs/#installation)

If you want to have virtualenv created in `.venv` folder in repository root, configure Poetry with following command:
```
poetry config virtualenvs.in-project true
```

To create a venv and install all dependencies run:
```
poetry install
```

For more usage see [Poetry Documentation](https://python-poetry.org/docs/)

### Tests

Tests should be written using pytest and put in the `tests` package. For dependencies handling see [Dependencies section](#dependencies).

#### Running tests

To run all the tests use the `pytest` command without any parameters in the main folder of the repo. This will start all the tests from the `tests` package and count coverage for every python file in the `script_args_parser` package.

Results of tests will be written to standard output. Coverage can be found in the `.coverage` file and the HTML version of the report will be put in `coverage-report` directory.

#### Configuration

Every configuration should be put into the `setup.cfg` file.

### Linting

For linting, this repository is using flake8 tool.

#### Running linter

To lint all python code use the `flake8` command without any parameters in the main folder of the repo.

Full linting report in HTML form will be available in `flake8-report` directory. Summary will be written to standard output.

#### Configuration

Every configuration should be put into the `setup.cfg` file.
