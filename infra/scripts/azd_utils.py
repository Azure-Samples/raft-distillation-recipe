from dotenv import load_dotenv
import subprocess

def azd_env_get_values():
    result = subprocess.run(['azd', 'env', 'get-values'], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to get azd environment values because of: " + result.stdout)
    return result.stdout

def load_azd_env():
    from io import StringIO
    env_values = azd_env_get_values()
    config = StringIO(env_values)
    load_dotenv(stream=config)
