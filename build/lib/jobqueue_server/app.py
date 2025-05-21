from flask import Flask, request, jsonify, send_file
import uuid
import os
from .queues import queues
from .job_loops import start_queue_loops, get_status
from .config import JOB_FOLDER

app = Flask(__name__)
os.makedirs(JOB_FOLDER, exist_ok=True)

@app.route("/submit", methods=["POST"])
def submit():
    software = request.form.get("software")
    if software not in queues:
        return jsonify({"error": f"Unknown software: {software}"}), 400

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(JOB_FOLDER, job_id)
    os.makedirs(job_dir, exist_ok=True)

    script_file = request.files["script"]
    script_path = os.path.join(job_dir, script_file.filename)
    script_file.save(script_path)

    job = {"job_id": job_id, "software": software, "script_path": script_path}
    queues[software].put(job)

    return jsonify({"status": "queued", "job_id": job_id})

@app.route("/result/<job_id>")
def result(job_id):
    output_path = os.path.join(JOB_FOLDER, job_id, "output.txt")
    if not os.path.exists(output_path):
        return jsonify({"status": "pending"}), 202
    return send_file(output_path, as_attachment=False)

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
