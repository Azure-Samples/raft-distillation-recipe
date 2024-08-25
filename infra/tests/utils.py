from openai import OpenAI

def do_test_openai_endpoint(base_url, key, model):
    from openai import AzureOpenAI

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
