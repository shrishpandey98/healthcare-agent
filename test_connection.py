import requests
import json

API_KEY = "9eb2248170d7e66bb715b855e5f0c2a887bae49a"
USERNAMES = [
    "devansh404"
]
HOSTS = [
    "www.pythonanywhere.com"
]

print("Starting PythonAnywhere API connection test...")

for host in HOSTS:
    for username in USERNAMES:
        url = f"https://{host}/api/v0/user/{username}/cpu/"
        headers = {
            "Authorization": f"Token {API_KEY}"
        }
        try:
            print(f"Testing host: {host}, username: {username} ...")
            response = requests.get(url, headers=headers)
            print(f"  Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"  [SUCCESS] Connected to {host} using username: {username}!")
                print(f"  Response: {response.text}")
                
                # Try listing webapps
                webapps_url = f"https://{host}/api/v0/user/{username}/webapps/"
                webapps_resp = requests.get(webapps_url, headers=headers)
                print(f"  Webapps response code: {webapps_resp.status_code}")
                if webapps_resp.status_code == 200:
                    print(f"  Webapps: {webapps_resp.text}")
                
                # Try listing consoles
                consoles_url = f"https://{host}/api/v0/user/{username}/consoles/"
                consoles_resp = requests.get(consoles_url, headers=headers)
                print(f"  Consoles response code: {consoles_resp.status_code}")
                if consoles_resp.status_code == 200:
                    print(f"  Consoles: {consoles_resp.text}")
                
                # Try listing scheduled tasks
                tasks_url = f"https://{host}/api/v0/user/{username}/scheduled_tasks/"
                tasks_resp = requests.get(tasks_url, headers=headers)
                print(f"  Scheduled tasks response code: {tasks_resp.status_code}")
                if tasks_resp.status_code == 200:
                    print(f"  Tasks: {tasks_resp.text}")
                
                break
            else:
                try:
                    print(f"  Details: {response.json()}")
                except Exception:
                    print(f"  Details: {response.text}")
        except Exception as e:
            print(f"  Error testing {username} on {host}: {e}")

print("Probing completed.")
