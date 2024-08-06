def get_pdf_image(doc_path):
    """Converts a PDF document to an image."""
    from wand.image import Image as WImage
    from pathlib import Path
    img = None
    if Path(doc_path).exists() and Path(doc_path).is_file():
        img = WImage(filename=doc_path)

        # make background of img white
        img.format = 'png'
        img.background_color = 'white'
        img.alpha_channel = 'remove'
    return img

def get_reporting_project_scope():
    """Builds the project scope for AI Studio reporting from the environment."""
    from os import getenv
    subscription_id = getenv("REPORT_SUB_ID")
    resource_group_name = getenv("REPORT_GROUP")
    project_name = getenv("REPORT_PROJECT_NAME")
    report_vars = [subscription_id, resource_group_name, project_name]
    project_scope_report = None
    if any(report_vars):
        print("Configuring AI Studio Reporting")
        if any(not var for var in report_vars):
            raise ValueError("In order to use AI Studio reporting, please set all REPORT_SUB_ID, REPORT_GROUP, and REPORT_PROJECT_NAME environment variables.")
        project_scope_report = {
            "subscription_id": subscription_id,
            "resource_group_name": resource_group_name,
            "project_name": project_name,
        }
    else:
        print("Skipping AI Studio Reporting")
    return project_scope_report

def update_state(key, value):
    """Update the .env.state state file with the key and value."""
    from pathlib import Path
    from dotenv import dotenv_values
    data = {}
    state_filename = '.env.state'
    if Path(state_filename).exists() and Path(state_filename).is_file():
        data = dotenv_values(state_filename)
    data[key] = value
    with open(state_filename, 'w') as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")

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
