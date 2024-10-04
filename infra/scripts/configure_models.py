#!/usr/bin/env python

import os
import rich_click as click
import yaml
from pathlib import Path
from dotenv import load_dotenv
import subprocess

def azd_env_get_values():
    result = subprocess.run(['azd', 'env', 'get-values'], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to get azd environment values because of: " + result.stdout)
    return result.stdout

def load_azd_env():
    from io import StringIO
    env_values = azd_env_get_values()
    config = StringIO(env_values)
    load_dotenv(stream=config)

load_azd_env()
load_dotenv(".env")
load_dotenv(".env.state")


class Model:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def name(self):
        return self.data['name']

    @property
    def api(self):
        return self.data['api']

class Descriptor:
    def __init__(self, data) -> None:
        self.data = data

    def is_supported_in_regions(self, regions):
        common = set(self.regions & set(regions))
        return len(common) > 0
    
    @property
    def regions(self):
        return set(self.data['regions'])

    @property
    def model(self):
        return Model(self.data['model'])

class Descriptors:
    def __init__(self, ai_config):
        self.ai_config = ai_config

    def __getitem__(self, key):
        models = self.ai_config.data['deployments'] if 'deployments' in self.ai_config.data else []
        val = next(filter(lambda d: d['name'] == key, models))
        if not val:
            raise Exception(f"Model {key} not found")
        return Descriptor(val)

class AiConfig:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def descriptors(self):
        return Descriptors(self)


def read_ai_config():
    dir = os.path.dirname(os.path.realpath(__file__))
    path=Path(dir, "../azd/ai.yaml")
    with open(path, 'r') as aiConfigFile:
        aiConfig = yaml.safe_load(aiConfigFile)
    return AiConfig(aiConfig)

def get_roles(aiConfig):
    deployments=aiConfig['deployments'] if 'deployments' in aiConfig else []
    roles = list(set([role for d in deployments for role in d['roles']]))
    roles.sort()
    return roles

def get_regions(aiConfig):
    deployments=aiConfig['deployments'] if 'deployments' in aiConfig else []
    regions = set([region for d in deployments for region in d['regions']])
    return regions

def get_deployment_names(ai_config, regions, role='teacher'):
    deployments=ai_config['deployments'] if 'deployments' in ai_config else []

    deployments = filter(lambda d: role in d['roles'] and Descriptor(d).is_supported_in_regions(regions), deployments)
    deploymentNames = map(lambda d: d['name'], deployments)
    return list(deploymentNames)

def first(array):
    return next(iter(array), None)

def select_model(role, names, default = None):
    import survey
    default_index = names.index(default) if default and default in names else 0
    index = survey.routines.select(f"Pick a {role} deployment name: ", options = names, index = default_index)
    deployment=names[index]
    return deployment

def select_region(regions, default = None):
    import survey
    regions = list(regions)
    default_index = regions.index(default) if default and default in regions else 0
    index = survey.routines.select(f"Pick a region: ", options = regions, index = default_index)
    region=regions[index]
    return region

def decorators(decorators):
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f
    return decorator

def role_option(ai_config, regions, role):
    return click.option(f'--{role}-deployment',
        type=click.Choice(get_deployment_names(ai_config=ai_config, regions=regions, role=role)),
        default=os.getenv(role_deployment_env_var_name(role)),
        help=f'The name of the {role} deployment to select.'
        )

def role_deployment_env_var_name(role):
    return f'{role.upper()}_DEPLOYMENT_NAME'

def role_model_env_var_name(role):
    return f'{role.upper()}_MODEL_NAME'

def role_model_api_env_var_name(role):
    return f'{role.upper()}_MODEL_API'

def azd_set_env(name, value):
    subprocess.run(['azd', 'env', 'set', name, value], shell=False, capture_output=True, text=True)

if __name__ == '__main__':

    # Read ai.yaml, collect roles and build a CLI option for each deployment model role
    ai_config = read_ai_config()
    roles = get_roles(ai_config.data)
    regions = get_regions(ai_config.data)
    role_options = [role_option(ai_config.data, regions, role) for role in roles]

    @click.command()
    @decorators(role_options)
    @click.option('--set-azd-env/--no-set-azd-env', default=True, help='Set the selected deployment names as azd environment variables.')
    @click.option('--region', '-r', multiple=True, default=None, help='Restricts which regions to consider for models. Defaults to all regions.')
    def select_models(set_azd_env, region,  **kwargs):
        click.echo(f"Select which models to use. Each selection narrows down future selections based on the region:")
        values = []
        regions = get_regions(ai_config.data)
        if region:
            regions = regions & set(region)
        for arg_name, arg_value in kwargs.items():
            role = arg_name.replace('_deployment', '')
            names = get_deployment_names(ai_config.data, regions, role)
            arg_value = select_model(role, names, default = arg_value)
            descriptor = ai_config.descriptors[arg_value]
            regions = regions & descriptor.regions

            values.append((role_deployment_env_var_name(role), arg_value))
            values.append((role_model_env_var_name(role), descriptor.model.name))
            values.append((role_model_api_env_var_name(role), descriptor.model.api))

        region = select_region(regions, os.getenv("AZURE_LOCATION"))
        values.append(("AZURE_LOCATION", region))

        if set_azd_env:
            click.echo()
            click.echo('Saving model selection to azd environment:')
            for name, value in values:
                click.echo(f' - {name}={value}')
                azd_set_env(name, value)

    select_models()
