import requests
import json

API_KEY = "9eb2248170d7e66bb715b855e5f0c2a887bae49a"
USERNAME = "devansh404"
HOST = "www.pythonanywhere.com"

headers = {
    "Authorization": f"Token {API_KEY}"
}

def list_files(path=""):
    url = f"https://{HOST}/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/{path}"
    print(f"Fetching: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

files = list_files()
if files:
    print(json.dumps(files, indent=2))
