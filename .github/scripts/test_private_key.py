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
        with open(private_key_path, "r") as f:
            private_key = f.read()
        
        print(f"📄 Private key file size: {len(private_key)} characters")
        print(f"📄 First 100 characters: {repr(private_key[:100])}")
        print(f"📄 Last 100 characters: {repr(private_key[-100:])}")
        
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