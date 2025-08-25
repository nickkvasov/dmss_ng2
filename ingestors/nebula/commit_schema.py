#!/usr/bin/env python3
"""
Nebula Graph Schema Committer

Executes generated schema files against a Nebula Graph database.
This script connects to Nebula Graph and applies schema changes.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
import time

try:
    from nebula3.gclient.net import ConnectionPool
    from nebula3.Config import Config
    from nebula3.gclient.net.Session import Session
except ImportError:
    print("Error: nebula3-python package not found. Please install it with:")
    print("pip install nebula3-python")
    sys.exit(1)

from config_loader import ConfigLoader


class NebulaSchemaCommitter:
    """Commits schema files to Nebula Graph database"""
    
    def __init__(self, config_file: str = "config.yaml", host: str = None, port: int = None,
                 username: str = None, password: str = None, environment: str = None, mock_mode: bool = False):
        """Initialize with configuration file and optional overrides"""
        self.config_loader = ConfigLoader(config_file)
        
        # Get connection parameters from config or use provided overrides
        connection = self.config_loader.get_nebula_connection(environment)
        
        self.host = host or connection.get('host', 'localhost')
        self.port = port or connection.get('port', 9669)
        self.username = username or connection.get('username', 'root')
        self.password = password or connection.get('password', 'nebula')
        self.environment = environment
        self.mock_mode = mock_mode
        
        self.connection_pool = None
        self.session = None
        self.last_error = None
        
    def connect(self) -> bool:
        """Connect to Nebula Graph"""
        if self.mock_mode:
            print(f"Mock mode: Simulating connection to Nebula Graph at {self.host}:{self.port}")
            return True
            
        try:
            # Create connection pool
            config = Config()
            self.connection_pool = ConnectionPool()
            
            # Initialize connection pool
            init_result = self.connection_pool.init([(self.host, self.port)], config)
            if not init_result:
                print(f"Failed to initialize connection pool")
                return False
            
            # Get session
            self.session = self.connection_pool.get_session(self.username, self.password)
            if not self.session:
                print("Failed to get session")
                return False
            
            print(f"Successfully connected to Nebula Graph at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Nebula Graph"""
        if self.mock_mode:
            print("Mock mode: Simulating disconnection from Nebula Graph")
            return
            
        if self.session:
            self.session.release()
        if self.connection_pool:
            self.connection_pool.close()
        print("Disconnected from Nebula Graph")
    
    def execute_statement(self, statement: str) -> bool:
        """Execute a single SQL statement"""
        if self.mock_mode:
            print(f"✓ Mock executed: {statement[:50]}...")
            return True
            
        try:
            result = self.session.execute(statement)
            if result.is_succeeded():
                print(f"✓ Executed: {statement[:50]}...")
                self.last_error = None
                return True
            else:
                error_msg = result.error_msg()
                print(f"✗ Failed: {statement[:50]}...")
                print(f"  Error: {error_msg}")
                self.last_error = error_msg
                return False
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Exception: {statement[:50]}...")
            print(f"  Error: {error_msg}")
            self.last_error = error_msg
            return False
    
    def execute_schema_file(self, schema_file: Path, dry_run: bool = False) -> bool:
        """Execute all statements from a schema file"""
        if not schema_file.exists():
            print(f"Schema file not found: {schema_file}")
            return False
        
        print(f"Processing schema file: {schema_file}")
        
        # Read schema file
        with open(schema_file, 'r') as f:
            content = f.read()
        
        # Parse statements
        statements = self._parse_statements(content)
        
        if dry_run:
            print(f"DRY RUN: Would execute {len(statements)} statements:")
            for i, stmt in enumerate(statements, 1):
                print(f"  {i}. {stmt[:50]}...")
            return True
        
        # Execute statements
        success_count = 0
        total_count = len(statements)
        
        for i, statement in enumerate(statements, 1):
            print(f"[{i}/{total_count}] ", end="")
            if self.execute_statement(statement):
                success_count += 1
                
                # Add delay after space creation to allow propagation
                if "CREATE SPACE" in statement:
                    print("  Waiting for space creation to propagate...")
                    import time
                    time.sleep(10)  # Wait 10 seconds
                    
            else:
                # Special handling for USE statements that might fail due to space propagation delay
                if "USE " in statement and "SpaceNotFound" in str(self.last_error):
                    print("  Retrying USE statement after space creation...")
                    import time
                    time.sleep(5)  # Additional wait
                    
                    # Retry the USE statement
                    if self.execute_statement(statement):
                        print("✓ Retry successful:", statement[:50] + "..." if len(statement) > 50 else statement)
                        success_count += 1
                        continue
                
                print(f"Stopping execution due to error in statement {i}")
                break
        
        print(f"\nExecution completed: {success_count}/{total_count} statements successful")
        return success_count == total_count
    
    def _parse_statements(self, content: str) -> List[str]:
        """Parse SQL statements from schema content"""
        statements = []
        current_statement = ""
        in_statement = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('--'):
                continue
            
            # If line ends with semicolon, it's a complete statement
            if line.endswith(';'):
                current_statement += line
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
                in_statement = False
            else:
                # Continue building the statement
                if current_statement:
                    current_statement += " " + line
                else:
                    current_statement = line
                in_statement = True
        
        return statements
    
    def list_spaces(self) -> bool:
        """List all spaces in the database"""
        try:
            result = self.session.execute("SHOW SPACES")
            if result.is_succeeded():
                print("Available spaces:")
                for row in result:
                    print(f"  - {row[0]}")
                return True
            else:
                print(f"Failed to list spaces: {result.error_msg()}")
                return False
        except Exception as e:
            print(f"Error listing spaces: {e}")
            return False
    
    def check_space_exists(self, space_name: str) -> bool:
        """Check if a space exists"""
        try:
            result = self.session.execute("SHOW SPACES")
            if result.is_succeeded():
                for row in result:
                    if row[0] == space_name:
                        return True
                return False
            else:
                print(f"Failed to check space existence: {result.error_msg()}")
                return False
        except Exception as e:
            print(f"Error checking space existence: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Commit Nebula Graph schema to database')
    parser.add_argument('schema_file', help='Path to schema file (.ngql)')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--environment', help='Environment name (development, staging, production)')
    parser.add_argument('--host', help='Nebula Graph host (overrides config)')
    parser.add_argument('--port', type=int, help='Nebula Graph port (overrides config)')
    parser.add_argument('--username', help='Nebula Graph username (overrides config)')
    parser.add_argument('--password', help='Nebula Graph password (overrides config)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be executed without actually executing')
    parser.add_argument('--list-spaces', action='store_true', help='List all spaces and exit')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode (no actual database connection)')
    
    args = parser.parse_args()
    
    # Initialize committer
    committer = NebulaSchemaCommitter(
        config_file=args.config,
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        environment=args.environment,
        mock_mode=args.mock
    )
    
    # Connect to database
    if not committer.connect():
        print("Failed to connect to Nebula Graph")
        sys.exit(1)
    
    try:
        # List spaces if requested
        if args.list_spaces:
            committer.list_spaces()
            return
        
        # Execute schema file
        schema_file = Path(args.schema_file)
        success = committer.execute_schema_file(schema_file, dry_run=args.dry_run)
        
        if success:
            print("Schema commit completed successfully!")
            sys.exit(0)
        else:
            print("Schema commit failed!")
            sys.exit(1)
            
    finally:
        committer.disconnect()


if __name__ == "__main__":
    main()
