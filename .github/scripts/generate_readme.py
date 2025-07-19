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
        if not os.path.exists(PRIVATE_KEY_PATH):
            raise FileNotFoundError(f"Private key file not found: {PRIVATE_KEY_PATH}")
        
        with open(PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read()
        
        print(f"📄 Private key loaded, length: {len(private_key)} characters")
        print(f"📄 First 100 chars: '{private_key[:100]}'")
        print(f"📄 Last 100 chars: '{private_key[-100:]}'")
        
        # Enhanced validation
        if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            print("🔧 Private key missing RSA header, attempting to add...")
            private_key = private_key.replace("\\n", "\n")
            if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
                with open(PRIVATE_KEY_PATH, "w") as f:
                    f.write(private_key)
                print("🔧 Added RSA headers and saved")
        
        # Check for PKCS#8 format and convert if needed
        if private_key.startswith("-----BEGIN PRIVATE KEY-----"):
            print("🔧 Detected PKCS#8 format, attempting conversion...")
            try:
                # Load PKCS#8 key and convert to traditional RSA format
                import cryptography.hazmat.primitives.serialization as serialization
                from cryptography.hazmat.primitives import serialization as ser
                
                pkcs8_key = serialization.load_pem_private_key(
                    private_key.encode('utf-8'),
                    password=None
                )
                
                # Convert to traditional RSA format
                rsa_private_key = pkcs8_key.private_bytes(
                    encoding=ser.Encoding.PEM,
                    format=ser.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=ser.NoEncryption()
                ).decode('utf-8')
                
                print("✅ Successfully converted PKCS#8 to RSA format")
                private_key = rsa_private_key
                
                # Save the converted key
                with open(PRIVATE_KEY_PATH, "w") as f:
                    f.write(private_key)
                print("💾 Saved converted RSA key")
                
            except Exception as conv_e:
                print(f"❌ PKCS#8 conversion failed: {conv_e}")
                # Continue with original key
        
        # Final validation
        if private_key.startswith("-----BEGIN RSA PRIVATE KEY-----") and private_key.endswith("-----END RSA PRIVATE KEY-----"):
            print("✅ Private key appears to be properly formatted")
        else:
            print("⚠️ Private key format may have issues")
            
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
        
        # Try multiple approaches for JWT generation
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
        
        # If all methods fail, try with cryptography backend explicitly
        try:
            print("🔧 Trying with explicit cryptography backend...")
            import cryptography.hazmat.primitives.serialization as serialization
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            print(f"🔧 Key starts with: '{private_key_str[:50]}...'")
            print(f"🔧 Key ends with: '...{private_key_str[-50:]}'")
            
            # Try to load the private key using cryptography with detailed error handling
            try:
                private_key_obj = serialization.load_pem_private_key(
                    private_key_str.encode('utf-8'),
                    password=None
                )
                print("✅ Cryptography library successfully loaded the private key")
            except Exception as key_load_error:
                print(f"❌ Cryptography key loading failed: {key_load_error}")
                # Try with stripped key
                try:
                    stripped_key = private_key_str.strip()
                    print(f"🔧 Trying with stripped key (length: {len(stripped_key)})")
                    private_key_obj = serialization.load_pem_private_key(
                        stripped_key.encode('utf-8'),
                        password=None
                    )
                    print("✅ Cryptography library loaded stripped key successfully")
                except Exception as stripped_error:
                    print(f"❌ Stripped key also failed: {stripped_error}")
                    # Try cleaning the key content
                    try:
                        # Remove any potential invisible characters and normalize
                        clean_key = ''.join(char for char in private_key_str if ord(char) < 128)
                        clean_key = clean_key.replace('\r\n', '\n').replace('\r', '\n')
                        print(f"🔧 Trying with cleaned key (length: {len(clean_key)})")
                        private_key_obj = serialization.load_pem_private_key(
                            clean_key.encode('utf-8'),
                            password=None
                        )
                        print("✅ Cryptography library loaded cleaned key successfully")
                        private_key_str = clean_key  # Use the cleaned key for JWT
                    except Exception as clean_error:
                        print(f"❌ Cleaned key also failed: {clean_error}")
                        raise clean_error
            
            # Create JWT manually using cryptography
            header = {"alg": "RS256", "typ": "JWT"}
            import base64
            import json
            
            # Encode header and payload
            header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
            payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
            
            # Create signature
            message = f"{header_b64}.{payload_b64}".encode()
            signature = private_key_obj.sign(
                message,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
            
            token = f"{header_b64}.{payload_b64}.{signature_b64}"
            print("✅ JWT token generated successfully with cryptography backend")
            print(f"   Token length: {len(token)}")
            return token
            
        except Exception as e:
            print(f"❌ Cryptography backend also failed: {e}")
            raise Exception(f"All JWT generation methods failed. Last error: {e}")
            
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
