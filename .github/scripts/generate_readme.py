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
    """Load the private key from file (already converted to PKCS#8 by workflow)."""
    try:
        print(f"📂 Reading private key from: {PRIVATE_KEY_PATH}")
        
        with open(PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read().strip()
        
        print(f"🔑 Private key loaded successfully")
        print(f"🔑 Key length: {len(private_key)} characters")
        print(f"🔑 Key starts with: {private_key[:50]}...")
        print(f"🔑 Key ends with: ...{private_key[-50:]}")
        
        # Basic validation - should be PKCS#8 format now
        if private_key.startswith("-----BEGIN PRIVATE KEY-----") and private_key.endswith("-----END PRIVATE KEY-----"):
            print("✅ Private key is in PKCS#8 format")
        elif private_key.startswith("-----BEGIN RSA PRIVATE KEY-----") and private_key.endswith("-----END RSA PRIVATE KEY-----"):
            print("⚠️ Private key is in PKCS#1 format - workflow conversion may have failed")
        else:
            print("❌ Private key format not recognized")
            
        return private_key
        
    except Exception as e:
        print(f"❌ Error loading private key: {e}")
        raise

# === Generate JWT ===
def generate_jwt(app_id, private_key_str):
    try:
        print(f"🔑 Generating JWT with app_id: {app_id}")
        print(f"🔑 Private key length: {len(private_key_str)}")
        print(f"🔑 Private key starts with: {private_key_str[:30]}...")
        
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": app_id
        }
        
        # Use cryptography library to load the private key properly
        try:
            from cryptography.hazmat.primitives import serialization
            
            # Load the private key using cryptography
            private_key = serialization.load_pem_private_key(
                private_key_str.encode('utf-8'),
                password=None
            )
            print("✅ Private key loaded successfully with cryptography")
            
            # Generate JWT using the loaded private key
            token = jwt.encode(payload, private_key, algorithm="RS256")
            print("✅ JWT token generated successfully")
            return token
            
        except Exception as crypto_e:
            print(f"❌ Cryptography method failed: {crypto_e}")
            
            # Fallback: Try direct string methods (for backward compatibility)
            print("🔧 Trying fallback methods...")
            methods = [
                ("direct", private_key_str),
                ("stripped", private_key_str.strip()),
                ("with_newline", private_key_str.strip() + "\n"),
            ]
            
            for method_name, key in methods:
                try:
                    print(f"🔧 Trying method: {method_name}")
                    token = jwt.encode(payload, key, algorithm="RS256")
                    print(f"✅ JWT token generated successfully with {method_name}")
                    return token
                except Exception as e:
                    print(f"❌ Method {method_name} failed: {e}")
                    continue
            
            raise Exception(f"All JWT generation methods failed. Last error: {crypto_e}")
        
    except Exception as e:
        print(f"❌ Error generating JWT: {e}")
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
