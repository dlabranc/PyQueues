import json
import os
from .config import JOB_FOLDER
STATUS_FILE = os.path.join(JOB_FOLDER, "job_status.json")
QUEUE_FILE = os.path.join(JOB_FOLDER, "job_queues.json")

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)
            # Update any "running" jobs to "interrupted" and "queued" jobs to "never started"
            for job_id in status:
                if status[job_id] == "running":
                    status[job_id] = "interrupted"
                elif status[job_id] == "queued":
                    status[job_id] = "never started"
            return status
    return {}

def save_status(status_dict):
    with open(STATUS_FILE, "w") as f:
        json.dump(status_dict, f, indent=2)

def load_queues():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r") as f:
            job_queues = json.load(f)            
            return job_queues
    return {}

def save_queues(queue_dict):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue_dict, f, indent=2)