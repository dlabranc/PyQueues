from flask import Flask, request, jsonify, send_file
import io
import zipfile
import uuid
import os
from .utils import *
from .queues import queues
from .job_loops import start_queue_loops, get_status, job_status, job_queues
from .config import JOB_FOLDER, RESULT_FOLDER
from .job_status_store import load_status, save_status, load_queues, save_queues

app = Flask(__name__)
os.makedirs(JOB_FOLDER, exist_ok=True)


@app.route("/submit", methods=["POST"])
def submit():
    software = request.form.get("software")
    if software not in queues:
        return jsonify({"error": f"Unknown software: {software}"}), 400

    job_id = generate_job_id()#str(uuid.uuid4())
    job_dir = os.path.join(JOB_FOLDER, software, job_id)
    os.makedirs(job_dir, exist_ok=True)

    script_file = request.files["script"]
    script_path = os.path.join(job_dir, script_file.filename)
    script_file.save(script_path)

    job = {"job_id": job_id, "software": software, "script_path": script_path}
    queues[software].put(job)
    print(f"Job {job_id} submitted to {software} queue.")
    job_status[job_id] = "queued"
    job_queues[job_id] = software
    return jsonify({"status": "queued", "job_id": job_id})

@app.route("/result/<job_id>")
def result(job_id):
    software = job_queues[job_id]
    if software is None:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    output_path = os.path.join(JOB_FOLDER, software, job_id, "log.txt")
    if not os.path.exists(output_path):
        return jsonify({"status": "pending"}), 202
    return send_file(output_path, as_attachment=False)


@app.route("/download/<job_id>")
def download_result_folder(job_id):
    # Lookup software type from job_status
    software = job_queues[job_id]
    if software is None:
        return jsonify({"error": f"Job {job_id} not found"}), 404

    result_dir = os.path.join(RESULT_FOLDER, software, job_id)

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
        download_name=f"{job_id}_{software}_results.zip"
    )

@app.route("/status/<job_id>")
def status(job_id):
    status = get_status().get(job_id, "unknown")
    return jsonify({"job_id": job_id, "status": status})

@app.route("/status/all")
def status_all():
    return jsonify(get_status())

def run():
    start_queue_loops()
    app.run(host="0.0.0.0", port=5000)
