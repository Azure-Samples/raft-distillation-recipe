import os
import yaml
from pathlib import Path

class Model:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def name(self):
        return self.data['name']

    @property
    def api(self):
        return self.data['api']

    @property
    def version(self):
        return self.data['version']

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
