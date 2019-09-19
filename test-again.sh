#! /usr/bin/env bash

# pre-requisite: 
# - container for training-project running
# - which means run test.sh script at least once before using this script

# this script produces the same result as test.sh, but faster
# because it rsyncs the latest modification into testing-project
# instead of removing it and generating it again

# Exit in case of error
set -e

# push new src files
rsync -av \{\{cookiecutter.project_slug\}\}/backend testing-project/

# restart backend container
docker-compose -f testing-project/docker-stack.yml restart backend

# run tests
docker-compose -f testing-project/docker-stack.yml exec -T backend-tests /tests-start.sh $*
