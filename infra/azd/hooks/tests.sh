#!/bin/sh
echo "Loading azd .env file from current environment"

DIR="$( cd "$( dirname "$0" )/../../tests" && pwd )"

echo 'Running tests'
python -m pytest --rootdir=${DIR}
