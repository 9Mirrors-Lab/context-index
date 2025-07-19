#!/usr/bin/env python3
"""
Test script to debug private key formatting issues
"""

import os
import sys

def test_private_key():
    """Test private key loading and formatting"""
    private_key_path = "private-key.pem"
    
    if not os.path.exists(private_key_path):
        print(f"❌ Private key file not found: {private_key_path}")
        return False
    
    try:
        # First, check the raw file size and type
        file_size = os.path.getsize(private_key_path)
        print(f"📄 Private key file size: {file_size} bytes")
        
        # Try to read as binary first to see what we're dealing with
        with open(private_key_path, "rb") as f:
            raw_data = f.read()
        
        print(f"📄 First 20 bytes (hex): {raw_data[:20].hex()}")
        print(f"📄 First 20 bytes (repr): {repr(raw_data[:20])}")
        
        # Check if it looks like text (PEM format should be ASCII)
        try:
            private_key = raw_data.decode('utf-8')
            print(f"📄 Successfully decoded as UTF-8")
            print(f"📄 First 100 characters: {repr(private_key[:100])}")
            print(f"📄 Last 100 characters: {repr(private_key[-100:])}")
        except UnicodeDecodeError as e:
            print(f"❌ UTF-8 decoding failed: {e}")
            # Try to decode as ASCII
            try:
                private_key = raw_data.decode('ascii')
                print(f"📄 Successfully decoded as ASCII")
                print(f"📄 First 100 characters: {repr(private_key[:100])}")
            except UnicodeDecodeError:
                print(f"❌ ASCII decoding also failed")
                print(f"📄 This appears to be binary data, not a text PEM file")
                print(f"📄 Possible double-encoding or corruption issue")
                return False
            
            # Check for proper PEM formatting
            if "-----BEGIN RSA PRIVATE KEY-----" in private_key:
                print("✅ Private key contains proper PEM header")
            else:
                print("❌ Private key missing PEM header")
                print("🔧 Attempting to fix formatting...")
                
                # Try to fix formatting
                fixed_key = private_key.replace("\\n", "\n")
                if not fixed_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                    fixed_key = f"-----BEGIN RSA PRIVATE KEY-----\n{fixed_key}\n-----END RSA PRIVATE KEY-----"
                
                print(f"🔧 Fixed key starts with: {repr(fixed_key[:100])}")
                
                # Write fixed key back
                with open(private_key_path, "w") as f:
                    f.write(fixed_key)
                print("✅ Fixed private key written back to file")
                
            return True
        
    except Exception as e:
        print(f"❌ Error reading private key: {e}")
        return False

if __name__ == "__main__":
    success = test_private_key()
    sys.exit(0 if success else 1) 