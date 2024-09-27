#!/usr/bin/env python

import rich_click as click
import json
from sys import stdin

def export_var(var_name, value):
    print(f"{var_name}={value}")

@click.command()
@click.option('--deployments-file', 
              help='deployments.json file',
              type=click.File('r'),
              default=stdin)
def export(deployments_file):
    with deployments_file:
        deployments_json = deployments_file.read()
        deployments = json.loads(deployments_json)
        for deployment in deployments:
            var_prefix = deployment['role'].upper()
            export_var(f"{var_prefix}_DEPLOYMENT_NAME", deployment['name'])
            export_var(f"{var_prefix}_DEPLOYMENT_PLATFORM", deployment['platform'])

            deployment_var_name = f"{var_prefix}_AZURE_OPENAI_DEPLOYMENT" if deployment['platform'] == 'openai' else f"{var_prefix}_OPENAI_DEPLOYMENT"
            endpoint_var_name = f"{var_prefix}_AZURE_OPENAI_ENDPOINT" if deployment['platform'] == 'openai' else f"{var_prefix}_OPENAI_BASE_URL"
            export_var(deployment_var_name, deployment['name'])
            export_var(endpoint_var_name, deployment['endpointUri'])

            if deployment['primaryKey']:
                export_var(f"{var_prefix}_OPENAI_API_KEY", deployment['primaryKey'])

if __name__ == '__main__':
    export()
