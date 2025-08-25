#!/usr/bin/env python3
"""
Nebula Graph Schema Generator for People Ontology

Converts the People ontology to Nebula Graph schema definitions.
This script is part of the Nebula ingestion process for people and roles.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class NebulaSchemaGenerator:
    """Generates Nebula Graph schema from ontology definition"""
    
    def __init__(self, ontology_path: str):
        """Initialize with ontology file path"""
        self.ontology_path = Path(ontology_path)
        self.ontology = self._load_ontology()
        
    def _load_ontology(self) -> Dict[str, Any]:
        """Load ontology from YAML file"""
        with open(self.ontology_path, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('ontology', data)
    
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
        """Generate index creation statements"""
        indexes = self.ontology.get('indexes', [])
        index_statements = []
        
        for index in indexes:
            index_name = index['name']
            entity = index['entity']
            properties = index['properties']
            
            props_str = ", ".join(properties)
            stmt = f"CREATE TAG INDEX {index_name} ON {entity}({props_str});"
            index_statements.append(stmt)
        
        return index_statements
    
    def generate_schema(self) -> str:
        """Generate complete Nebula Graph schema"""
        schema_parts = []
        
        # Add header
        schema_parts.append("-- Nebula Graph Schema for People Ontology")
        schema_parts.append(f"-- Generated from: {self.ontology_path}")
        schema_parts.append(f"-- Generated at: {datetime.now().isoformat()}")
        schema_parts.append("")
        
        # Add space creation
        schema_parts.append("-- Create space for People data")
        schema_parts.append("CREATE SPACE people_space (partition_num = 10, replica_factor = 1, vid_type = FIXED_STRING(32));")
        schema_parts.append("USE people_space;")
        schema_parts.append("")
        
        # Generate tag schemas
        schema_parts.append("-- Tag definitions (vertices)")
        for entity in self.ontology['entities']:
            schema_parts.append(self._generate_tag_schema(entity))
            schema_parts.append("")
        
        # Generate edge schemas
        schema_parts.append("-- Edge definitions (relationships)")
        for relationship in self.ontology['relationships']:
            schema_parts.append(self._generate_edge_schema(relationship))
            schema_parts.append("")
        
        # Generate indexes
        schema_parts.append("-- Indexes for performance")
        for index_stmt in self._generate_indexes():
            schema_parts.append(index_stmt)
        schema_parts.append("")
        
        return "\n".join(schema_parts)
    
    def save_schema(self, output_path: str):
        """Save generated schema to file"""
        schema = self.generate_schema()
        
        with open(output_path, 'w') as f:
            f.write(schema)
        
        print(f"Schema saved to: {output_path}")
    
    def save_timestamped_schema(self, schema_dir: str = "schema"):
        """Save schema with timestamp for versioning"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nebula_people_schema_{timestamp}.ngql"
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


def main():
    """Main function to generate schema"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Nebula Graph schema from People ontology')
    parser.add_argument('--ontology', default='../../../ontology/people/people_ontology.yaml', 
                       help='Path to ontology YAML file')
    parser.add_argument('--output', default='schema/nebula_people_schema.ngql',
                       help='Output schema file path')
    parser.add_argument('--timestamped', action='store_true',
                       help='Generate timestamped schema file')
    parser.add_argument('--schema-dir', default='schema',
                       help='Schema directory for timestamped files')
    
    args = parser.parse_args()
    
    # Generate schema
    generator = NebulaSchemaGenerator(args.ontology)
    
    if args.timestamped:
        output_path = generator.save_timestamped_schema(args.schema_dir)
        print(f"Timestamped schema saved to: {output_path}")
    else:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        generator.save_schema(args.output)


if __name__ == "__main__":
    main()
