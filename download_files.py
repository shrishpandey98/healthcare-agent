import os
import requests

API_KEY = "9eb2248170d7e66bb715b855e5f0c2a887bae49a"
USERNAME = "devansh404"
HOST = "www.pythonanywhere.com"

headers = {
    "Authorization": f"Token {API_KEY}"
}

def download(filename):
    url = f"https://{HOST}/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/{filename}"
    print(f"Downloading: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Downloaded {filename}")
    else:
        print(f"Error downloading {filename}: {response.status_code}")

download("app.py")
download("main.py")
download("config.py")
download("sheet_updater.py")
download("analytics_agent.py")
download("setup_sheet.py")
download("categorizer.py")
download("app.css")
download("templates/index.html")
download("templates/login.html")
download("static/app.js")
