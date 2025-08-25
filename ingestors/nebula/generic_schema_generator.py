#!/usr/bin/env python3
"""
Generic Nebula Graph Schema Generator

Converts all ontologies (POI, People, People Locations) to a unified Nebula Graph schema.
This script generates a single space containing all entities and relationships from all ontologies.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from config_loader import ConfigLoader


class GenericNebulaSchemaGenerator:
    """Generates unified Nebula Graph schema from all ontology definitions"""
    
    def __init__(self, config_file: str = "config.yaml", ontology_base_path: str = None, space_name: str = None):
        """Initialize with configuration file and optional overrides"""
        self.config_loader = ConfigLoader(config_file)
        
        # Use config values or provided overrides
        self.ontology_base_path = Path(ontology_base_path or self.config_loader.get_ontology_base_path())
        self.space_name = space_name or self.config_loader.get_space_name()
        
        self.ontologies = {}
        self._load_all_ontologies()
        
    def _load_all_ontologies(self):
        """Load all ontology files from the base directory"""
        ontology_dirs = self.config_loader.get_ontology_directories()
        file_pattern = self.config_loader.get_ontology_file_pattern()
        
        for dir_name in ontology_dirs:
            ontology_dir = self.ontology_base_path / dir_name
            if ontology_dir.exists():
                # Find the ontology YAML file
                for yaml_file in ontology_dir.glob(file_pattern):
                    try:
                        with open(yaml_file, 'r') as f:
                            data = yaml.safe_load(f)
                            ontology_data = data.get('ontology', data)
                            self.ontologies[dir_name] = {
                                'path': yaml_file,
                                'data': ontology_data
                            }
                            print(f"Loaded ontology: {dir_name} from {yaml_file}")
                    except Exception as e:
                        print(f"Error loading ontology {dir_name}: {e}")
    
    def _get_nebula_type(self, ontology_type: str) -> str:
        """Convert ontology type to Nebula Graph type"""
        type_mapping = {
            'string': 'string',
            'int': 'int',
            'double': 'double',
            'float': 'double',
            'bool': 'bool',
            'timestamp': 'timestamp'
        }
        return type_mapping.get(ontology_type, 'string')
    
    def _generate_tag_schema(self, entity: Dict[str, Any]) -> str:
        """Generate Nebula Graph tag schema for an entity"""
        entity_name = entity['name']
        properties = entity.get('properties', [])
        
        # Start tag definition
        schema_lines = [f"CREATE TAG {entity_name} ("]
        
        # Add properties with commas
        prop_lines = []
        for i, prop in enumerate(properties):
            prop_name = prop['name']
            prop_type = self._get_nebula_type(prop['type'])
            nullable = "" if prop.get('required', False) else " NULL"
            comma = "," if i < len(properties) - 1 else ""
            prop_lines.append(f"    {prop_name} {prop_type}{nullable}{comma}")
        
        schema_lines.extend(prop_lines)
        schema_lines.append(");")
        
        return "\n".join(schema_lines)
    
    def _generate_edge_schema(self, relationship: Dict[str, Any]) -> str:
        """Generate Nebula Graph edge schema for a relationship"""
        edge_name = relationship['name']
        properties = relationship.get('properties', [])
        
        # Start edge definition
        schema_lines = [f"CREATE EDGE {edge_name} ("]
        
        # Add properties with commas
        prop_lines = []
        for i, prop in enumerate(properties):
            prop_name = prop['name']
            prop_type = self._get_nebula_type(prop['type'])
            nullable = "" if prop.get('required', False) else " NULL"
            comma = "," if i < len(properties) - 1 else ""
            prop_lines.append(f"    {prop_name} {prop_type}{nullable}{comma}")
        
        schema_lines.extend(prop_lines)
        schema_lines.append(");")
        
        return "\n".join(schema_lines)
    
    def _generate_indexes(self) -> List[str]:
        """Generate index creation statements from all ontologies"""
        index_statements = []
        
        for ontology_name, ontology_info in self.ontologies.items():
            ontology_data = ontology_info['data']
            indexes = ontology_data.get('indexes', [])
            
            for index in indexes:
                index_name = f"{ontology_name}_{index['name']}"  # Prefix with ontology name
                entity = index['entity']
                properties = index['properties']
                
                props_str = ", ".join(properties)
                stmt = f"CREATE TAG INDEX {index_name} ON {entity}({props_str});"
                index_statements.append(stmt)
        
        return index_statements
    
    def generate_schema(self) -> str:
        """Generate complete unified Nebula Graph schema"""
        schema_parts = []
        
        # Add header
        schema_parts.append("-- Unified Nebula Graph Schema for All Ontologies")
        schema_parts.append(f"-- Generated from: {self.ontology_base_path}")
        schema_parts.append(f"-- Generated at: {datetime.now().isoformat()}")
        schema_parts.append("")
        
        # List loaded ontologies
        schema_parts.append("-- Loaded Ontologies:")
        for ontology_name, ontology_info in self.ontologies.items():
            schema_parts.append(f"--   {ontology_name}: {ontology_info['path']}")
        schema_parts.append("")
        
        # Add space creation
        schema_parts.append("-- Create unified space for all data")
        
        # Get space configuration from config
        schema_config = self.config_loader.get_schema_config()
        generation_config = schema_config.get('generation', {})
        
        partition_num = generation_config.get('partition_num', 10)
        replica_factor = generation_config.get('replica_factor', 1)
        vid_type = generation_config.get('vid_type', 'FIXED_STRING(32)')
        
        schema_parts.append(f"CREATE SPACE {self.space_name} (partition_num = {partition_num}, replica_factor = {replica_factor}, vid_type = {vid_type});")
        schema_parts.append(f"USE {self.space_name};")
        schema_parts.append("")
        
        # Generate tag schemas from all ontologies
        schema_parts.append("-- Tag definitions (vertices) from all ontologies")
        for ontology_name, ontology_info in self.ontologies.items():
            ontology_data = ontology_info['data']
            schema_parts.append(f"-- {ontology_name.upper()} ONTOLOGY")
            
            for entity in ontology_data.get('entities', []):
                schema_parts.append(self._generate_tag_schema(entity))
                schema_parts.append("")
        
        # Generate edge schemas from all ontologies
        schema_parts.append("-- Edge definitions (relationships) from all ontologies")
        for ontology_name, ontology_info in self.ontologies.items():
            ontology_data = ontology_info['data']
            schema_parts.append(f"-- {ontology_name.upper()} ONTOLOGY")
            
            for relationship in ontology_data.get('relationships', []):
                schema_parts.append(self._generate_edge_schema(relationship))
                schema_parts.append("")
        
        # Generate indexes from all ontologies
        schema_parts.append("-- Indexes for performance (from all ontologies)")
        for index_stmt in self._generate_indexes():
            schema_parts.append(index_stmt)
        schema_parts.append("")
        
        return "\n".join(schema_parts)
    
    def save_schema(self, output_path: str):
        """Save generated schema to file"""
        schema = self.generate_schema()
        
        with open(output_path, 'w') as f:
            f.write(schema)
        
        print(f"Unified schema saved to: {output_path}")
    
    def save_timestamped_schema(self, schema_dir: str = None):
        """Save schema with timestamp for versioning"""
        if schema_dir is None:
            schema_dir = self.config_loader.get_schema_dir()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nebula_{self.space_name}_schema_{timestamp}.ngql"
        output_path = Path(schema_dir) / filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.save_schema(str(output_path))
        return str(output_path)
    
    def get_schema_statements(self) -> List[str]:
        """Get schema as list of individual statements for execution"""
        schema = self.generate_schema()
        statements = []
        
        # Process line by line to build statements
        current_statement = ""
        in_statement = False
        
        for line in schema.split('\n'):
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
    
    def list_loaded_ontologies(self):
        """List all loaded ontologies and their entities"""
        print("Loaded Ontologies:")
        for ontology_name, ontology_info in self.ontologies.items():
            print(f"\n{ontology_name.upper()}:")
            print(f"  Path: {ontology_info['path']}")
            
            ontology_data = ontology_info['data']
            entities = ontology_data.get('entities', [])
            relationships = ontology_data.get('relationships', [])
            
            print(f"  Entities ({len(entities)}):")
            for entity in entities:
                print(f"    - {entity['name']}")
            
            print(f"  Relationships ({len(relationships)}):")
            for rel in relationships:
                print(f"    - {rel['name']}: {rel.get('source', '?')} -> {rel.get('target', '?')}")


def main():
    """Main function to generate unified schema"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate unified Nebula Graph schema from all ontologies')
    parser.add_argument('--config', default='config.yaml',
                       help='Configuration file path')
    parser.add_argument('--ontology-base',
                       help='Base path to ontology directory (overrides config)')
    parser.add_argument('--space-name',
                       help='Space name (overrides config)')
    parser.add_argument('--output',
                       help='Output schema file path (auto-generated if not specified)')
    parser.add_argument('--timestamped', action='store_true',
                       help='Generate timestamped schema file')
    parser.add_argument('--schema-dir',
                       help='Schema directory for timestamped files (overrides config)')
    parser.add_argument('--list-ontologies', action='store_true',
                       help='List loaded ontologies and their entities')
    
    args = parser.parse_args()
    
    # Generate schema
    generator = GenericNebulaSchemaGenerator(
        config_file=args.config,
        ontology_base_path=args.ontology_base,
        space_name=args.space_name
    )
    
    if args.list_ontologies:
        generator.list_loaded_ontologies()
        return
    
    if args.timestamped:
        output_path = generator.save_timestamped_schema(args.schema_dir)
        print(f"Timestamped schema saved to: {output_path}")
    else:
        # Auto-generate output path if not specified
        if args.output is None:
            output_path = f"schema/nebula_{generator.space_name}_schema.ngql"
        else:
            output_path = args.output
        
        # Ensure output directory exists
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        generator.save_schema(output_path)
        print(f"Unified schema saved to: {output_path}")


if __name__ == "__main__":
    main()
