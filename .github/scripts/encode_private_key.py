#!/usr/bin/env python3
"""
Helper script to encode private key in base64 to avoid GitHub secret masking.
Run this locally to generate the PRIVATE_KEY_BASE64 secret value.
"""

import base64
import sys

def encode_private_key(file_path):
    """Encode private key file to base64"""
    try:
        with open(file_path, 'rb') as f:
            private_key_bytes = f.read()
        
        # Encode to base64
        encoded = base64.b64encode(private_key_bytes).decode('ascii')
        
        print("🔑 Private key successfully encoded to base64!")
        print(f"📄 Original size: {len(private_key_bytes)} bytes")
        print(f"📄 Encoded size: {len(encoded)} characters")
        print()
        print("📋 Add this value as PRIVATE_KEY_BASE64 secret in GitHub:")
        print("=" * 50)
        print(encoded)
        print("=" * 50)
        print()
        print("🛠️  Steps to add the secret:")
        print("1. Go to your GitHub repository settings")
        print("2. Navigate to Secrets and variables > Actions")
        print("3. Click 'New repository secret'")
        print("4. Name: PRIVATE_KEY_BASE64")
        print("5. Value: Copy the encoded string above")
        print("6. Click 'Add secret'")
        
        return encoded
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error encoding private key: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python encode_private_key.py <path_to_private_key.pem>")
        print("Example: python encode_private_key.py private-key.pem")
        sys.exit(1)
    
    file_path = sys.argv[1]
    encode_private_key(file_path) 