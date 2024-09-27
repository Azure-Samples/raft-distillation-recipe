#!/bin/bash

env_file=".env.state"
echo "Exporting environment variables to ${env_file}"

dedup_env() {
    from=$1
    into=$2 
    local -A env_ary
    while IFS== read -r key value; do
        value=$(echo "$value" | sed 's/^ *"//' | sed 's/" *$//')
        env_ary[$key]=$value
    done <<EOM
$(cat $into $from | grep -v '^#' | grep -v "^\ *$")
EOM
    for key in ${!env_ary[@]}; do
        echo "${key}=${env_ary[${key}]}"
    done | sort > $into
}

touch ${env_file}

# Export all azd env vars except DEPLOYMENTS which requires a special processing
dedup_env <(azd env get-values | grep -v "DEPLOYMENTS=") ${env_file}

# Process the azd DEPLOYMENTS env var and export the models env vars
dedup_env <(azd env get-value DEPLOYMENTS | ./infra/azd/hooks/export_models.py) ${env_file}
