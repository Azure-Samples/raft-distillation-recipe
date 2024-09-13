from openai import OpenAI, AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider

def do_test_openai_endpoint(base_url, key, model):
    assert model is not None
    assert base_url is not None
    assert key is not None

    client = OpenAI(
        base_url = base_url,
        api_key = key,
        )
    response = client.chat.completions.create(
        model=model, 
        messages=[{"role": "user", "content": "Hello"}]
        )
    assert response is not None
    assert len(choices := response.choices) > 0
    assert (choice := choices[0]) is not None
    assert (message := choice.message) is not None
    assert message.content is not None

def do_test_azure_openai_endpoint(endpoint, model, version):
    assert model is not None
    assert endpoint is not None
    assert version is not None

    print(f"endpoint: {endpoint}")
    print(f"model: {model}")

    # Authenticate using the default Azure credential chain
    azure_credential = DefaultAzureCredential()

    client = AzureOpenAI(
        api_version=version,
        azure_endpoint=endpoint,
        azure_ad_token_provider = get_bearer_token_provider(
            azure_credential, "https://cognitiveservices.azure.com/.default"
        )
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello"}]
        )
    assert response is not None
    assert len(choices := response.choices) > 0
    assert (choice := choices[0]) is not None
    assert (message := choice.message) is not None
    assert message.content is not None
