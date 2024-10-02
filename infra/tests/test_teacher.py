from dotenv import load_dotenv
from os import getenv
from utils import do_test_openai_endpoint

load_dotenv(".env")
load_dotenv(".env.state")

def test_teacher():
    do_test_openai_endpoint("TEACHER")
