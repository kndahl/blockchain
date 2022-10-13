import re
import requests
import os

def reg_node():
    try:
        host = os.environ['NODE_NAME']
        port = os.environ['NODE_PORT']
        req = requests.get(f'http://{host}:{port}/blockchain/worker/register')
        if req.status_code == 200:
            return True
    except Exception:
        return False