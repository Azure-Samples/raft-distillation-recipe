#!/usr/local/bin/python3.12
# -*- coding: utf-8 -*-
import re
import sys

# LiteLLM doesn't support DefaultAzureCredential and get_bearer_token_provider
# And the team doesn't seem to be willing to add it
# See https://github.com/BerriAI/litellm/issues/4417

# This monkey patches LiteLLM to force it to use the DefaultAzureCredential and get_bearer_token_provider
# This requires the `tenant_id` to be set on `litellm_params`

#  - litellm_params:
#      api_base: https://aoai-3d5caufuiotbg.openai.azure.com/
#      model: azure/openai-gpt-4o
#      tpm: 8000
#      tenant_id: "HACK"
#    model_name: gpt-4o


from litellm.router_utils import client_initalization_utils
from typing import TYPE_CHECKING, Any, Callable, Optional
from litellm._logging import verbose_router_logger

def get_azure_ad_token_from_entrata_id(
    tenant_id: str, client_id: str, client_secret: str
) -> Callable[[], str]:
    from azure.identity import (
        ClientSecretCredential,
        DefaultAzureCredential,
        get_bearer_token_provider,
    )

    verbose_router_logger.debug("Getting Azure AD Token from Entrata ID")

    credential = DefaultAzureCredential()

    verbose_router_logger.debug("credential %s", credential)
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )

    verbose_router_logger.debug("token_provider %s", token_provider)

    return token_provider


client_initalization_utils.get_azure_ad_token_from_entrata_id = get_azure_ad_token_from_entrata_id

from litellm import run_server

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(run_server())
