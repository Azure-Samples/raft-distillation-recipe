#!/bin/sh
echo "Loading azd .env file from current environment"

# Use the `get-values` azd command to retrieve environment variables from the `.env` file
while IFS='=' read -r key value; do
    value=$(echo "$value" | sed 's/^"//' | sed 's/"$//')
    export "$key=$value"
done <<EOF
$(azd env get-values) 
EOF

DIR="$( cd "$( dirname "$0" )/../../tests" && pwd )"

echo 'Running tests'
python -m pytest --rootdir=${DIR}
