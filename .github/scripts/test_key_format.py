#!/usr/bin/env python3
"""
Test script to verify private key format and conversion methods.
"""

import os
import sys
import base64
import subprocess
from pathlib import Path

def test_key_formats():
    """Test different key formats and conversion methods."""
    
    print("🔍 Testing private key formats...")
    
    # Check if we have the local private key file
    local_key_path = Path("index-knowledge-repos.2025-07-18.private-key.pem")
    if not local_key_path.exists():
        print("❌ Local private key file not found!")
        return False
    
    print(f"✅ Found local private key: {local_key_path}")
    
    # Read the original key
    with open(local_key_path, 'rb') as f:
        original_key = f.read()
    
    print(f"📄 Original key length: {len(original_key)} bytes")
    
    # Base64 encode it (like we do for GitHub secrets)
    encoded_key = base64.b64encode(original_key).decode('utf-8')
    print(f"📦 Base64 encoded length: {len(encoded_key)} chars")
    
    # Decode it back (simulate GitHub workflow)
    with open('test-key.der', 'wb') as f:
        f.write(base64.b64decode(encoded_key))
    
    print("✅ Simulated GitHub secret decode")
    
    # Test file detection
    result = subprocess.run(['file', 'test-key.der'], capture_output=True, text=True)
    print(f"🔍 File detection: {result.stdout.strip()}")
    
    # Check first bytes
    with open('test-key.der', 'rb') as f:
        first_bytes = f.read(4)
    print(f"🔍 First bytes: {' '.join(f'{b:02x}' for b in first_bytes)}")
    
    # Test different OpenSSL conversions
    print("\n🔧 Testing OpenSSL conversions...")
    
    # Method 1: Legacy RSA format (what was causing the error)
    try:
        subprocess.run([
            'openssl', 'rsa', 
            '-in', 'test-key.der', '-inform', 'DER',
            '-out', 'test-rsa.pem', '-outform', 'PEM'
        ], check=True, capture_output=True)
        print("✅ RSA format conversion successful")
        
        # Check what we got
        with open('test-rsa.pem', 'r') as f:
            rsa_content = f.read()
        print(f"📄 RSA format header: {rsa_content.split(chr(10))[0]}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ RSA format conversion failed: {e}")
    
    # Method 2: PKCS#8 format (what we want)
    try:
        subprocess.run([
            'openssl', 'pkcs8',
            '-inform', 'DER', '-in', 'test-key.der',
            '-nocrypt', '-out', 'test-pkcs8.pem'
        ], check=True, capture_output=True)
        print("✅ PKCS#8 format conversion successful")
        
        # Check what we got
        with open('test-pkcs8.pem', 'r') as f:
            pkcs8_content = f.read()
        print(f"📄 PKCS#8 format header: {pkcs8_content.split(chr(10))[0]}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PKCS#8 format conversion failed: {e}")
    
    # Test JWT generation with both formats
    print("\n🔧 Testing JWT generation with different formats...")
    
    # Import here to avoid issues if not installed
    try:
        import jwt
        from cryptography.hazmat.primitives import serialization
        
        app_id = "12345"  # Dummy app ID for testing
        
        # Test RSA format
        if os.path.exists('test-rsa.pem'):
            try:
                with open('test-rsa.pem', 'r') as f:
                    rsa_key = f.read()
                
                # Try to load with cryptography
                private_key = serialization.load_pem_private_key(
                    rsa_key.encode('utf-8'),
                    password=None
                )
                print("✅ RSA format: Cryptography loading successful")
                
                # Try JWT generation
                payload = {"iss": app_id, "exp": 1234567890}
                token = jwt.encode(payload, private_key, algorithm="RS256")
                print("✅ RSA format: JWT generation successful")
                
            except Exception as e:
                print(f"❌ RSA format failed: {e}")
        
        # Test PKCS#8 format
        if os.path.exists('test-pkcs8.pem'):
            try:
                with open('test-pkcs8.pem', 'r') as f:
                    pkcs8_key = f.read()
                
                # Try to load with cryptography
                private_key = serialization.load_pem_private_key(
                    pkcs8_key.encode('utf-8'),
                    password=None
                )
                print("✅ PKCS#8 format: Cryptography loading successful")
                
                # Try JWT generation
                payload = {"iss": app_id, "exp": 1234567890}
                token = jwt.encode(payload, private_key, algorithm="RS256")
                print("✅ PKCS#8 format: JWT generation successful")
                
            except Exception as e:
                print(f"❌ PKCS#8 format failed: {e}")
                
    except ImportError:
        print("⚠️ PyJWT or cryptography not installed, skipping JWT tests")
    
    # Cleanup
    for test_file in ['test-key.der', 'test-rsa.pem', 'test-pkcs8.pem']:
        if os.path.exists(test_file):
            os.remove(test_file)
    
    print("\n✅ Key format testing complete!")
    return True

if __name__ == "__main__":
    success = test_key_formats()
    sys.exit(0 if success else 1) 