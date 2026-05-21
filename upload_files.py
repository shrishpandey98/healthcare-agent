import requests
import os

API_KEY = "9eb2248170d7e66bb715b855e5f0c2a887bae49a"
USERNAME = "devansh404"
HOST = "www.pythonanywhere.com"

FILES_TO_UPLOAD = [
    "config.py",
    "decision_engine.py",
    "main.py",
    "app.py",
    "messenger.py"
]

headers = {
    "Authorization": f"Token {API_KEY}"
}

for filename in FILES_TO_UPLOAD:
    url = f"https://{HOST}/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/{filename}"
    print(f"Uploading {filename} to {url}...")
    
    with open(filename, "rb") as f:
        files = {"content": f}
        r = requests.post(url, headers=headers, files=files)
        
    if r.status_code in (200, 201):
        print(f"Successfully uploaded {filename}")
    else:
        print(f"Failed to upload {filename}: {r.status_code} - {r.text}")
