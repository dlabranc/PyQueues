import requests
import os
import getpass
import pandas as pd
from .client_config import IP, PORT

USER_ID = getpass.getuser()

SERVER_URL = f"http://{IP}:{PORT}"
# HISTORY_FILE = "client_job_history.json"


def submit_job(script_path, queue_name, resources=None, user_id=USER_ID, server_url=SERVER_URL):
    # Open the main script file
    files = [("script", open(script_path, "rb"))]

    script_dir = os.path.dirname(script_path)
    if script_dir == "":
        script_dir = os.getcwd()


    if resources is None:
        # Recursively gather all files excluding the script
        resources = []
        for root, _, filenames in os.walk(script_dir):
            for f in filenames:
                full_path = os.path.join(root, f)
                if os.path.abspath(full_path) != os.path.abspath(script_path):
                    resources.append(full_path)
    elif isinstance(resources, str):
        resources = [resources]

    print(resources)
    # Attach each resource with its relative path
    for res_path in resources:
        rel_path = os.path.relpath(res_path, start=script_dir)
        with open(res_path, "rb") as f:
            files.append(("resources", (rel_path, f.read())))
    
    # Send the request to the server
    data = {"queue_name": queue_name, "user_id": user_id}
    r = requests.post(f"{server_url}/submit", files=files, data=data)
    response = r.json()
    print("Server response:", response)


def get_job(job_id, server_url=SERVER_URL):
    r = requests.get(f"{server_url}/status_id/{job_id}")
    if r.status_code == 200:
        jobs = r.json()
        jobs = pd.DataFrame(jobs)
        return jobs
    else:
        print("Error:", r.status_code, r.text)

def get_all_user_jobs(user_id=USER_ID, server_url=SERVER_URL):
    r = requests.get(f"{server_url}/status_user/{user_id}")
    if r.status_code == 200:
        jobs = r.json()
        jobs = pd.DataFrame(jobs)
        return jobs
    else:
        print("Error:", r.status_code, r.text)

def get_all_jobs(server_url=SERVER_URL):
    r = requests.get(f"{server_url}/status/all")
    if r.status_code == 200:
        jobs = r.json()
        jobs = pd.DataFrame(jobs)
        return jobs
    else:
        print("Error:", r.status_code, r.text)

def download_job_log(job_id, save_as=None, server_url=SERVER_URL):
    if save_as is None:
        save_as = f"{job_id}_log.txt"
    r = requests.get(f"{server_url}/result/{job_id}")
    if r.status_code == 200:
        with open(save_as, "wb") as f:
            f.write(r.content)
        print(f"✅ Downloaded output to: {save_as}")
    else:
        print("Error:", r.status_code, r.text)

def download_job_results(job_id, save_as=None, server_url=SERVER_URL):
    if save_as is None:
        save_as = f"{job_id}_results.zip"
    r = requests.get(f"{server_url}/download/{job_id}")
    if r.status_code == 200:
        with open(save_as, "wb") as f:
            f.write(r.content)
        print(f"✅ Downloaded output to: {save_as}")
    else:
        print("Error:", r.status_code, r.text)