#!/usr/bin/env python3
"""
Configuration Loader for Nebula Graph Tools

Loads and manages configuration parameters for Nebula Graph connection,
schema generation, and deployment.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Loads and manages configuration from YAML files"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """Initialize with configuration file path"""
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            print(f"Warning: Configuration file {self.config_file} not found. Using defaults.")
            return self._get_default_config()
            
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                return config or {}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'nebula': {
                'connection': {
                    'host': 'localhost',
                    'port': 9669,
                    'username': 'root',
                    'password': 'nebula'
                }
            },
            'schema': {
                'default_space_name': 'unified_space',
                'output': {
                    'schema_dir': 'schema'
                }
            },
            'deployment': {
                'default': {
                    'dry_run': False,
                    'mock_mode': False
                }
            }
        }
    
    def get_nebula_connection(self, environment: str = None) -> Dict[str, Any]:
        """Get Nebula Graph connection parameters"""
        if environment and environment in self.config.get('deployment', {}).get('environments', {}):
            # Use environment-specific settings
            env_config = self.config['deployment']['environments'][environment]
            connection = {
                'host': env_config.get('host', 'localhost'),
                'port': env_config.get('port', 9669),
                'username': env_config.get('username', 'root'),
                'password': env_config.get('password', 'nebula')
            }
        else:
            # Use default connection settings
            connection = self.config.get('nebula', {}).get('connection', {})
        
        # Override with environment variables if they exist
        env_vars = self.config.get('security', {}).get('env_vars', {})
        
        if env_vars.get('host') and os.getenv(env_vars['host']):
            connection['host'] = os.getenv(env_vars['host'])
        
        if env_vars.get('port') and os.getenv(env_vars['port']):
            connection['port'] = int(os.getenv(env_vars['port']))
        
        if env_vars.get('username') and os.getenv(env_vars['username']):
            connection['username'] = os.getenv(env_vars['username'])
        
        if env_vars.get('password') and os.getenv(env_vars['password']):
            connection['password'] = os.getenv(env_vars['password'])
        
        return connection
    
    def get_schema_config(self) -> Dict[str, Any]:
        """Get schema generation configuration"""
        return self.config.get('schema', {})
    
    def get_deployment_config(self, environment: str = None) -> Dict[str, Any]:
        """Get deployment configuration"""
        deployment_config = self.config.get('deployment', {}).get('default', {})
        
        if environment and environment in self.config.get('deployment', {}).get('environments', {}):
            env_config = self.config['deployment']['environments'][environment]
            # Merge environment-specific settings with defaults
            deployment_config.update(env_config)
        
        return deployment_config
    
    def get_ontology_config(self) -> Dict[str, Any]:
        """Get ontology configuration"""
        return self.config.get('ontology', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})
    
    def get_space_name(self, custom_space_name: str = None) -> str:
        """Get space name for schema generation"""
        if custom_space_name:
            return custom_space_name
        
        schema_config = self.get_schema_config()
        return schema_config.get('default_space_name', 'unified_space')
    
    def get_schema_dir(self) -> str:
        """Get schema output directory"""
        schema_config = self.get_schema_config()
        return schema_config.get('output', {}).get('schema_dir', 'schema')
    
    def get_ontology_base_path(self) -> str:
        """Get ontology base path"""
        ontology_config = self.get_ontology_config()
        return ontology_config.get('base_path', '../../ontology')
    
    def get_ontology_directories(self) -> list:
        """Get list of ontology directories to process"""
        ontology_config = self.get_ontology_config()
        return ontology_config.get('directories', ['poi', 'people', 'people_locations'])
    
    def get_ontology_file_pattern(self) -> str:
        """Get ontology file pattern"""
        ontology_config = self.get_ontology_config()
        return ontology_config.get('file_pattern', '*_ontology.yaml')
    
    def is_dry_run(self, environment: str = None) -> bool:
        """Check if dry-run mode is enabled"""
        deployment_config = self.get_deployment_config(environment)
        return deployment_config.get('dry_run', False)
    
    def is_mock_mode(self, environment: str = None) -> bool:
        """Check if mock mode is enabled"""
        deployment_config = self.get_deployment_config(environment)
        return deployment_config.get('mock_mode', False)
    
    def get_ssl_config(self, environment: str = None) -> Dict[str, Any]:
        """Get SSL configuration"""
        if environment and environment in self.config.get('deployment', {}).get('environments', {}):
            env_config = self.config['deployment']['environments'][environment]
            return env_config.get('ssl', {})
        
        nebula_config = self.config.get('nebula', {})
        return nebula_config.get('connection', {}).get('ssl', {})
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            # Check required sections
            required_sections = ['nebula', 'schema', 'deployment']
            for section in required_sections:
                if section not in self.config:
                    print(f"Warning: Missing configuration section: {section}")
            
            # Check connection parameters
            connection = self.get_nebula_connection()
            required_connection_params = ['host', 'port', 'username', 'password']
            for param in required_connection_params:
                if param not in connection:
                    print(f"Warning: Missing connection parameter: {param}")
            
            return True
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False
    
    def print_config(self, environment: str = None):
        """Print current configuration"""
        print("Current Configuration:")
        print(f"  Config file: {self.config_file}")
        print(f"  Environment: {environment or 'default'}")
        print()
        
        print("Nebula Connection:")
        connection = self.get_nebula_connection(environment)
        for key, value in connection.items():
            if key == 'password':
                print(f"  {key}: {'*' * len(str(value))}")
            else:
                print(f"  {key}: {value}")
        print()
        
        print("Schema Generation:")
        schema_config = self.get_schema_config()
        print(f"  Default space name: {schema_config.get('default_space_name', 'unified_space')}")
        print(f"  Schema directory: {schema_config.get('output', {}).get('schema_dir', 'schema')}")
        print()
        
        print("Deployment:")
        deployment_config = self.get_deployment_config(environment)
        print(f"  Dry run: {deployment_config.get('dry_run', False)}")
        print(f"  Mock mode: {deployment_config.get('mock_mode', False)}")
        print(f"  Verbose: {deployment_config.get('verbose', True)}")


def main():
    """Test configuration loader"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuration loader test')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--environment', help='Environment name')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    
    args = parser.parse_args()
    
    # Load configuration
    config_loader = ConfigLoader(args.config)
    
    if args.validate:
        if config_loader.validate_config():
            print("Configuration is valid!")
        else:
            print("Configuration validation failed!")
    else:
        config_loader.print_config(args.environment)


if __name__ == "__main__":
    main()
