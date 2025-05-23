import os
import threading
from .job_db import update_status, get_job_status
from .queues import queues
from .config import JOB_FOLDER, RESULT_FOLDER
from datetime import datetime
import subprocess

# job_status = load_status()
# job_queues = load_queues()
def process_job(job):
    print(f"{datetime.now()} - Processing job: {job['job_id']}")
    job_id = job["job_id"]
    script_path = job["script_path"]
    queue_name = job["queue_name"]
    output_path = os.path.join(JOB_FOLDER, queue_name, job_id, "log.txt")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Define job-specific result folder
    result_dir = os.path.join(RESULT_FOLDER, queue_name, job_id)
    os.makedirs(result_dir, exist_ok=True)



    # Update job status
    update_status(job_id, "running")

    

    try:
        with open(output_path, "w") as f:
            f.write(f"[{datetime.now()}] Started job {job_id} for {queue_name}\n")
            f.write(f"[{datetime.now()}] Running script: {script_path}\n")
            f.flush()

            # Run job script
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
                    f.write(f"\n[{datetime.now()}] Error in job {job_id}\n")
                    update_status(job_id, "failed")
                else:
                    f.write(f"\n[{datetime.now()}] Completed job {job_id}\n")
                    update_status(job_id, "completed")
            else:
                f.write(f"\n[{datetime.now()}] Unknown script type for job {job_id}. Skipping execution\n")
                update_status(job_id, "failed")


    except Exception as e:
        with open(output_path, "a") as f:
            f.write(f"\n[{datetime.now()}] Job failed: {str(e)}\n")
        update_status(job_id, "failed")

    status = get_job_status(job_id)['status'].values[0]
    print(f"{datetime.now()} - Finished job: {job['job_id']} - Status: {status}")

def run_queue_loop(queue_name):
    print(f"Starting queue loop for {queue_name}")
    q = queues[queue_name]
    while True:
        job = q.get()
        process_job(job)
        q.task_done()

def start_queue_loops():
    for queue_name in queues:
        t = threading.Thread(target=run_queue_loop, args=(queue_name,), daemon=True)
        t.start()

# def get_status():
#     return job_status