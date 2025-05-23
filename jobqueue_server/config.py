import os


BASE_DIR = '\\BASEDIR\\' #os.path.dirname(__file__)
JOB_FOLDER = os.path.join(BASE_DIR, "jobs")
RESULT_FOLDER = os.path.join(BASE_DIR, "results")
DB_FOLDER = os.path.join(BASE_DIR, "job_db")
SOFTWARE_QUEUES = ["ansys", "palace"]
