#!/bin/sh -e
# Print commands and their arguments as they are executed
set -x

# Run ruff to check for linting issues in 'app' and 'scripts' directories and automatically fix them.
ruff check app scripts --fix
# Run ruff to format the code in 'app' and 'scripts' directories.
ruff format app scripts
