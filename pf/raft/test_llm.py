from promptflow import tool
from promptflow.connections import CustomConnection
from openai import OpenAI


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def classify_intent(prompt: str) -> str:

    endpoint_url = "xxx"
    api_key = "xxx"

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    base_url = endpoint_url + '/v1'
    client = OpenAI(
        base_url = base_url,
        api_key=api_key,
    )

    deployment_name = "Llama-2-7b-raft-bats-18k-unrrr"

    # COMPLETION API
    response = client.completions.create(
        model=deployment_name,
        prompt=prompt,
        stop="<STOP>",
        temperature=0.5,
        max_tokens=512,
        top_p=0.1,
        best_of=1,
        presence_penalty=0,
    )

    return response.choices[0].text.strip()