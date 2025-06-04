#!/usr/bin/env bash

# Exit in case of error
set -e
# Print commands and their arguments as they are executed
set -x

# Run pytest with coverage measurement.
# --source=app specifies that coverage should be measured for the 'app' directory.
# -m pytest ensures that pytest is run as a module.
coverage run --source=app -m pytest

# Generate a text-based coverage report in the terminal.
# --show-missing will also list the line numbers of code that were not executed.
coverage report --show-missing

# Generate an HTML coverage report.
# The output will be in a directory named 'htmlcov' by default.
# The --title option sets the title of the HTML report.
# "${@-coverage}" attempts to use any arguments passed to this script in the title.
# For example, if the script is called with `backend/scripts/test.sh -k my_test`,
# the title might become "-k my_test-coverage". If no arguments are passed, it will be "-coverage".
coverage html --title "${@-coverage}"
