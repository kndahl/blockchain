import requests
import time

time.sleep(20)
req = requests.get('http://worker_service:3000/worker/mine/')
print(req.status_code)
print(req.json())