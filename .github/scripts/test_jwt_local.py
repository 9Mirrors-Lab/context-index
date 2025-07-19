#!/usr/bin/env python3
"""
Local test for JWT generation with actual private key
"""

import time
import jwt
import json
import base64

def test_jwt_methods():
    """Test JWT generation with multiple methods"""
    print("🧪 Testing JWT generation methods...")
    
    # Read the private key
    try:
        with open("private-key.pem", "r") as f:
            private_key = f.read()
        
        print(f"📄 Key length: {len(private_key)}")
        print(f"📄 Key starts: {private_key[:100]}...")
        
        # Test payload (using dummy app_id)
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": "12345"  # Dummy app_id for testing
        }
        
        print("\n🔑 Testing JWT generation methods...")
        
        # Method 1: Direct PyJWT
        try:
            token1 = jwt.encode(payload, private_key, algorithm="RS256")
            print("✅ Method 1 (PyJWT direct): SUCCESS")
            print(f"   Token length: {len(token1)}")
            return True
        except Exception as e:
            print(f"❌ Method 1 (PyJWT direct): {e}")
        
        # Method 2: Stripped key
        try:
            stripped_key = private_key.strip()
            token2 = jwt.encode(payload, stripped_key, algorithm="RS256")
            print("✅ Method 2 (PyJWT stripped): SUCCESS")
            return True
        except Exception as e:
            print(f"❌ Method 2 (PyJWT stripped): {e}")
        
        # Method 3: Manual JWT with cryptography
        try:
            print("🔧 Trying manual JWT creation with cryptography...")
            import cryptography.hazmat.primitives.serialization as serialization
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # Load the private key using cryptography
            private_key_obj = serialization.load_pem_private_key(
                private_key.encode('utf-8'),
                password=None
            )
            
            # Create JWT manually
            header = {"alg": "RS256", "typ": "JWT"}
            
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
            
            token3 = f"{header_b64}.{payload_b64}.{signature_b64}"
            print("✅ Method 3 (Manual cryptography): SUCCESS")
            print(f"   Token length: {len(token3)}")
            return True
            
        except Exception as e:
            print(f"❌ Method 3 (Manual cryptography): {e}")
        
        print("❌ All methods failed")
        return False
        
    except Exception as e:
        print(f"❌ Error reading key: {e}")
        return False

if __name__ == "__main__":
    success = test_jwt_methods()
    exit(0 if success else 1) 