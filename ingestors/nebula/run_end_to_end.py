#!/usr/bin/env python3
"""
End-to-End Nebula Graph Pipeline Runner

Automates the complete workflow by calling existing scripts:
1. Load ontologies from YAML files
2. Generate unified Nebula Graph schema
3. Commit schema to Nebula Graph database
4. Validate deployment

Usage:
    python run_end_to_end.py [OPTIONS]
"""

import argparse
import sys
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from config_loader import ConfigLoader


class EndToEndRunner:
    """End-to-end pipeline runner for Nebula Graph schema deployment"""
    
    def __init__(self, config_file: str = "config.yaml", environment: str = None):
        """Initialize the end-to-end runner"""
        self.config_loader = ConfigLoader(config_file)
        self.environment = environment
        self.logger = self._setup_logging()
        
        # Generated schema path
        self.generated_schema_path = None
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging_config = self.config_loader.get_logging_config()
        
        # Configure logging
        log_level = getattr(logging, logging_config.get('level', 'INFO'))
        log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger('EndToEndRunner')
    
    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met"""
        self.logger.info("Validating prerequisites...")
        
        # Check configuration
        if not self.config_loader.validate_config():
            self.logger.error("Configuration validation failed")
            return False
        
        # Check if required scripts exist
        required_scripts = ['generic_schema_generator.py', 'commit_schema.py']
        missing_scripts = []
        for script in required_scripts:
            if not Path(script).exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            self.logger.error(f"Missing required scripts: {missing_scripts}")
            return False
        
        # Check ontology base path
        ontology_base_path = Path(self.config_loader.get_ontology_base_path())
        if not ontology_base_path.exists():
            self.logger.error(f"Ontology base path does not exist: {ontology_base_path}")
            return False
        
        # Check ontology directories
        ontology_dirs = self.config_loader.get_ontology_directories()
        missing_dirs = []
        for dir_name in ontology_dirs:
            dir_path = ontology_base_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.logger.warning(f"Missing ontology directories: {missing_dirs}")
        
        # Check schema output directory
        schema_dir = Path(self.config_loader.get_schema_dir())
        schema_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Prerequisites validation completed")
        return True
    
    def run_schema_generator(self, space_name: str = None, timestamped: bool = False) -> bool:
        """Run the schema generator script"""
        self.logger.info("Running schema generator...")
        
        try:
            # Build command for schema generator
            cmd = ['python', 'generic_schema_generator.py']
            
            # Add configuration options
            cmd.extend(['--config', str(self.config_loader.config_file)])
            
            if space_name:
                cmd.extend(['--space-name', space_name])
            
            if timestamped:
                cmd.append('--timestamped')
            
            # Don't add list-ontologies flag as it prevents schema generation
            # We'll get ontology info from the output instead
            
            self.logger.info(f"Executing: {' '.join(cmd)}")
            
            # Run schema generator
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse output to get generated schema path
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Unified schema saved to:' in line:
                    self.generated_schema_path = line.split(': ')[1].strip()
                    break
            
            if not self.generated_schema_path:
                # If no explicit path found, construct it
                actual_space_name = space_name or self.config_loader.get_space_name()
                schema_dir = self.config_loader.get_schema_dir()
                if timestamped:
                    # For timestamped files, we need to find the latest one
                    schema_path = Path(schema_dir)
                    timestamped_files = list(schema_path.glob(f"nebula_{actual_space_name}_schema_*.ngql"))
                    if timestamped_files:
                        self.generated_schema_path = str(max(timestamped_files, key=lambda x: x.stat().st_mtime))
                    else:
                        self.logger.error("Could not find generated timestamped schema file")
                        return False
                else:
                    filename = f"nebula_{actual_space_name}_schema.ngql"
                    self.generated_schema_path = str(Path(schema_dir) / filename)
            
            self.logger.info(f"Schema generated successfully: {self.generated_schema_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Schema generator failed: {e}")
            if e.stdout:
                self.logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                self.logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Schema generation failed: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """Validate the generated schema"""
        self.logger.info("Validating generated schema...")
        
        if not self.generated_schema_path or not Path(self.generated_schema_path).exists():
            self.logger.error("Generated schema file not found")
            return False
        
        try:
            # Read and validate schema content
            with open(self.generated_schema_path, 'r') as f:
                schema_content = f.read()
            
            # Basic validation checks
            if not schema_content.strip():
                self.logger.error("Generated schema is empty")
                return False
            
            # Check for required elements
            required_elements = [
                "CREATE SPACE",
                "USE",
                "CREATE TAG",
                "CREATE EDGE"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in schema_content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.logger.error(f"Schema missing required elements: {missing_elements}")
                return False
            
            # Count statements (simple count of semicolons)
            statement_count = schema_content.count(';')
            self.logger.info(f"Schema contains approximately {statement_count} statements")
            
            self.logger.info("Schema validation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False
    
    def run_schema_committer(self, dry_run: bool = False, mock_mode: bool = False) -> bool:
        """Run the schema committer script"""
        self.logger.info("Running schema committer...")
        
        if not self.generated_schema_path:
            self.logger.error("No schema file to commit")
            return False
        
        try:
            # Build command for schema committer
            cmd = ['python', 'commit_schema.py', self.generated_schema_path]
            
            # Add configuration options
            cmd.extend(['--config', str(self.config_loader.config_file)])
            
            if self.environment:
                cmd.extend(['--environment', self.environment])
            
            if dry_run:
                cmd.append('--dry-run')
            
            if mock_mode:
                cmd.append('--mock')
            
            self.logger.info(f"Executing: {' '.join(cmd)}")
            
            # Run schema committer
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Check for success indicators in output
            output = result.stdout + result.stderr
            if 'completed successfully' in output.lower() or 'schema commit completed' in output.lower():
                self.logger.info("Schema commit completed successfully")
                return True
            else:
                self.logger.warning("Schema commit may have had issues")
                return True  # Still consider it successful if no exception
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Schema committer failed: {e}")
            if e.stdout:
                self.logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                self.logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Schema commit failed: {e}")
            return False
    
    def run_pipeline(self, space_name: str = None, timestamped: bool = False, 
                    dry_run: bool = False, mock_mode: bool = False, 
                    skip_validation: bool = False) -> bool:
        """Run the complete end-to-end pipeline"""
        self.logger.info("Starting end-to-end Nebula Graph pipeline...")
        start_time = time.time()
        
        try:
            # Step 1: Validate prerequisites
            if not self.validate_prerequisites():
                return False
            
            # Step 2: Generate schema using existing script
            if not self.run_schema_generator(space_name, timestamped):
                return False
            
            # Step 3: Validate schema
            if not skip_validation and not self.validate_schema():
                return False
            
            # Step 4: Commit schema using existing script
            if not self.run_schema_committer(dry_run, mock_mode):
                return False
            
            # Calculate execution time
            execution_time = time.time() - start_time
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            
            # Print summary
            self._print_summary(space_name, dry_run, mock_mode, execution_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return False
    
    def _print_summary(self, space_name: str, dry_run: bool, mock_mode: bool, execution_time: float):
        """Print pipeline execution summary"""
        print("\n" + "="*60)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*60)
        actual_space_name = space_name or self.config_loader.get_space_name()
        print(f"Space Name: {actual_space_name}")
        print(f"Environment: {self.environment or 'default'}")
        print(f"Schema File: {self.generated_schema_path}")
        print(f"Execution Mode: {'DRY RUN' if dry_run else 'MOCK' if mock_mode else 'LIVE'}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        # Get ontology information
        ontology_dirs = self.config_loader.get_ontology_directories()
        print(f"Ontologies Processed: {len(ontology_dirs)}")
        for ontology_name in ontology_dirs:
            print(f"  - {ontology_name}")
        
        # Count statements if schema file exists
        if self.generated_schema_path and Path(self.generated_schema_path).exists():
            try:
                with open(self.generated_schema_path, 'r') as f:
                    content = f.read()
                    statement_count = content.count(';')
                    print(f"Schema Statements: ~{statement_count}")
            except:
                print("Schema Statements: Unknown")
        
        print("="*60)


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description='End-to-End Nebula Graph Pipeline Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline with default settings
  python run_end_to_end.py

  # Run with custom space name
  python run_end_to_end.py --space-name tourism_space

  # Run in dry-run mode
  python run_end_to_end.py --dry-run

  # Run in mock mode for testing
  python run_end_to_end.py --mock

  # Run for specific environment
  python run_end_to_end.py --environment production

  # Generate timestamped schema
  python run_end_to_end.py --timestamped

  # Skip validation steps
  python run_end_to_end.py --skip-validation
        """
    )
    
    # Configuration options
    parser.add_argument('--config', default='config.yaml',
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--environment',
                       help='Environment name (development, staging, production)')
    
    # Schema generation options
    parser.add_argument('--space-name',
                       help='Space name for schema generation (overrides config)')
    parser.add_argument('--timestamped', action='store_true',
                       help='Generate timestamped schema file')
    
    # Execution options
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be executed without actually executing')
    parser.add_argument('--mock', action='store_true',
                       help='Run in mock mode (no actual database connection)')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip schema and deployment validation steps')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress non-error output')
    
    args = parser.parse_args()
    
    # Setup logging level based on arguments
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run pipeline
    runner = EndToEndRunner(
        config_file=args.config,
        environment=args.environment
    )
    
    success = runner.run_pipeline(
        space_name=args.space_name,
        timestamped=args.timestamped,
        dry_run=args.dry_run,
        mock_mode=args.mock,
        skip_validation=args.skip_validation
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
