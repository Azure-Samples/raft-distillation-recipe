from dotenv import load_dotenv
from os import getenv
from utils import do_test_openai_endpoint

load_dotenv(".env")
load_dotenv(".env.state")

def test_teacher():
    base_url = getenv("COMPLETION_OPENAI_BASE_URL")
    key = getenv("COMPLETION_OPENAI_API_KEY")
    model = getenv("COMPLETION_OPENAI_DEPLOYMENT")
    do_test_openai_endpoint(base_url, key, model)
