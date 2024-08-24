from dotenv import load_dotenv
from os import getenv
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.identity import get_bearer_token_provider
from openai import AzureOpenAI

load_dotenv(".env")
load_dotenv(".env.state")

def test_embeddings():
    from openai import AzureOpenAI

    # Authenticate using the default Azure credential chain
    azure_credential = DefaultAzureCredential()

    model = getenv("EMBEDDING_DEPLOYMENT_NAME")

    oai_client = AzureOpenAI(
        api_version = getenv("EMBEDDING_OPENAI_API_VERSION"),
        azure_endpoint = getenv("EMBEDDING_AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider = get_bearer_token_provider(
            azure_credential, "https://cognitiveservices.azure.com/.default")
        )
    response = oai_client.embeddings.create(input = ["Hello"], model=model).data[0].embedding
    assert response is not None
    assert len(response) >= 512
