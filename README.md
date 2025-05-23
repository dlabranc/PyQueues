This is a simple module for scheduling tasks in queues from python scripts.
# Installation 
Install this package on both the server and client. Note: the server environment in which you will run this server must have all the client's codes required packages installed.
Clone the repository.
'git clone'
Install the package.
'pip install -e .'
# Server end
First set the BASE_DIR path in "config.py". This sets the folder on the remote machine in which all the scripts results and logs will be stored.
'
BASE_DIR = '\\BASEDIR\\'
'
In the same file you can define different queues for your scheduler as a list. Each queue will be handeled in parallel.
'
SOFTWARE_QUEUES = ["ansys", "palace"]
'
You can now start the server:
'
jobqueue-server
'
# Client end
The client only needs to know the IP and port where the server is running and set that in the client_config.py file.

1. Set the IP and PORT of the server in client_config.py
   '
    IP = "127.0.0.1"
    PORT = 5000
   '
2. Start submitting jobs! For example in the test_folder
   '
   from jobqueue_server.client import *
   submit_job("example_script.py", "ansys")
   '
   This code submits a new job to the "ansys" queue with "example_script.py" as main script and all the files in the folder as auxiliary files (these can be used as config files, support files or whatever you want)
3. The client can track the jobs by using:
   '
   get_all_jobs()
   get_all_user_jobs(USER_ID)
   get_job(JOB_ID)
   '
4. Once the job status is "completed" the client can download the log file and the zip results folder:
   '
   download_job_log(JOB_ID)
   download_job_results(JOB_ID)
   '
   
   
