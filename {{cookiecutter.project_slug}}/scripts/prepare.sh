#! /usr/bin/env sh

# Exit in case of error
set -e

# poetry update generate new poetry.lock file with updated possible dependencies
poetry update

# generate requirements.txt file [Optional with --dev]
./make-requirements.sh
