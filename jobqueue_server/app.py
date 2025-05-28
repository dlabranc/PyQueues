from flask import Flask, request, jsonify, send_file
import io
import zipfile
import os
from .utils import *
from .queues import queues
from .job_loops import start_queue_loops
from .config import JOB_FOLDER, RESULT_FOLDER
from .job_db import add_job, get_user_jobs, update_status, get_job_queue_name, get_job_status, load_db, at_server_start
from datetime import datetime
from collections import OrderedDict

app = Flask(__name__)
os.makedirs(JOB_FOLDER, exist_ok=True)


# Submit and queues a job
# Also adds the job to the database - Tested and working
@app.route("/submit", methods=["POST"])
def submit():
    queue_name = request.form.get("queue_name")
    user_id = request.form.get("user_id")
    if queue_name not in queues:
        return jsonify({"error": f"Unknown queue_name: {queue_name}"}), 400

    job_id = generate_job_id()

    # Create directories for job and result
    job_dir = os.path.join(JOB_FOLDER, queue_name, job_id)
    result_dir = os.path.join(RESULT_FOLDER, queue_name, job_id)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(result_dir, exist_ok=True)

    script_file = request.files["script"]
    resources = request.files.getlist("resources")

    # Save the script file in result_dir
    script_path = os.path.join(result_dir, script_file.filename)
    script_file.save(script_path)

    # # Save resources in result_dir
    # for file in resources:
    #     res_path = os.path.join(result_dir, file.filename)
    #     file.save(res_path)
    for file in resources:
        rel_path = file.filename
        full_path = os.path.join(result_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)


    # Save the job information to the database
    # This should include the job ID, user ID, queue name, script path, and status
    # You can also include timestamps for when the job was created and last updated
    job = {
        "job_id": job_id,
        "user_id": user_id,
        "queue_name": queue_name,
        "script_path": script_path,
        "status": "sent",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Save the job to the database
    add_job(job)

    # Add job to the queue
    queues[queue_name].put(job)

    update_status(job_id, "queued")

    return jsonify({"status": "queued", "job_id": job_id})


# Gets the job log file - Tested and working
@app.route("/result/<job_id>")
def result(job_id):
    queue_name = get_job_queue_name(job_id).values[0] if not get_job_queue_name(job_id).empty else None
    if queue_name is None:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    output_path = os.path.join(JOB_FOLDER, queue_name, job_id, "log.txt")
    if not os.path.exists(output_path):
        return jsonify({"status": "pending"}), 202
    return send_file(output_path, as_attachment=False), 200


# Gets the job file results folder
@app.route("/download/<job_id>")
def download_result_folder(job_id):
    # Lookup queue_name type from job_status
    queue_name = get_job_queue_name(job_id).values[0] if not get_job_queue_name(job_id).empty else None
    if queue_name is None:
        return jsonify({"error": f"Job {job_id} not found"}), 404

    result_dir = os.path.join(RESULT_FOLDER, queue_name, job_id)

    if not os.path.exists(result_dir):
        return jsonify({"error": "Result folder does not exist"}), 404

    # Create zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(result_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, result_dir)
                zipf.write(full_path, rel_path)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{job_id}_{queue_name}_results.zip"
    )

# Gets the jobs of a specific user - Tested and working
@app.route("/status_user/<user_id>")
def status_user_jobs(user_id):
    return jsonify(get_user_jobs(user_id).to_dict())


# Gets the status of a specific job - Tested and working
@app.route("/status_id/<job_id>")
def status_job(job_id):
    job = get_job_status(job_id)
    print(job)
    if job is not None:
        return jsonify(job.to_dict()), 200
    else:
        return jsonify({"error": "Result folder does not exist"}), 404

# Gets the status of all jobs - Tested and working
@app.route("/status/all")
def status_all():
    jobs = load_db()
    return jsonify(jobs.to_dict()), 200

# Starts the queues at server start - Tested and working
def run():
    at_server_start()
    start_queue_loops()
    app.run(host="0.0.0.0", port=5000)