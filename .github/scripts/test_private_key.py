#!/usr/bin/env python3
"""
Test private key file formatting and readability.
This is a diagnostic script that should not block the workflow.
"""

import sys
import os

def main():
    try:
        # Check if private key file exists
        if not os.path.exists('private-key.pem'):
            print("❌ private-key.pem file not found")
            return  # Exit gracefully, don't block workflow
            
        # Get file size
        file_size = os.path.getsize('private-key.pem')
        print(f"📄 Private key file size: {file_size} bytes")
        
        # Read first 20 bytes as binary for hex analysis
        with open('private-key.pem', 'rb') as f:
            first_bytes = f.read(20)
            print(f"📄 First 20 bytes (hex): {first_bytes.hex()}")
            print(f"📄 First 20 bytes (repr): {repr(first_bytes)}")
        
        # Try to read as text
        try:
            with open('private-key.pem', 'r', encoding='utf-8') as f:
                content = f.read()
                print("📄 Successfully decoded as UTF-8")
                
                # Show first and last 100 characters
                if len(content) >= 200:
                    print(f"📄 First 100 characters: {repr(content[:100])}")
                    print(f"📄 Last 100 characters: {repr(content[-100:])}")
                
                # Check for PEM format
                if content.startswith('-----BEGIN'):
                    print("✅ File appears to be in PEM format")
                else:
                    print("⚠️ File doesn't start with PEM header")
                    
        except UnicodeDecodeError as e:
            print(f"❌ UTF-8 decoding failed: {e}")
            
            # Try ASCII
            try:
                with open('private-key.pem', 'r', encoding='ascii') as f:
                    content = f.read()
                    print("📄 Successfully decoded as ASCII")
            except UnicodeDecodeError:
                print("❌ ASCII decoding also failed")
                print("📄 This appears to be binary data, not a text PEM file")
                print("📄 Possible double-encoding or corruption issue")
                
    except Exception as e:
        print(f"❌ Error reading private key file: {e}")
    
    # Always exit with success code - this is just diagnostic
    print("📄 Private key diagnostic completed")

if __name__ == "__main__":
    main() 