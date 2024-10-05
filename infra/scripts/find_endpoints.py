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

def get_az_ad_signed_in_user():
    result = subprocess.run(['az', 'ad', 'signed-in-user', 'show', "--query", "id"], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stdout)
    return json.loads(result.stdout)

def get_role_assignments(user_id, scope, role):
    result = subprocess.run([
        'az', 'role', 'assignment', 'list', 
        '--assignee', user_id, 
        '--out', 'json',
        '--scope', scope,
        '--include-inherited',
        '--role', role
        ], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stdout)
    return json.loads(result.stdout)

def has_role_assignment(user_id, scope, role):
    assignments = get_role_assignments(user_id, scope, role)
    return len(assignments) > 0

openai_user_role_id = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' # Cognitive Services OpenAI User

def do_scan_azure():
    click.echo(f"Scanning Azure for OpenAI endpoints")
    accounts = list_cognitive_services_accounts()
    endpoints = {}
    signed_in_user_id = get_az_ad_signed_in_user()
    for account_digest in accounts:
        account_id = account_digest['id']
        if has_role_assignment(signed_in_user_id, account_id, openai_user_role_id):
            click.echo(f"OpenAI resource with role assignment: {account_id}")
            account = get_cognitive_services_account(account_id)
            oai_endpoint = get_oai_endpoint(account)
            #click.echo(f"OpenAI endpoint: {oai_endpoint}")
            deployments = get_deployments(account_id)
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
                    "tpm": tpm,
                    "tenant_id": "HACK"
                }
            })

    return litellm_config

def export_proxy_endpoints():
    config = read_ai_config()
    roles = get_roles(config.data)

    model_names = []
    env_values = []
    for role_name in roles:
        click.echo(f"Exporting env vars for role {role_name}")
        role = read_env_role(role_name)
        model_name = role['model_name']
        model_names.append(model_name)
        env_values.append((f"{role_name.upper()}_OPENAI_BASE_URL", "http://localhost:4000/"))
        env_values.append((f"{role_name.upper()}_OPENAI_API_KEY", "DUMMY"))
        env_values.append((f"{role_name.upper()}_OPENAI_DEPLOYMENT", model_name))

    with open('.env.scan', 'w') as f:
        for name, value in env_values:
            f.write(f'{name}={value}\n')
    #        azd_set_env(name, value)


@click.command()
@click.option('--scan-azure/--no-scan-azure', default=True, help='Whether to scan Azure searching for OpenAI endpoints.')
@click.option('--set-azd-env/--no-set-azd-env', default=True, help='Set the selected deployment names as azd environment variables.')
def find_endpoints(scan_azure, set_azd_env):

    if scan_azure:
        litellm_config = do_scan_azure()

        click.echo(f"Writing litellm_config.yaml")
        with open('litellm_config.yaml', 'w') as f:
            yaml.dump(litellm_config, f)

    if set_azd_env:
        export_proxy_endpoints()

if __name__ == '__main__':
    find_endpoints()
