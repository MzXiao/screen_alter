#!/usr/bin/env python
"""
Test script for authentication module.
Run from project root: python test_auth_standalone.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager
from auth.auth_manager import AuthManager
from config import config

def main():
    print("=" * 50)
    print("Authentication Module Test")
    print("=" * 50)
    
    print(f"\nDatabase path: {config.db_path}")
    db_manager = DatabaseManager(config.db_path)
    auth_manager = AuthManager(db_manager)
    
    # Test registration
    print("\n1. Testing registration...")
    success, message = auth_manager.register("testuser", "password123")
    print(f"   Result: {success}")
    print(f"   Message: {message}")
    
    # Test duplicate registration
    print("\n2. Testing duplicate registration...")
    success, message = auth_manager.register("testuser", "password456")
    print(f"   Result: {success}")
    print(f"   Message: {message}")
    
    # Test login with correct password
    print("\n3. Testing login with correct password...")
    success, message = auth_manager.login("testuser", "password123")
    print(f"   Result: {success}")
    print(f"   Message: {message}")
    
    if success:
        user = auth_manager.get_current_user()
        print(f"   Current user: {user}")
    
    # Test logout
    print("\n4. Testing logout...")
    auth_manager.logout()
    print(f"   Is authenticated: {auth_manager.is_authenticated()}")
    
    # Test login with wrong password
    print("\n5. Testing login with wrong password...")
    success, message = auth_manager.login("testuser", "wrongpassword")
    print(f"   Result: {success}")
    print(f"   Message: {message}")
    
    # Test short password
    print("\n6. Testing registration with short password...")
    success, message = auth_manager.register("newuser", "123")
    print(f"   Result: {success}")
    print(f"   Message: {message}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
