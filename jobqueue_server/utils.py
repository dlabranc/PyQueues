import datetime
import random
import string

def generate_job_id():
    now = datetime.datetime.now()
    time_part = now.strftime("%H%M")
    date_part = now.strftime("%y%m%d")
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    #str(uuid.uuid4())
    return f"{date_part}_{time_part}_{rand_part}"