#!/usr/bin/env python

import os
import rich_click as click
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv
import subprocess
from itertools import groupby

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

@click.command()
def find_endpoints():
    click.echo(f"Searching for endpoints")
    accounts = list_cognitive_services_accounts()
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
            click.echo(f"OpenAI endpoint: {model_name} {oai_endpoint} ({sku_capacity} {sku_name})")

if __name__ == '__main__':
    find_endpoints()
