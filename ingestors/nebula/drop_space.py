#!/usr/bin/env python3
"""
Simple script to drop a Nebula Graph space
"""

import sys
from pathlib import Path

try:
    from nebula3.gclient.net import ConnectionPool
    from nebula3.Config import Config
    from nebula3.gclient.net.Session import Session
except ImportError:
    print("Error: nebula3-python package not found. Please install it with:")
    print("pip install nebula3-python")
    sys.exit(1)

from config_loader import ConfigLoader


def drop_space(space_name: str, config_file: str = "config.yaml"):
    """Drop a Nebula Graph space"""
    config_loader = ConfigLoader(config_file)
    connection = config_loader.get_nebula_connection()
    
    print(f"Dropping space: {space_name}")
    print(f"Connecting to: {connection['host']}:{connection['port']}")
    
    try:
        # Connect to Nebula Graph
        config = Config()
        connection_pool = ConnectionPool()
        init_result = connection_pool.init([(connection['host'], connection['port'])], config)
        if not init_result:
            print(f"Failed to initialize connection pool")
            return False
        
        session = connection_pool.get_session(connection['username'], connection['password'])
        if not session:
            print("Failed to get session")
            return False
        
        print(f"Successfully connected to Nebula Graph")
        
        # Drop the space
        drop_statement = f"DROP SPACE {space_name}"
        print(f"Executing: {drop_statement}")
        
        result = session.execute(drop_statement)
        if result.is_succeeded():
            print(f"✓ Successfully dropped space: {space_name}")
            return True
        else:
            print(f"✗ Failed to drop space: {result.error_msg()}")
            return False
            
    except Exception as e:
        print(f"Error dropping space: {e}")
        return False
    finally:
        if 'session' in locals():
            session.release()
        if 'connection_pool' in locals():
            connection_pool.close()


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python drop_space.py <space_name>")
        sys.exit(1)
    
    space_name = sys.argv[1]
    success = drop_space(space_name)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
