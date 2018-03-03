


import time
from datetime import datetime, timedelta
import json

def load_from_file(filename, default_value=None):
    ret = default_value
    try:
        file = open(filename,'r')  
        ret = json.loads(file.read())
        file.close()
    except:
        pass
    return ret

def save_to_file(filename, data):   
    file = open(filename,'w')  
    file.write(json.dumps(data, sort_keys=True, indent=4)) 
    file.close() 
  

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def timestamp_to_time(t):
    return datetime_from_utc_to_local(datetime(1970, 1, 1) + timedelta(seconds=int(t)/1000) ).strftime('%H:%M:%S')


