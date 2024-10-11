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

def role_deployment_name_env_var_name(role):
    return f'{role.upper()}_DEPLOYMENT_NAME'

def read_env_role(role):
    return {
        "role": role,
        "model_name": os.getenv(role_model_env_var_name(role)),
        "deployment_name": os.getenv(role_deployment_name_env_var_name(role)),
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

def bold(text):
    return click.style(text, bold=True)

def red(text):
    return click.style(text, bold=True, fg='red')

def green(text):
    return click.style(text, bold=True, fg='green')

def do_scan_azure():
    click.echo(f"Scanning Azure for OpenAI endpoints")
    accounts = list_cognitive_services_accounts()
    endpoints = {}
    stats = {}
    signed_in_user_id = get_az_ad_signed_in_user()
    for account_digest in accounts:
        account_id = account_digest['id']
        resource_group = account_digest['resourceGroup']
        account_name = account_digest['name']
        granted = has_role_assignment(signed_in_user_id, account_id, openai_user_role_id)
        click.echo(f"Found OpenAI resource: {bold(account_name)} in {bold(resource_group)} - {green("GRANTED") if granted else red("DENIED")}")
        if granted:
            account = get_cognitive_services_account(account_id)
            oai_endpoint = get_oai_endpoint(account)
            deployments = get_deployments(account_id)
            for deployment in deployments:
                deployment_name = deployment['name']
                deployment_properties = deployment['properties']
                model = deployment_properties['model']
                model_name = model['name']
                model_version = model['version']
                model_id = f"{model_name}@{model_version}"
                rateLimits = get_deployment_rate_limits(deployment)
                sku = deployment['sku']
                sku_capacity = sku['capacity']
                sku_name = sku['name']

    #            if model_name in model_names:
                if not model_id in endpoints.keys():
                    endpoints[model_id] = []
                    stats[model_id] = {
                        "total_capacity": 0,
                        "total_endpoints": 0
                    }
                endpoints[model_id].append({
                    "deployment_name": deployment_name,
                    "sku_capacity": sku_capacity,
                    "sku_name": sku_name,
                    "endpoint": oai_endpoint
                })
                stats[model_id]['total_capacity'] += sku_capacity
                stats[model_id]['total_endpoints'] += 1
                click.echo(f" - Adding OpenAI endpoint: {bold(model_id)} ({sku_capacity} {sku_name})")


    click.echo("Total capacity by model:")
    for model_id, stat in stats.items():
        click.echo(f" - {model_id}: {stat['total_capacity']}")

    model_list = []
    litellm_config = {
        "model_list": model_list,
        "litellm_settings": {
            "enable_azure_ad_token_refresh": "true"
        }
    }
    for model_id, endpoint_list in endpoints.items():
        for endpoint in endpoint_list:
            deployment_name = endpoint['deployment_name']
            api_base = endpoint['endpoint']
            tpm = int(endpoint['sku_capacity']) * 1000
            model_list.append({
                "model_name": model_id,
                "litellm_params": {
                    "model": f"azure/{deployment_name}",
                    "api_base": api_base,
                    "tpm": tpm,
                    "tenant_id": "HACK"
                }
            })

    return litellm_config

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

def export_proxy_endpoints():
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
