import os
import time
import threading
from .job_status_store import save_status, load_status, save_queues, load_queues
from .queues import queues
from .config import JOB_FOLDER, RESULT_FOLDER
from datetime import datetime
import subprocess

job_status = load_status()
job_queues = load_queues()
def process_job(job):
    print(f"Processing job: {job}")
    job_id = job["job_id"]
    script_path = job["script_path"]
    software = job["software"]
    output_path = os.path.join(JOB_FOLDER, software, job_id, "log.txt")

    # Define job-specific result folder
    result_dir = os.path.join(RESULT_FOLDER, software, job_id)
    os.makedirs(result_dir, exist_ok=True)

    # Update job status
    job_status[job_id] = "running"
    save_status(job_status)
    save_queues(job_queues)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, "w") as f:
            f.write(f"[{datetime.now()}] Started job {job_id} for {software}\n")
            f.write(f"[{datetime.now()}] Running script: {script_path}\n")
            f.flush()

            # Simulated job run: sleep for 5 seconds
            # Replace this with actual execution logic if needed
            if script_path.endswith(".py"):
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    cwd=result_dir,
                    timeout=300  # Optional timeout in seconds
                )
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n[stderr]\n{result.stderr}")
            else:
                f.write("Unknown script type. Skipping execution.\n")

            f.write(f"\n[{datetime.now()}] Completed job {job_id}\n")

        job_status[job_id] = "completed"
        save_status(job_status)

    except Exception as e:
        with open(output_path, "a") as f:
            f.write(f"\n[{datetime.now()}] Job failed: {str(e)}\n")
        job_status[job_id] = "failed"
        save_status(job_status)

def run_queue_loop(software):
    print(f"Starting queue loop for {software}")
    # job_status[job["job_id"]] = "queued"
    q = queues[software]
    while True:
        job = q.get()
        process_job(job)
        q.task_done()

def start_queue_loops():
    for software in queues:
        t = threading.Thread(target=run_queue_loop, args=(software,), daemon=True)
        t.start()

def get_status():
    return job_status