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
REPO_OWNER = "9Mirrors-Lab"
REPO_NAME = "knowledge-index"

# Read and format private key properly
def load_private_key():
    try:
        print(f"🔍 Looking for private key at: {PRIVATE_KEY_PATH}")
        if not os.path.exists(PRIVATE_KEY_PATH):
            print(f"❌ Private key file not found: {PRIVATE_KEY_PATH}")
            print(f"📁 Current directory contents:")
            for file in os.listdir("."):
                print(f"   - {file}")
            raise FileNotFoundError(f"Private key file not found: {PRIVATE_KEY_PATH}")
        
        with open(PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read()
        
        print(f"📄 Private key loaded, length: {len(private_key)} characters")
        print(f"📄 First 100 chars: {repr(private_key[:100])}")
        print(f"📄 Last 100 chars: {repr(private_key[-100:])}")
        
        # Ensure proper PEM formatting
        if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            print("⚠️ Private key doesn't start with proper PEM header, attempting to fix...")
            # If it's not properly formatted, try to fix it
            private_key = private_key.replace("\\n", "\n")
            if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                print("⚠️ Still not formatted, wrapping with PEM headers...")
                # If still not formatted, wrap it
                private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
            
            # Write the fixed key back
            with open(PRIVATE_KEY_PATH, "w") as f:
                f.write(private_key)
            print("✅ Fixed private key written back to file")
        
        # Final verification
        if "-----BEGIN RSA PRIVATE KEY-----" in private_key and "-----END RSA PRIVATE KEY-----" in private_key:
            print("✅ Private key appears to be properly formatted")
        else:
            print("❌ Private key still not properly formatted after fixes")
            raise ValueError("Private key not in proper PEM format")
        
        return private_key
    except Exception as e:
        print(f"❌ Error loading private key: {e}")
        raise

# === Generate JWT ===
def generate_jwt(app_id, private_key_str):
    try:
        print(f"🔑 Generating JWT with app_id: {app_id}")
        print(f"🔑 Private key length: {len(private_key_str)}")
        print(f"🔑 Private key starts with: {private_key_str[:50]}...")
        
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": app_id
        }
        
        # Use the private key directly - PyJWT handles RSA private keys correctly
        token = jwt.encode(payload, private_key_str, algorithm="RS256")
        print("✅ JWT token generated successfully")
        return token
    except jwt.InvalidKeyError as e:
        print(f"❌ Invalid key format: {e}")
        print("🔧 Attempting to fix key format...")
        
        # Try to fix common key format issues
        try:
            # Remove any extra whitespace and ensure proper line breaks
            cleaned_key = private_key_str.strip()
            if not cleaned_key.endswith('\n'):
                cleaned_key += '\n'
            
            token = jwt.encode(payload, cleaned_key, algorithm="RS256")
            print("✅ JWT token generated successfully with cleaned key")
            return token
        except Exception as e2:
            print(f"❌ Still failed with cleaned key: {e2}")
            raise
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
        print("🚀 Starting README generation process...")
        print(f"📋 Environment check:")
        print(f"   - APP_ID: {APP_ID}")
        print(f"   - INSTALLATION_ID: {INSTALLATION_ID}")
        print(f"   - REPO_OWNER: {REPO_OWNER}")
        print(f"   - REPO_NAME: {REPO_NAME}")
        
        print("🔑 Loading private key...")
        private_key = load_private_key()
        
        print("🔑 Generating JWT token...")
        jwt_token = generate_jwt(APP_ID, private_key)
        
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

        print("�� Updating README.md...")
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
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
