from dotenv import load_dotenv
from os import getenv
from utils import do_test_azure_openai_endpoint

load_dotenv(".env")
load_dotenv(".env.state")

def test_scoring():
    endpoint = getenv("SCORING_AZURE_OPENAI_ENDPOINT")
    deployment = getenv("SCORING_AZURE_OPENAI_DEPLOYMENT")
    version = getenv("SCORING_OPENAI_API_VERSION")
    do_test_azure_openai_endpoint(endpoint, deployment, version)
