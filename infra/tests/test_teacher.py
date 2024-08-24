from dotenv import load_dotenv
from os import getenv
from openai import OpenAI

load_dotenv(".env")
load_dotenv(".env.state")

def test_teacher():
    from openai import AzureOpenAI

    model = getenv("COMPLETION_OPENAI_DEPLOYMENT")
    assert model is not None

    base_url = getenv("COMPLETION_OPENAI_BASE_URL")
    assert base_url is not None

    key = getenv("COMPLETION_OPENAI_API_KEY")
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
