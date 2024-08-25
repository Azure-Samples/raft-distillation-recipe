from dotenv import load_dotenv
from os import getenv
from utils import do_test_openai_endpoint

load_dotenv(".env")
load_dotenv(".env.state")

def test_baseline():
    base_url = getenv("BASELINE_OPENAI_BASE_URL")
    key = getenv("BASELINE_OPENAI_API_KEY")
    model = getenv("BASELINE_OPENAI_DEPLOYMENT")
    do_test_openai_endpoint(base_url, key, model)
