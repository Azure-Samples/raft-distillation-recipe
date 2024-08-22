#!/bin/bash
set -e

dedup_env() {
    from=$1
    into=$2 
    local -A env_ary
    while IFS== read -r key value; do
        value=$(echo "$value" | sed 's/^ *"//' | sed 's/" *$//')
        env_ary[$key]=$value
    done <<EOM
$(cat $from $into)
EOM
    for key in ${!env_ary[@]}; do
        echo "${key}=\"${env_ary[${key}]}\""
    done | sort > $into
}

touch .env.state
dedup_env <(azd env get-values) .env.state
