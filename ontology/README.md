# Ontology Directory

This directory contains ontology definitions for the knowledge graph system. Ontologies define the structure, entities, relationships, and properties that will be used across different graph databases and ingestion processes.

## Structure

```
ontology/
├── poi/                    # Points of Interest ontology
│   ├── poi_ontology.yaml   # Main ontology definition
│   └── README.md          # POI-specific documentation
├── people/                 # People ontology (tourism & event impact)
│   ├── people_ontology.yaml # Main ontology definition
│   └── README.md          # People-specific documentation
├── people_locations/       # People locations ontology
│   ├── people_locations_ontology.yaml # Main ontology definition
│   └── README.md          # People locations documentation
└── README.md              # This file
```

## Ontology Files

Each ontology is defined in YAML format and contains:

- **Entities**: Vertex types and their properties
- **Relationships**: Edge types and their properties  
- **Indexes**: Performance optimization definitions
- **Metadata**: Version, description, and other metadata

## Usage

Ontologies are used by:

1. **Schema Generators**: Convert ontology definitions to database-specific schemas
2. **Ingestion Processes**: Validate and structure data according to ontology
3. **Query Interfaces**: Provide consistent data models across the system

## Conversion Scripts

Conversion scripts that transform ontologies to database-specific schemas are located in their respective ingestion directories:

- **Nebula Graph POI**: `ingestors/nebula/poi/nebula_schema_generator.py`
- **Nebula Graph People**: `ingestors/nebula/people/nebula_schema_generator.py`
- **Nebula Graph People Locations**: `ingestors/nebula/people_locations/nebula_schema_generator.py`
- **Other databases**: Located in their respective ingestion directories

This separation ensures that:
- Ontologies remain database-agnostic
- Conversion logic is specific to each database technology
- Ingestion processes can handle their own schema requirements

## Adding New Ontologies

To add a new ontology:

1. Create a new subdirectory under `ontology/`
2. Define the ontology in YAML format
3. Create appropriate conversion scripts in the relevant ingestion directories
4. Update this README with documentation
