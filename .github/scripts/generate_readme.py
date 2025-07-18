# .github/scripts/generate_readme.py

import os
import jwt
import time
import requests
from github import Github

# === Load env vars from GitHub Actions ===
APP_ID = os.getenv("APP_ID")
INSTALLATION_ID = os.getenv("INSTALLATION_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # private key as a string
REPO_OWNER = "9Mirrors-Lab"
REPO_NAME = "knowledge-index"

# === Generate JWT ===
def generate_jwt(app_id, private_key_str):
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id
    }
    return jwt.encode(payload, private_key_str, algorithm="RS256")

# === Get installation token ===
def get_installation_token(jwt_token, installation_id):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]

# === Generate new README content ===
def generate_readme(repos):
    lines = [
        "# 📘 9Mirrors Knowledge Index",
        "",
        "[![MCP Enabled](https://img.shields.io/badge/MCP-ready-blueviolet)](https://gitmcp.io/9Mirrors-Lab/knowledge-index)",
        "",
        "This index is auto-generated from all forked repos in this org that start with `know-`.",
        "",
        "## 📚 Auto-Indexed Knowledge Repositories",
        "",
        "| Repo | GitHub | MCP |",
        "|------|--------|-----|"
    ]
    for repo in sorted(repos, key=lambda r: r.name):
        name = repo.name
        gh_url = f"https://github.com/{REPO_OWNER}/{name}"
        mcp_url = f"https://gitmcp.io/{REPO_OWNER}/{name}"
        lines.append(f"| `{name}` | [GitHub]({gh_url}) | [MCP Viewer]({mcp_url}) |")

    lines.append("")
    lines.append(f"_Last updated: {time.strftime('%Y-%m-%d')}_")
    return "\n".join(lines)

# === Main logic ===
def main():
    jwt_token = generate_jwt(APP_ID, PRIVATE_KEY)
    installation_token = get_installation_token(jwt_token, INSTALLATION_ID)

    gh = Github(installation_token)
    org = gh.get_organization(REPO_OWNER)
    repos = [r for r in org.get_repos() if r.name.startswith("know-")]

    readme_content = generate_readme(repos)

    repo = gh.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    contents = repo.get_contents("README.md")

    if contents.decoded_content.decode() != readme_content:
        repo.update_file(
            path="README.md",
            message="🔄 Auto-update README with latest `know-` repos",
            content=readme_content,
            sha=contents.sha
        )
        print("✅ README.md updated.")
    else:
        print("ℹ️ No change to README.md needed.")

if __name__ == "__main__":
    main()