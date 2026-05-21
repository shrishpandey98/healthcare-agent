import requests
import time

API_KEY = "9eb2248170d7e66bb715b855e5f0c2a887bae49a"
USERNAME = "devansh404"
CONSOLE_ID = 45653402

headers = {
    "Authorization": f"Token {API_KEY}"
}

# Clear any pending output by reading it first
r = requests.get(f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/consoles/{CONSOLE_ID}/", headers=headers)
print("Initial console state fetched.")

# Send input command
cmd = "python main.py\n"
print(f"Sending command: {cmd.strip()}")
r = requests.post(
    f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/consoles/{CONSOLE_ID}/send_input/",
    headers=headers,
    json={"input": cmd}
)

if r.status_code == 200:
    print("Command sent successfully. Waiting for output...")
    time.sleep(5)
    
    # Read output
    r = requests.get(f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/consoles/{CONSOLE_ID}/", headers=headers)
    output = r.json().get("latest_output", "")
    print("--- Console Output ---")
    print(output[-2000:]) # Print the last 2000 characters
else:
    print(f"Failed to send input: {r.status_code} - {r.text}")
