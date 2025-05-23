import os
from datetime import datetime
import pandas as pd
from .config import DB_FOLDER

# This module handles the job database, which is a JSON file.
# Each job is a dictionary with the following keys:
# - job_id: a unique identifier for the job
# - user_id: the ID of the user who submitted the job
# - status: the current status of the job (e.g., "pending", "running", "completed")
# - created_at: the timestamp when the job was created
# - updated_at: the timestamp when the job was last updated
DB_FILE = os.path.join(DB_FOLDER, "jobs_database.csv")

def at_server_start():
    if DB_FOLDER and not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER, exist_ok=True)
    # Ensure the DB_FOLDER exists
    if not os.path.exists(DB_FILE):
        jobs = pd.DataFrame(columns=["job_id", "user_id", "queue_name", "script_path", "status", "created_at", "updated_at"])
        jobs.to_csv(DB_FILE)  # Initialize with an empty dictionary
    else:
        jobs = load_db()
    jobs.loc[jobs['status'] == 'queued', 'status'] = 'never started'
    jobs.loc[jobs['status'] == 'sent', 'status'] = 'never started'
    jobs.loc[jobs['status'] == 'running', 'status'] = 'interrupted'
    save_db(jobs)

def load_db():
    if os.path.exists(DB_FILE):
        jobs = pd.read_csv(DB_FILE, index_col=0)
        return jobs
    else:
        raise FileNotFoundError(f"Jobs datatbase file {DB_FILE} not found.")

def save_db(jobs):
    jobs.to_csv(DB_FILE)

def add_job(job):
    jobs = load_db()
    jobs = pd.concat([jobs, pd.DataFrame([job])], ignore_index=True)
    save_db(jobs)

def update_status(job_id, new_status):
    jobs = load_db()
    jobs.loc[jobs['job_id'] == job_id, 'status'] = new_status
    jobs.loc[jobs['job_id'] == job_id, 'updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_db(jobs)

def get_job_queue_name(job_id):
    jobs = load_db()
    return jobs.loc[jobs['job_id'] == job_id, 'queue_name']

def get_user_jobs(user_id):
    jobs = load_db()
    return jobs.loc[jobs['user_id'] == user_id]

def get_job_status(job_id):
    jobs = load_db()
    if any(jobs['job_id'] == job_id):
        return jobs.loc[jobs['job_id'] == job_id]
    else:
        return None

def reset_job_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    at_server_start()
    print("Job database reset.")