import requests
req = requests.get('http://127.0.0.1:3000/mine/')
print(req.status_code)
print(req.json())