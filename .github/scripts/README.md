# GitHub Scripts

This directory contains scripts for automating README generation and managing GitHub App authentication.

## 🔑 Private Key Setup (IMPORTANT)

### The GitHub Secret Masking Problem

GitHub automatically masks certain patterns in secrets that it detects as potentially sensitive. Unfortunately, this can corrupt RSA private keys by replacing parts of the key content with `***`, making the key invalid.

### Solution: Base64 Encoding

To avoid this issue, we encode the private key in base64 before storing it as a GitHub secret.

### Setup Steps

1. **Encode your private key:**
   ```bash
   python .github/scripts/encode_private_key.py your-private-key.pem
   ```

2. **Add the base64 encoded value as a GitHub secret:**
   - Go to repository Settings → Secrets and variables → Actions
   - Create a new secret named `PRIVATE_KEY_BASE64`
   - Use the base64 encoded string as the value

3. **Keep your existing secrets:**
   - `APP_ID` - Your GitHub App ID
   - `INSTALLATION_ID` - Your GitHub App Installation ID

## 📁 Script Files

- **`generate_readme.py`** - Main script that generates README content by fetching repositories
- **`debug_key.py`** - Diagnostic script for troubleshooting JWT/key issues
- **`test_private_key.py`** - Tests private key formatting and validation
- **`check_dependencies.py`** - Verifies PyJWT and cryptography library compatibility
- **`encode_private_key.py`** - Helper to encode private key for GitHub secrets
- **`test_jwt_local.py`** - Local JWT generation testing

## 🔧 How It Works

1. **Private key loading:** The workflow decodes the base64 secret to restore the original PEM file
2. **JWT generation:** Creates a JWT token using the GitHub App credentials
3. **API access:** Uses the JWT to get an installation access token
4. **Repository fetching:** Queries for repositories starting with "know-"
5. **README generation:** Updates the main README with the repository table

## 🚨 Troubleshooting

If you see errors like:
- `InvalidHeader("***")` - Your private key is being masked by GitHub
- `Could not parse the provided public key` - Key format or encoding issue

**Solution:** Follow the base64 encoding steps above to fix GitHub secret masking. 