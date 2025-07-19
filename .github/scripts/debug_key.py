#!/usr/bin/env python3
"""
Standalone script to debug private key issues
"""

import os
import sys
import jwt
import time

def debug_private_key():
    """Debug private key loading and JWT generation"""
    print("🔍 Debugging private key issues...")
    
    # Check environment variables
    app_id = os.getenv("APP_ID")
    installation_id = os.getenv("INSTALLATION_ID")
    
    print(f"📋 Environment variables:")
    print(f"   - APP_ID: {app_id}")
    print(f"   - INSTALLATION_ID: {installation_id}")
    
    # Check if private key file exists
    private_key_path = "private-key.pem"
    print(f"\n📁 Checking for private key file: {private_key_path}")
    
    if not os.path.exists(private_key_path):
        print(f"❌ Private key file not found!")
        print(f"📁 Current directory contents:")
        for file in os.listdir("."):
            print(f"   - {file}")
        return False
    
    print(f"✅ Private key file found")
    
    # Read and analyze the private key
    try:
        with open(private_key_path, "r") as f:
            private_key = f.read()
        
        print(f"\n📄 Private key analysis:")
        print(f"   - File size: {len(private_key)} characters")
        print(f"   - First 100 chars: {repr(private_key[:100])}")
        print(f"   - Last 100 chars: {repr(private_key[-100:])}")
        
        # Check for PEM formatting
        has_header = "-----BEGIN RSA PRIVATE KEY-----" in private_key
        has_footer = "-----END RSA PRIVATE KEY-----" in private_key
        
        print(f"\n🔍 PEM format check:")
        print(f"   - Has header: {has_header}")
        print(f"   - Has footer: {has_footer}")
        
        if not has_header or not has_footer:
            print("⚠️ Private key is not properly formatted!")
            print("🔧 Attempting to fix...")
            
            # Try to fix formatting
            fixed_key = private_key.replace("\\n", "\n")
            if not fixed_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                fixed_key = f"-----BEGIN RSA PRIVATE KEY-----\n{fixed_key}\n-----END RSA PRIVATE KEY-----"
            
            print(f"🔧 Fixed key starts with: {repr(fixed_key[:100])}")
            
            # Test JWT generation with fixed key
            try:
                payload = {
                    "iat": int(time.time()) - 60,
                    "exp": int(time.time()) + (10 * 60),
                    "iss": app_id
                }
                
                token = jwt.encode(payload, fixed_key, algorithm="RS256")
                print("✅ JWT generation successful with fixed key!")
                return True
                
            except Exception as e:
                print(f"❌ JWT generation failed with fixed key: {e}")
                return False
        
        else:
            print("✅ Private key appears to be properly formatted")
            
            # Test JWT generation with original key
            try:
                payload = {
                    "iat": int(time.time()) - 60,
                    "exp": int(time.time()) + (10 * 60),
                    "iss": app_id
                }
                
                token = jwt.encode(payload, private_key, algorithm="RS256")
                print("✅ JWT generation successful with original key!")
                return True
                
            except jwt.InvalidKeyError as e:
                print(f"❌ JWT generation failed with original key: {e}")
                print("🔧 This is likely a key format issue. Trying to fix...")
                
                # Try to fix the key format
                try:
                    # Clean the key - remove extra whitespace and ensure proper formatting
                    cleaned_key = private_key.strip()
                    if not cleaned_key.endswith('\n'):
                        cleaned_key += '\n'
                    
                    # Ensure proper PEM formatting
                    if not cleaned_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                        cleaned_key = f"-----BEGIN RSA PRIVATE KEY-----\n{cleaned_key}\n-----END RSA PRIVATE KEY-----"
                    
                    token = jwt.encode(payload, cleaned_key, algorithm="RS256")
                    print("✅ JWT generation successful with cleaned key!")
                    return True
                    
                except Exception as e2:
                    print(f"❌ JWT generation still failed with cleaned key: {e2}")
                    print("🔍 This might be a different issue - check the private key content")
                    return False
                    
            except Exception as e:
                print(f"❌ JWT generation failed with original key: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error reading private key: {e}")
        return False

if __name__ == "__main__":
    success = debug_private_key()
    sys.exit(0 if success else 1) 