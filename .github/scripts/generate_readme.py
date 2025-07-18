import requests

ORG = "9Mirrors-Lab"
REPO = "knowledge-index"
GITHUB_TOKEN = "ghp_xxx"  # store this securely in Actions secrets

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

response = requests.get(f"https://api.github.com/orgs/{ORG}/repos", headers=headers)
repos = response.json()

table = "## 🧠 Knowledge Repos\n\n| Repo | GitHub | MCP |\n|------|--------|-----|\n"

for repo in repos:
    name = repo["name"]
    if name.startswith("know-"):
        github_link = repo["html_url"]
        mcp_link = f"https://gitmcp.io/{ORG}/{name}"
        table += f"| `{name}` | [Repo]({github_link}) | [MCP Viewer]({mcp_link}) |\n"

# Write to README
with open("README.md", "w") as f:
    f.write(f"# 9Mirrors Knowledge Index\n\n{table}")
