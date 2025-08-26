#!/usr/bin/env python3
"""
POI Ingestor for Nebula Graph

Reads POI data from generated files and loads it into Nebula Graph database.
Includes ontology-based schema generation for Nebula Graph.
"""

import json
import csv
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from generic_schema_generator import GenericNebulaSchemaGenerator


class POIIngestor:
    """Ingests POI data into Nebula Graph"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the POI ingestor"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.connection_pool = None
        self.session = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file or use defaults"""
        config = {
            'nebula': {
                'host': 'localhost',
                'port': 9669,
                'username': 'root',
                'password': 'nebula',
                'space': 'poi_space'
            },
            'batch_size': 100,
            'max_retries': 3,
            'retry_delay': 1.0
        }
        
        # Load from file if provided and exists
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                # Merge file config with defaults
                if file_config:
                    config.update(file_config)
        
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_to_nebula(self):
        """Connect to Nebula Graph"""
        try:
            nebula_config = self.config['nebula']
            
            # Create connection pool
            config = Config()
            self.connection_pool = ConnectionPool()
            
            # Initialize connection pool
            init_result = self.connection_pool.init(
                [(nebula_config['host'], nebula_config['port'])],
                config
            )
            
            if not init_result:
                raise Exception("Failed to initialize connection pool")
            
            # Get session
            self.session = self.connection_pool.get_session(
                nebula_config['username'], 
                nebula_config['password']
            )
            
            if not self.session:
                raise Exception("Failed to authenticate")
            
            # Try to use space, but don't fail if it doesn't exist yet
            use_result = self.session.execute(f"USE {nebula_config['space']}")
            if not use_result.is_succeeded():
                self.logger.info(f"Space {nebula_config['space']} doesn't exist yet, will be created during schema setup")
            else:
                self.logger.info(f"Connected to existing Nebula Graph space: {nebula_config['space']}")
            
            self.logger.info("Connected to Nebula Graph")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Nebula Graph: {e}")
            raise
    
    def disconnect_from_nebula(self):
        """Disconnect from Nebula Graph"""
        if hasattr(self, 'session') and self.session:
            self.session.release()
        if hasattr(self, 'connection_pool') and self.connection_pool:
            self.connection_pool.close()
        self.logger.info("Disconnected from Nebula Graph")
    
    def setup_schema(self, ontology_path: Optional[str] = None):
        """Setup Nebula Graph schema from ontology"""
        if ontology_path is None:
            # Get ontology path from config or use default
            ontology_config = self.config.get('ontology', {})
            if ontology_config.get('path'):
                # Resolve relative path from current working directory
                ontology_path = Path.cwd() / ontology_config['path']
            else:
                # Default ontology path relative to project root
                ontology_path = Path.cwd() / "ontology" / "poi" / "poi_ontology.yaml"
        
        # Resolve to absolute path
        ontology_path = ontology_path.resolve()
        
        try:
            self.logger.info(f"Setting up schema from ontology: {ontology_path}")
            
            # Generate schema from ontology using the generic schema generator
            # Use the ontology base path (parent directory) for the generic generator
            ontology_base_path = str(ontology_path.parent.parent)  # Go up to ontology root
            space_name = self.config['nebula']['space']
            
            schema_generator = GenericNebulaSchemaGenerator(
                ontology_base_path=ontology_base_path,
                space_name=space_name
            )
            
            # Generate the complete schema
            schema_content = schema_generator.generate_schema()
            
            # Split into individual statements and execute
            statements = [stmt.strip() for stmt in schema_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:  # Skip empty statements
                    self.logger.info(f"Executing schema statement: {statement[:50]}...")
                    result = self.session.execute(statement)
                    
                    if not result.is_succeeded():
                        self.logger.warning(f"Schema statement failed: {result.error_msg()}")
                        # Continue with other statements even if some fail
                    else:
                        self.logger.info("Schema statement executed successfully")
            
            self.logger.info("Schema setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup schema: {e}")
            raise
    
    def load_poi_data(self, data_dir: str) -> List[Dict[str, Any]]:
        """Load POI data from generated files"""
        data_path = Path(data_dir)
        poi_data = []
        
        # Look for JSON files containing POI data
        json_files = list(data_path.glob("*.json"))
        
        for json_file in json_files:
            self.logger.info(f"Loading data from: {json_file}")
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    poi_data.extend(data)
                else:
                    poi_data.append(data)
                    
            except Exception as e:
                self.logger.error(f"Failed to load {json_file}: {e}")
                continue
        
        self.logger.info(f"Loaded {len(poi_data)} POI records")
        return poi_data
    
    def validate_poi_data(self, poi_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean POI data"""
        valid_data = []
        
        for poi in poi_data:
            # Check required fields
            required_fields = ['poi_id', 'name', 'category', 'lat', 'lon']
            if not all(field in poi and poi[field] is not None for field in required_fields):
                self.logger.warning(f"Skipping POI with missing required fields: {poi.get('poi_id', 'unknown')}")
                continue
            
            # Validate coordinates
            try:
                lat = float(poi['lat'])
                lon = float(poi['lon'])
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    self.logger.warning(f"Skipping POI with invalid coordinates: {poi['poi_id']}")
                    continue
                    
            except (ValueError, TypeError):
                self.logger.warning(f"Skipping POI with invalid coordinate format: {poi['poi_id']}")
                continue
            
            # Convert lat/lon to WKT POINT format for GEOGRAPHY type
            location_wkt = f"POINT({lon} {lat})"
            
            # Clean and normalize data
            cleaned_poi = {
                'poi_id': str(poi['poi_id']),
                'name': str(poi['name']).strip(),
                'category': str(poi['category']).strip(),
                'location': location_wkt,  # WKT format for GEOGRAPHY type
                'address': str(poi.get('address', '')).strip() if poi.get('address') else None,
                'description': str(poi.get('description', '')).strip() if poi.get('description') else None,
                'rating': float(poi['rating']) if poi.get('rating') is not None else None,
                'opening_hours': str(poi.get('opening_hours', '')).strip() if poi.get('opening_hours') else None,
                'capacity': int(poi['capacity']) if poi.get('capacity') is not None else None
            }
            
            valid_data.append(cleaned_poi)
        
        self.logger.info(f"Validated {len(valid_data)} POI records")
        return valid_data
    
    def create_poi_vertex(self, poi: Dict[str, Any]) -> str:
        """Create a POI vertex in Nebula Graph"""
        # Build property values in schema order for new schema
        schema_props = ['poi_id', 'name', 'category', 'location', 'address', 'description', 'rating', 'opening_hours', 'capacity']
        values = []
        for key in schema_props:
            if key in poi and poi[key] is not None:
                value = poi[key]
                if key == 'location':
                    # Handle GEOGRAPHY type with ST_GeogFromText function
                    values.append(f"ST_GeogFromText('{value}')")
                elif isinstance(value, str):
                    # Escape single quotes in strings
                    escaped_value = value.replace("'", "\\'")
                    values.append(f"'{escaped_value}'")
                else:
                    values.append(str(value))
            else:
                # Use appropriate default values based on type
                if key == 'capacity':
                    values.append("0")  # Integer default
                elif key == 'rating':
                    values.append("0.0")  # Double default
                elif key == 'location':
                    values.append("ST_GeogFromText('POINT(0 0)')")  # Default GEOGRAPHY
                else:
                    values.append("''")  # String default
        
        values_str = ", ".join(values)
        vertex_id = poi['poi_id']  # Use the original ID directly
        
        # Create vertex - use positional format
        query = f"INSERT VERTEX POI VALUES '{vertex_id}':({values_str});"
        
        # Debug output
        self.logger.info(f"Executing query: {query}")
        
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise Exception(f"Failed to create POI vertex: {result.error_msg()}")
        
        return vertex_id
    
    def create_poi_type_vertex(self, poi_type: Dict[str, Any]) -> str:
        """Create a POI_TYPE vertex in Nebula Graph"""
        # Build property values in schema order
        schema_props = ['type_id', 'name', 'description', 'category']
        values = []
        for key in schema_props:
            if key in poi_type and poi_type[key] is not None:
                value = poi_type[key]
                if isinstance(value, str):
                    # Escape single quotes in strings
                    escaped_value = value.replace("'", "\\'")
                    values.append(f"'{escaped_value}'")
                else:
                    values.append(str(value))
            else:
                # Use empty string for missing values
                values.append("''")
        
        values_str = ", ".join(values)
        vertex_id = poi_type['type_id']  # Use the original ID directly
        
        # Create vertex - use positional format
        query = f"INSERT VERTEX POI_TYPE VALUES '{vertex_id}':({values_str});"
        
        result = self.session.execute(query)
        if not result.is_succeeded():
            raise Exception(f"Failed to create POI_TYPE vertex: {result.error_msg()}")
        
        return vertex_id
    
    def create_is_of_type_relationship(self, poi_id: str, poi_type_id: str, confidence: float = 1.0):
        """Create IS_OF_TYPE relationship between POI and POI_TYPE"""
        try:
            query = f"INSERT EDGE IS_OF_TYPE VALUES '{poi_id}' -> '{poi_type_id}':({confidence});"
            
            result = self.session.execute(query)
            if not result.is_succeeded():
                self.logger.warning(f"Failed to create IS_OF_TYPE relationship: {result.error_msg()}")
                return False
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to create IS_OF_TYPE relationship: {e}")
            return False
    
    def extract_poi_types(self, pois: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract unique POI types from POI data"""
        poi_types = {}
        
        for poi in pois:
            # Use landmark_type if available, otherwise use category
            type_name = poi.get('landmark_type') or poi.get('category', 'unknown')
            type_id = f"type_{type_name.lower().replace(' ', '_')}"
            
            if type_id not in poi_types:
                poi_types[type_id] = {
                    'type_id': type_id,
                    'name': type_name,
                    'description': f"Type for {type_name}",
                    'category': poi.get('category', 'unknown')
                }
        
        return poi_types
    
    def ingest_pois(self, data_dir: str, create_relationships: bool = True, setup_schema: bool = True):
        """Ingest POI data into Nebula Graph"""
        try:
            # Connect to Nebula Graph
            self.connect_to_nebula()
            
            # Setup schema from ontology if requested
            if setup_schema:
                ontology_config = self.config.get('ontology', {})
                auto_setup = ontology_config.get('auto_setup_schema', True)
                if auto_setup:
                    self.setup_schema()
            
            # Load and validate data
            raw_data = self.load_poi_data(data_dir)
            valid_data = self.validate_poi_data(raw_data)
            
            if not valid_data:
                self.logger.warning("No valid POI data found")
                return
            
            # Extract and create POI types
            poi_types = self.extract_poi_types(valid_data)
            created_types = 0
            
            for poi_type in poi_types.values():
                try:
                    self.create_poi_type_vertex(poi_type)
                    created_types += 1
                except Exception as e:
                    self.logger.error(f"Failed to create POI_TYPE vertex {poi_type['type_id']}: {e}")
                    continue
            
            self.logger.info(f"Successfully created {created_types} POI_TYPE vertices")
            
            # Create POI vertices
            batch_size = self.config.get('batch_size', 100)
            created_vertices = 0
            created_relationships = 0
            
            for i in range(0, len(valid_data), batch_size):
                batch = valid_data[i:i + batch_size]
                
                for poi in batch:
                    try:
                        vertex_id = self.create_poi_vertex(poi)
                        created_vertices += 1
                        
                        # Create IS_OF_TYPE relationship
                        if create_relationships:
                            type_name = poi.get('landmark_type') or poi.get('category', 'unknown')
                            type_id = f"type_{type_name.lower().replace(' ', '_')}"
                            
                            if self.create_is_of_type_relationship(poi['poi_id'], type_id):
                                created_relationships += 1
                        
                        if created_vertices % 100 == 0:
                            self.logger.info(f"Created {created_vertices} POI vertices")
                            
                    except Exception as e:
                        self.logger.error(f"Failed to create POI vertex {poi['poi_id']}: {e}")
                        continue
            
            self.logger.info(f"Successfully created {created_vertices} POI vertices")
            if create_relationships:
                self.logger.info(f"Successfully created {created_relationships} IS_OF_TYPE relationships")
            
        except Exception as e:
            self.logger.error(f"Failed to ingest POI data: {e}")
            raise
        finally:
            self.disconnect_from_nebula()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Ingest POI data into Nebula Graph')
    parser.add_argument('--space-name', required=True,
                       help='Nebula Graph space name')
    parser.add_argument('--data-dir', required=True, 
                       help='Directory containing generated POI data')
    parser.add_argument('--config', default='config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--host', default='localhost',
                       help='Nebula Graph host')
    parser.add_argument('--port', type=int, default=9669,
                       help='Nebula Graph port')
    parser.add_argument('--username', default='root',
                       help='Nebula Graph username')
    parser.add_argument('--password', default='nebula',
                       help='Nebula Graph password')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for data ingestion')
    parser.add_argument('--no-relationships', action='store_true',
                       help='Skip creating IS_OF_TYPE relationships')
    parser.add_argument('--no-schema-setup', action='store_true',
                       help='Skip schema setup from ontology')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate data without ingesting')
    
    args = parser.parse_args()
    
    # Initialize ingestor
    ingestor = POIIngestor(args.config)
    
    # Update config with command line arguments (overriding file config)
    ingestor.config['nebula'].update({
        'host': args.host,
        'port': args.port,
        'username': args.username,
        'password': args.password,
        'space': args.space_name
    })
    ingestor.config['batch_size'] = args.batch_size
    
    if args.dry_run:
        # Just validate data without connecting to Nebula
        raw_data = ingestor.load_poi_data(args.data_dir)
        valid_data = ingestor.validate_poi_data(raw_data)
        print(f"Dry run completed: {len(valid_data)} valid POI records found")
        return
    
    # Ingest data
    ingestor.ingest_pois(
        args.data_dir, 
        create_relationships=not args.no_relationships,
        setup_schema=not args.no_schema_setup
    )
    
    print("POI ingestion completed successfully!")


if __name__ == "__main__":
    main()
