import datetime
import random
import string

def generate_job_id():
    now = datetime.datetime.now()
    time_part = now.strftime("%H%M")
    date_part = now.strftime("%d%m%y")
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{time_part}_{date_part}_{rand_part}"