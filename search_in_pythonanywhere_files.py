import requests

API_KEY = "9eb2248170d7e66bb715b855e5f0c2a887bae49a"
USERNAME = "devansh404"
HOST = "www.pythonanywhere.com"

headers = {
    "Authorization": f"Token {API_KEY}"
}

files_to_check = [
    "app.py",
    "main.py",
    "index.html",
    "templates/index.html",
    "static/js/main.js",  # if exists, let's look for templates and static files later
]

for filename in files_to_check:
    url = f"https://{HOST}/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/{filename}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.text
        if "Agent triggered" in content or "delay" in content or "triggered" in content or "SMS" in content:
            print(f"=== Match found in {filename} ===")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if any(x in line for x in ["Agent triggered", "delay", "triggered", "SMS", "minute"]):
                    print(f"Line {i+1}: {line}")
    elif response.status_code == 404:
        # File doesn't exist, which is fine
        pass
    else:
        print(f"Error checking {filename}: {response.status_code}")
