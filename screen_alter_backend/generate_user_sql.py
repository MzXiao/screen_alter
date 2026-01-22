#!/usr/bin/env python3
import sys
import argparse
from datetime import datetime

try:
    from auth import hash_password
except ImportError:
    # Handle running from different directories
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from auth import hash_password

def generate_sql(username, password, expires_at):
    """Generate INSERT SQL for a new user."""
    pwd_hash = hash_password(password)
    
    # Format: INSERT INTO users (username, password_hash, expires_at) VALUES ('...', '...', '...');
    # Using MySQL syntax
    if expires_at:
        sql = f"INSERT INTO users (username, password_hash, expires_at) VALUES ('{username}', '{pwd_hash}', '{expires_at}');"
    else:
        sql = f"INSERT INTO users (username, password_hash) VALUES ('{username}', '{pwd_hash}');"
        
    return sql

def main():
    # parser = argparse.ArgumentParser(description='Generate MySQL INSERT SQL for a new user.')
    # parser.add_argument('--username', required=True, help='Username for the new user')
    # parser.add_argument('--password', required=True, help='Password for the new user')
    # parser.add_argument('--expires', help='Expiration date (YYYY-MM-DD HH:MM:SS)')
    #
    # args = parser.parse_args()
    #
    # try:
    #     if args.expires:
    #         # Validate date format
    #         datetime.strptime(args.expires, '%Y-%m-%d %H:%M:%S')
    # except ValueError:
    #     print("Error: Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'")
    #     sys.exit(1)
    args = {
        "username": 'test',
        "password": 'test123',
        "expires": '2026-01-30 00:00:00',
    }

    sql = generate_sql(args['username'], args['password'], args['expires'])
    print("\n--- Generated SQL ---")
    print(sql)
    print("---------------------\n")

if __name__ == "__main__":
    main()
