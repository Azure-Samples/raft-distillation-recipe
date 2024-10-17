#!/usr/bin/env python

import os
import rich_click as click
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv
import subprocess
from itertools import groupby
from ai_config import *
from azd_utils import *

def role_model_env_var_name(role):
    return f'{role.upper()}_MODEL_NAME'

def role_deployment_name_env_var_name(role):
    return f'{role.upper()}_DEPLOYMENT_NAME'

def read_env_role(role):
    return {
        "role": role,
        "model_name": os.getenv(role_model_env_var_name(role)),
        "deployment_name": os.getenv(role_deployment_name_env_var_name(role)),
    }

def redact_secret(key, value):
    """Redact a value from the logs if the key indicates that the value contains a keyword such as KEY or SECRET."""
    if "KEY" in key or "SECRET" in key:
        return value[:4] + "*" * (len(value) - 4)
    return value

def update_env_file(env_file, kv_tuples):
    """Update the env file with the key and value."""
    from pathlib import Path
    from dotenv import dotenv_values

    data = {}
    if Path(env_file).exists() and Path(env_file).is_file():
        data = dotenv_values(env_file)

    for key, value in kv_tuples:
        data[key] = value
        click.echo(f"Updating env file {env_file} with {key}={redact_secret(key, value)}")

    with open(env_file, "w") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")

@click.command()
def export_proxy_endpoints():

    load_azd_env()
    load_dotenv(".env")
    load_dotenv(".env.state")

    config = read_ai_config()
    roles = get_roles(config.data)

    env_values = []
    for role_name in roles:
        click.echo(f"Exporting env vars for role {role_name}")
        role = read_env_role(role_name)
        model_name = role['model_name']
        deployment_name = role['deployment_name']
        model_version = config.descriptors[deployment_name].model.version
        model_id = f"{model_name}@{model_version}"
        env_values.append((f"{role_name.upper()}_OPENAI_BASE_URL", "http://localhost:4000/"))
        env_values.append((f"{role_name.upper()}_OPENAI_API_KEY", "DUMMY"))
        env_values.append((f"{role_name.upper()}_OPENAI_DEPLOYMENT", model_id))

    update_env_file(".env.state", env_values)

if __name__ == '__main__':
    export_proxy_endpoints()
