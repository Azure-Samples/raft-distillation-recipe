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
    deployment=teacher_deployment_names[index]
    return deployment

def yad(decorators):
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f
    return decorator

if __name__ == '__main__':

    teacher_deployment_names = get_deployment_names(role='teacher')
    baseline_deployment_names = get_deployment_names(role='baseline')

    deployment_names = []

    roles = ['teacher', 'baseline']
    options = [
        click.option(f'--{role}-deployment',
            type=click.Choice(get_deployment_names(role=role)),
            default=os.getenv(f'{role.upper()}_DEPLOYMENT_NAME'),
            help=f'The name of the {role} deployment to select.'
            ) for role in roles]

    @click.command()
    @yad(options)
    def select_models(baseline_deployment, teacher_deployment):
        if not teacher_deployment:
            teacher_deployment = select_model('teacher', teacher_deployment_names)
        if not baseline_deployment:
            baseline_deployment = select_model('baseline', baseline_deployment_names)

        click.echo(f'Teacher deployment {teacher_deployment}')
        click.echo(f'Baseline deployment {baseline_deployment}')

    select_models()
