import requests
import os

GITHUB_TOKEN = os.getenv("GH_PERSONAL_ACCESS_TOKEN")
REPO_OWNER = "9Mirrors-Lab"
REPO_NAME = "knowledge-index"

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
}

payload = {
    "event_type": "repo-added"
}

response = requests.post(url, json=payload, headers=headers)

# Better feedback
if response.status_code == 204:
    print("✅ Successfully triggered the README auto-update workflow.")
else:
    print(f"❌ Failed to trigger workflow: {response.status_code}")
    print(response.text)