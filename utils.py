def get_pdf_image(doc_path):
    """Converts a PDF document to an image."""
    from wand.image import Image as WImage
    from pathlib import Path

    img = None
    if Path(doc_path).exists() and Path(doc_path).is_file():
        img = WImage(filename=doc_path)

        # make background of img white
        img.format = "png"
        img.background_color = "white"
        img.alpha_channel = "remove"
    return img


def update_state(key, value):
    """Update the .env.state state file with the key and value."""
    from pathlib import Path
    from dotenv import dotenv_values

    data = {}
    state_filename = ".env.state"
    if Path(state_filename).exists() and Path(state_filename).is_file():
        data = dotenv_values(state_filename)
    data[key] = value
    print(f"Updating state file with {key}={redact_secret(key, value)}")
    with open(state_filename, "w") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")

def redact_secret(key, value):
    """Redact a value from the logs if the key indicates that the value contains a keyword such as KEY or SECRET."""
    if "KEY" in key or "SECRET" in key:
        return value[:4] + "*" * (len(value) - 4)
    return value
    

def wait_for_model(client, model_name):
    """Wait for the model to be available, typically waiting for a finetuning job to complete."""
    import time

    attempts = 0
    while True:
        try:
            model = client.models.get(model_name, label="latest")
            return model
        except:
            print(f"Model not found yet #{attempts}")
            attempts += 1
            time.sleep(30)


def file_sha256(filename):
    """Returns the SHA256 hash of a file."""
    import hashlib

    with open(filename, "rb", buffering=0) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()
