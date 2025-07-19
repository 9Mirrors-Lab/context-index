#!/usr/bin/env python3
"""
Test script to verify base64 decoding of private key
"""

import base64
import os

def test_base64_decode():
    """Test the base64 decoding process"""
    print("🧪 Testing base64 decode process...")
    
    # Check if private-key.pem exists (created by workflow)
    if os.path.exists("private-key.pem"):
        print("✅ private-key.pem file found")
        
        # Read the raw file
        with open("private-key.pem", "rb") as f:
            raw_data = f.read()
        
        print(f"📄 File size: {len(raw_data)} bytes")
        print(f"📄 First 20 bytes: {raw_data[:20].hex()}")
        
        # Check if it's valid UTF-8 text
        try:
            text = raw_data.decode('utf-8')
            print("✅ Successfully decoded as UTF-8")
            print(f"📄 Starts with: {repr(text[:50])}")
            
            # Check if it's a proper PEM file
            if text.startswith("-----BEGIN"):
                print("✅ Appears to be a proper PEM file")
            else:
                print("❌ Does not start with PEM header")
                print("🔍 This might be a base64 encoding issue")
                
        except UnicodeDecodeError as e:
            print(f"❌ UTF-8 decode failed: {e}")
            print("🔍 File contains binary data - possible base64 issue")
            
            # Try to decode as base64
            try:
                decoded = base64.b64decode(raw_data)
                print(f"🔧 Base64 decode attempt: {len(decoded)} bytes")
                try:
                    pem_text = decoded.decode('utf-8')
                    print("✅ Base64 -> UTF-8 decode successful")
                    print(f"📄 PEM content starts: {repr(pem_text[:50])}")
                except UnicodeDecodeError:
                    print("❌ Even after base64 decode, UTF-8 decode fails")
            except Exception as e:
                print(f"❌ Base64 decode failed: {e}")
    else:
        print("❌ private-key.pem not found")
        return False
    
    return True

if __name__ == "__main__":
    test_base64_decode() 