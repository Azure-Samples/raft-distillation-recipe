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

    model = getenv("EMBEDDING_AZURE_OPENAI_DEPLOYMENT")
    assert model is not None

    endpoint = getenv("EMBEDDING_AZURE_OPENAI_ENDPOINT")
    assert endpoint is not None

    version = getenv("EMBEDDING_OPENAI_API_VERSION")
    assert version is not None

    oai_client = AzureOpenAI(
        api_version = version,
        azure_endpoint = endpoint,
        azure_ad_token_provider = get_bearer_token_provider(
            azure_credential, "https://cognitiveservices.azure.com/.default")
        )
    response = oai_client.embeddings.create(input = ["Hello"], model=model)
    assert response is not None
    assert len(datas := response.data) > 0
    assert datas[0] is not None
    assert (embedding := datas[0].embedding) is not None
    assert embedding is not None
    assert len(embedding) >= 512
