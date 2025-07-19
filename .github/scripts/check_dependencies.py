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
    
    # Safe check for PyJWT RS256 support
    try:
        supported_algorithms = jwt.get_algorithms()  # Available in PyJWT 2.x
        if 'RS256' in supported_algorithms:
            print("✅ PyJWT supports RS256 algorithm")
        else:
            print("❌ PyJWT does not support RS256")
            return False
    except AttributeError:
        # Fallback for versions without get_algorithms()
        try:
            # Try to get the algorithm object
            alg_obj = jwt.algorithms.RSAAlgorithm(jwt.algorithms.hashes.SHA256)
            print("✅ PyJWT has RS256 support (via algorithm object)")
        except Exception as e:
            print(f"❌ PyJWT RS256 support issue: {e}")
            return False
    
    print("✅ All dependencies look good")
    return True

if __name__ == "__main__":
    success = check_dependencies()
    exit(0 if success else 1) 