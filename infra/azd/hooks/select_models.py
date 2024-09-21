import click as click
import os
from rich.prompt import Prompt
import yaml
from pathlib import Path

def get_deployment_names(role='teacher'):
    dir=cwd = os.path.dirname(os.path.realpath(__file__))
    path=Path(dir, "../ai.yaml")
    with open(path, 'r') as aiConfigFile:
        aiConfig = yaml.safe_load(aiConfigFile)
        deployments=aiConfig['deployments'] if 'deployments' in aiConfig else []

    teacherDeployments = filter(lambda d: role in d['roles'], deployments)
    deploymentNames = map(lambda d: d['name'], teacherDeployments)
    return list(deploymentNames)

def first(array):
    return next(iter(array), None)

if __name__ == '__main__':

    teacher_deployment_names = get_deployment_names('teacher')
    baseline_deployment_names = get_deployment_names('baseline')

    @click.command()
    @click.option('--teacher-deployment',
        prompt='Teacher deployment name',
        type=click.Choice(teacher_deployment_names),
        default=os.getenv('TEACHER_DEPLOYMENT_NAME', first(teacher_deployment_names)),
        help='The name of the teacher deployment to select.'
        )
    @click.option('--baseline-deployment',
        prompt='Baseline deployment name',
        type=click.Choice(baseline_deployment_names),
        default=os.getenv('BASELINE_DEPLOYMENT_NAME', first(baseline_deployment_names)),
        help='The name of the baseline deployment to select.'
        )
    def select_models(teacher_deployment, baseline_deployment):
        click.echo(f'Teacher deployment {teacher_deployment}')

    select_models()
