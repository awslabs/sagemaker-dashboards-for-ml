import json
from pathlib import Path
import sagemaker


def get_notebook_name():
    with open('/opt/ml/metadata/resource-metadata.json') as openfile:
        data = json.load(openfile)
    notebook_name = data['ResourceName']
    return notebook_name


def get_dashboard_url(port):
    notebook_name = get_notebook_name()
    region_name = sagemaker.Session().boto_region_name
    return f"https://{notebook_name}.notebook.{region_name}.sagemaker.aws/proxy/{port}/"


def get_docker_run_command(port, image, local_dir_mount=False, debug=False):
    session = sagemaker.Session()
    region_name = session.boto_region_name
    credentials = session.boto_session.get_credentials()
    command = [f"docker run -p {port}:80"]
    if local_dir_mount:
        local_dir_mount = Path(local_dir_mount).resolve()
        command += [f"-v {local_dir_mount}:/usr/src/app/src"]
    command += [
        f"--env AWS_DEFAULT_REGION={region_name}",
        f"--env AWS_ACCESS_KEY_ID={credentials.access_key}",
        f"--env AWS_SECRET_ACCESS_KEY={credentials.secret_key}",
        f"--env AWS_SESSION_TOKEN={credentials.token}",
    ]
    if debug:
        command += [ "--env DASHBOARD_DEBUG=true" ]
    else:
        command += [ "--env DASHBOARD_DEBUG=false" ]
    command += [ f"{image}" ]
    return " \\\n".join(command)
