import click as click
import os
from rich.prompt import Prompt
import yaml
from pathlib import Path
from functools import cache

@cache
def read_ai_config():
    dir=cwd = os.path.dirname(os.path.realpath(__file__))
    path=Path(dir, "../ai.yaml")
    with open(path, 'r') as aiConfigFile:
        aiConfig = yaml.safe_load(aiConfigFile)
    return aiConfig

def get_roles(aiConfig):
    deployments=aiConfig['deployments'] if 'deployments' in aiConfig else []
    roles = set([role for d in deployments for role in d['roles']])
    return roles

@cache
def get_deployment_names(role='teacher'):
    aiConfig = read_ai_config()
    deployments=aiConfig['deployments'] if 'deployments' in aiConfig else []

    teacherDeployments = filter(lambda d: role in d['roles'], deployments)
    deploymentNames = map(lambda d: d['name'], teacherDeployments)
    return list(deploymentNames)

def first(array):
    return next(iter(array), None)

def select_model(role, names):
    import survey
    index = survey.routines.select(f"Pick a {role} deployment name: ", options = names)
    deployment=names[index]
    return deployment

def yad(decorators):
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f
    return decorator

def role_env_var_name(role):
    return f'{role.upper()}_DEPLOYMENT_NAME'

if __name__ == '__main__':

    ai_config = read_ai_config()
    roles = get_roles(ai_config)

    teacher_deployment_names = get_deployment_names(role='teacher')
    baseline_deployment_names = get_deployment_names(role='baseline')

    deployment_names = []

    options = [
        click.option(f'--{role}-deployment',
            type=click.Choice(get_deployment_names(role=role)),
            default=os.getenv(role_env_var_name(role)),
            help=f'The name of the {role} deployment to select.'
            ) for role in roles]

    @click.command()
    @yad(options)
    def select_models(**kwargs):
        for arg_name, arg_value in kwargs.items():
            if not arg_value:
                role = arg_name.replace('_deployment', '')
                names = get_deployment_names(role=role)
                if len(names) == 1:
                    arg_value = names[0]
                else:
                    arg_value = select_model(role, names)
            click.echo(f'{role_env_var_name(role)}={arg_value}')

    select_models()
