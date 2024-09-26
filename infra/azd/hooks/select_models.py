import click as click
import os
from rich.prompt import Prompt
import yaml
from pathlib import Path

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

def get_deployment_names(ai_config, role='teacher'):
    deployments=ai_config['deployments'] if 'deployments' in ai_config else []

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

if __name__ == '__main__':

    ai_config = read_ai_config()
    roles = get_roles(ai_config)
    role_options = [role_option(ai_config, role) for role in roles]

    @click.command()
    @decorators(role_options)
    def select_models(**kwargs):
        for arg_name, arg_value in kwargs.items():
            if not arg_value:
                role = arg_name.replace('_deployment', '')
                names = get_deployment_names(ai_config, role)
                if len(names) == 1:
                    arg_value = names[0]
                else:
                    arg_value = select_model(role, names)
            click.echo(f'{role_env_var_name(role)}={arg_value}')

    select_models()
