import os
import time
import threading
from .queues import queues
from .config import JOB_FOLDER
import datetime
import subprocess
job_status = {}

def process_job(job):
    job_id = job["job_id"]
    script_path = job["script_path"]
    software = job["software"]
    output_path = os.path.join(JOB_FOLDER, job_id, "output.txt")

    # Update job status
    job_status[job_id] = "running"

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
                    timeout=300  # Optional timeout in seconds
                )
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n[stderr]\n{result.stderr}")
            else:
                f.write("Unknown script type. Skipping execution.\n")

            f.write(f"\n[{datetime.now()}] Completed job {job_id}\n")

        job_status[job_id] = "completed"

    except Exception as e:
        with open(output_path, "a") as f:
            f.write(f"\n[{datetime.now()}] Job failed: {str(e)}\n")
        job_status[job_id] = "failed"

def run_queue_loop(software):
    job_status[job["job_id"]] = "queued"
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