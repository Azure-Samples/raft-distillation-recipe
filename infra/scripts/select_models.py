#!/usr/bin/env python

import click as click
import os
from rich.prompt import Prompt
import yaml
from pathlib import Path
from dotenv import load_dotenv
import subprocess

def azd_env_get_values():
    result = subprocess.run(['azd', 'env', 'get-values'], capture_output=True, text=True)
    return result.stdout

def load_azd_env():
    from io import StringIO
    env_values = azd_env_get_values()
    config = StringIO(env_values)
    load_dotenv(stream=config)

load_dotenv(".env")
load_dotenv(".env.state")
load_azd_env()

def read_ai_config():
    dir=cwd = os.path.dirname(os.path.realpath(__file__))
    path=Path(dir, "../azd/ai.yaml")
    with open(path, 'r') as aiConfigFile:
        aiConfig = yaml.safe_load(aiConfigFile)
    return aiConfig

def get_roles(aiConfig):
    deployments=aiConfig['deployments'] if 'deployments' in aiConfig else []
    roles = list(set([role for d in deployments for role in d['roles']]))
    roles.sort()
    return roles

def get_deployment_names(ai_config, role='teacher'):
    deployments=ai_config['deployments'] if 'deployments' in ai_config else []

    teacherDeployments = filter(lambda d: role in d['roles'], deployments)
    deploymentNames = map(lambda d: d['name'], teacherDeployments)
    return list(deploymentNames)

def first(array):
    return next(iter(array), None)

def select_model(role, names, default = None):
    import survey
    default_index = names.index(default) if default else 0
    index = survey.routines.select(f"Pick a {role} deployment name: ", options = names, index = default_index)
    deployment=names[index]
    return deployment

def decorators(decorators):
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f
    return decorator

def role_option(ai_config, role):
    return click.option(f'--{role}-deployment',
        type=click.Choice(get_deployment_names(ai_config=ai_config, role=role)),
        default=os.getenv(role_env_var_name(role)),
        help=f'The name of the {role} deployment to select.'
        )

def role_env_var_name(role):
    return f'{role.upper()}_DEPLOYMENT_NAME'

def azd_set_env(name, value):
    subprocess.run(['azd', 'env', 'set', name, value], shell=False, capture_output=True, text=True)

if __name__ == '__main__':

    # Read ai.yaml, collect roles and build a CLI option for each deployment model role
    ai_config = read_ai_config()
    roles = get_roles(ai_config)
    role_options = [role_option(ai_config, role) for role in roles]

    @click.command()
    @decorators(role_options)
    @click.option('--set-azd-env/--no-set-azd-env', default=True, help='Set the selected deployment names as environment variables.')
    def select_models(set_azd_env, **kwargs):
        values = []
        for arg_name, arg_value in kwargs.items():
            role = arg_name.replace('_deployment', '')
            env_var_name = role_env_var_name(role)
            names = get_deployment_names(ai_config, role)
            arg_value = select_model(role, names, default = arg_value)

            values.append((env_var_name, arg_value))

        if set_azd_env:
            click.echo()
            click.echo('Saving model selection to azd environment:')
            for name, value in values:
                click.echo(f' - {name}={value}')
                azd_set_env(name, value)

    select_models()
