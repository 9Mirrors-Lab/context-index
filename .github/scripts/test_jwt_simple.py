#!/usr/bin/env python3
"""
Simple JWT test script to debug key issues
"""

import os
import jwt
import time

def test_jwt_simple():
    """Simple JWT test with minimal setup"""
    print("🧪 Simple JWT test...")
    
    # Check environment
    app_id = os.getenv("APP_ID")
    print(f"📋 APP_ID: {app_id}")
    
    # Read private key
    try:
        with open("private-key.pem", "r") as f:
            private_key = f.read()
        
        print(f"📄 Key length: {len(private_key)}")
        print(f"📄 Key starts: {repr(private_key[:100])}")
        print(f"📄 Key ends: {repr(private_key[-100:])}")
        
        # Test different approaches
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": app_id
        }
        
        print("\n🔑 Testing JWT generation...")
        
        # Method 1: Direct key
        try:
            token1 = jwt.encode(payload, private_key, algorithm="RS256")
            print("✅ Method 1 (direct): Success")
            return True
        except Exception as e:
            print(f"❌ Method 1 (direct): {e}")
        
        # Method 2: Stripped key
        try:
            stripped_key = private_key.strip()
            token2 = jwt.encode(payload, stripped_key, algorithm="RS256")
            print("✅ Method 2 (stripped): Success")
            return True
        except Exception as e:
            print(f"❌ Method 2 (stripped): {e}")
        
        # Method 3: Ensure newline at end
        try:
            nl_key = private_key.strip() + "\n"
            token3 = jwt.encode(payload, nl_key, algorithm="RS256")
            print("✅ Method 3 (with newline): Success")
            return True
        except Exception as e:
            print(f"❌ Method 3 (with newline): {e}")
        
        # Method 4: Try with cryptography backend
        try:
            import cryptography
            print("🔧 Trying with cryptography backend...")
            token4 = jwt.encode(payload, private_key, algorithm="RS256")
            print("✅ Method 4 (cryptography): Success")
            return True
        except Exception as e:
            print(f"❌ Method 4 (cryptography): {e}")
        
        print("❌ All methods failed")
        return False
        
    except Exception as e:
        print(f"❌ Error reading key: {e}")
        return False

if __name__ == "__main__":
    success = test_jwt_simple()
    exit(0 if success else 1) 