#!/usr/bin/env python3
"""
Check dependencies and their versions
"""

import sys

def check_dependencies():
    """Check PyJWT and cryptography versions"""
    print("🔍 Checking dependencies...")
    
    # Check PyJWT
    try:
        import jwt
        print(f"✅ PyJWT version: {jwt.__version__}")
    except ImportError:
        print("❌ PyJWT not installed")
        return False
    except AttributeError:
        print("✅ PyJWT installed (version unknown)")
    
    # Check cryptography
    try:
        import cryptography
        print(f"✅ Cryptography version: {cryptography.__version__}")
    except ImportError:
        print("❌ Cryptography not installed")
        return False
    except AttributeError:
        print("✅ Cryptography installed (version unknown)")
    
    # Check if PyJWT has cryptography backend
    try:
        import jwt
        # Try to access the cryptography backend
        jwt._jwt_global_obj._algorithms.get('RS256')
        print("✅ PyJWT has RS256 algorithm support")
    except Exception as e:
        print(f"❌ PyJWT RS256 support issue: {e}")
        return False
    
    print("✅ All dependencies look good")
    return True

if __name__ == "__main__":
    success = check_dependencies()
    exit(0 if success else 1) 