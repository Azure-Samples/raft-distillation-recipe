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

load_azd_env()
load_dotenv(".env")
load_dotenv(".env.state")

def list_resource(resource_type):
    result = subprocess.run(['az', 'resource', 'list', '--out', 'json', '--resource-type', resource_type], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stdout)
    return json.loads(result.stdout)

def rest_call(method, url, version):
    result = subprocess.run(['az', 'rest', '--method', method, '--url', f"{url}?api-version={version}"], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stdout)
    return json.loads(result.stdout)

def list_cognitive_services_accounts():
    return list_resource("Microsoft.CognitiveServices/accounts")

def get_cognitive_services_account(resource_id):
    return rest_call("get", resource_id, "2023-05-01")

def get_deployments(resource_id):
    return rest_call("get", f"{resource_id}/deployments", "2023-05-01")['value']

def get_deployment_rate_limits(deployment):
    rates = {}
    deployment_properties = deployment['properties']
    if 'rateLimits' in deployment_properties:
        rateLimits = deployment_properties['rateLimits']
        rates = dict(groupby(rateLimits, lambda x: x['key']))
    return rates

def get_oai_endpoint(account):
    account_properties = account['properties']
    account_endpoints = account_properties['endpoints']
    return account_endpoints['OpenAI Language Model Instance API'] if 'OpenAI Language Model Instance API' in account_endpoints else None

def role_model_env_var_name(role):
    return f'{role.upper()}_MODEL_NAME'

def read_env_role(role):
    return {
        "role": role,
        "model_name": os.getenv(role_model_env_var_name(role)),
    }

@click.command()
def find_endpoints():

    config = read_ai_config()
    roles = get_roles(config.data)

    model_names = []
    for role_name in roles:
        click.echo(f"Role {role_name}")
        role = read_env_role(role_name)
        model_names.append(role['model_name'])

    click.echo(f"Searching for endpoints")
    accounts = list_cognitive_services_accounts()
    endpoints = {}
    for account_digest in accounts:
        click.echo(f"Found account: {account_digest['id']}")
        account = get_cognitive_services_account(account_digest['id'])
        oai_endpoint = get_oai_endpoint(account)
        #click.echo(f"OpenAI endpoint: {oai_endpoint}")
        deployments = get_deployments(account_digest['id'])
        for deployment in deployments:
            deployment_name = deployment['name']
            deployment_properties = deployment['properties']
            model = deployment_properties['model']
            model_name = model['name']
            rateLimits = get_deployment_rate_limits(deployment)
            sku = deployment['sku']
            sku_capacity = sku['capacity']
            sku_name = sku['name']

#            if model_name in model_names:
            if not model_name in endpoints.keys():
                endpoints[model_name] = []
            endpoints[model_name].append({
                "deployment_name": deployment_name,
                "sku_capacity": sku_capacity,
                "sku_name": sku_name,
                "endpoint": oai_endpoint
            })
            click.echo(f"Adding OpenAI endpoint: {model_name} {oai_endpoint} ({sku_capacity} {sku_name})")
#            else:
#                click.echo(f"Skipping OpenAI endpoint: {model_name} {oai_endpoint} ({sku_capacity} {sku_name})")

    model_list = []
    litellm_config = {
        "model_list": model_list,
        "litellm_settings": {
            "enable_azure_ad_token_refresh": "true"
        }
    }
    for model_name, endpoint_list in endpoints.items():
        for endpoint in endpoint_list:
            deployment_name = endpoint['deployment_name']
            api_base = endpoint['endpoint']
            tpm = int(endpoint['sku_capacity']) * 1000
            model_list.append({
                "model_name": model_name,
                "litellm_params": {
                    "model": f"azure/{deployment_name}",
                    "api_base": api_base,
                    "tpm": tpm
                }
            })
    click.echo(f"Writing litellm_config.yaml")
    with open('litellm_config.yaml', 'w') as f:
        yaml.dump(litellm_config, f)

if __name__ == '__main__':
    find_endpoints()
