# .github/scripts/generate_readme.py

import os
import jwt
import time
import requests
from github import Github

# === Load env vars from GitHub Actions ===
APP_ID = os.getenv("APP_ID")
INSTALLATION_ID = os.getenv("INSTALLATION_ID")
PRIVATE_KEY_PATH = "private-key.pem"

# Read and format private key properly
def load_private_key():
    try:
        with open(PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read()
        
        # Ensure proper PEM formatting
        if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            # If it's not properly formatted, try to fix it
            private_key = private_key.replace("\\n", "\n")
            if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                # If still not formatted, wrap it
                private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
        
        return private_key
    except FileNotFoundError:
        print(f"❌ Private key file not found: {PRIVATE_KEY_PATH}")
        raise
    except Exception as e:
        print(f"❌ Error loading private key: {e}")
        raise

PRIVATE_KEY = load_private_key()
REPO_OWNER = "9Mirrors-Lab"
REPO_NAME = "knowledge-index"

# === Generate JWT ===
def generate_jwt(app_id, private_key_str):
    try:
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": app_id
        }
        return jwt.encode(payload, private_key_str, algorithm="RS256")
    except Exception as e:
        print(f"❌ Error generating JWT: {e}")
        print(f"App ID: {app_id}")
        print(f"Private key length: {len(private_key_str)}")
        print(f"Private key starts with: {private_key_str[:50]}...")
        raise

# === Get installation token ===
def get_installation_token(jwt_token, installation_id):
    try:
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()["token"]
    except Exception as e:
        print(f"❌ Error getting installation token: {e}")
        raise

# === Generate new README content ===
def generate_readme(repos):
    lines = [
        "# 📘 9Mirrors Knowledge Index",
        "",
        "[![MCP Enabled](https://img.shields.io/badge/MCP-ready-blueviolet)](https://gitmcp.io/9Mirrors-Lab/knowledge-index)",
        "[![Last Update](https://img.shields.io/github/last-commit/9Mirrors-Lab/knowledge-index)](https://github.com/9Mirrors-Lab/knowledge-index/commits/main)",
        "",
        "This is a centralized index of reference repositories designed to support AI tools like Claude, GitMCP, Cursor, and custom LLM workflows. Each listed repo contains curated code, prompts, or workflow assets prepared for AI context ingestion.",
        "",
        "---",
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

    lines.extend([
        "",
        "---",
        "",
        "## 🧩 Usage",
        "",
        "These repos are structured to support:",
        "- Claude and Cursor via `mcp.json`",
        "- Augment Code workflows", 
        "- GitMCP-hosted viewers and assistant lookups",
        "",
        "> To add these to your AI coding tools, point to the `mcp.json` link under the MCP column.",
        "",
        "---",
        "",
        f"_Last updated: {time.strftime('%Y-%m-%d')}_"
    ])
    return "\n".join(lines)

# === Main logic ===
def main():
    try:
        print("🔑 Generating JWT token...")
        jwt_token = generate_jwt(APP_ID, PRIVATE_KEY)
        print("✅ JWT token generated successfully")
        
        print("🔑 Getting installation token...")
        installation_token = get_installation_token(jwt_token, INSTALLATION_ID)
        print("✅ Installation token obtained successfully")

        print("📚 Fetching repositories...")
        gh = Github(installation_token)
        org = gh.get_organization(REPO_OWNER)
        repos = [r for r in org.get_repos() if r.name.startswith("know-")]
        print(f"✅ Found {len(repos)} repositories starting with 'know-'")

        print("📝 Generating README content...")
        readme_content = generate_readme(repos)

        print("📄 Updating README.md...")
        repo = gh.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        contents = repo.get_contents("README.md")

        if contents.decoded_content.decode() != readme_content:
            repo.update_file(
                path="README.md",
                message="🔄 Auto-update README with latest `know-` repos",
                content=readme_content,
                sha=contents.sha
            )
            print("✅ README.md updated successfully.")
        else:
            print("ℹ️ No change to README.md needed.")
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
