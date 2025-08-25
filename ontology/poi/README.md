# POI Ontology

This directory contains the Points of Interest (POI) ontology definition for the knowledge graph system.

## Files

- `poi_ontology.yaml` - Main ontology definition in YAML format
- `README.md` - This documentation file

## Ontology Structure

### Entities (Vertices)

#### POI
Main entity representing Points of Interest with properties:
- `poi_id` (string, required): Unique identifier
- `name` (string, required): POI name
- `category` (string, required): Primary category
- `lat` (double, required): Latitude coordinate
- `lon` (double, required): Longitude coordinate
- `address` (string, optional): Street address
- `description` (string, optional): Detailed description
- `rating` (double, optional): Average rating (0.0-5.0)
- `opening_hours` (string, optional): Opening hours information
- `capacity` (int, optional): Maximum capacity

#### POI_TYPE
Entity representing POI type classifications:
- `type_id` (string, required): Unique type identifier
- `name` (string, required): Type name
- `description` (string, optional): Type description
- `category` (string, optional): Category classification

### Relationships (Edges)

#### IS_OF_TYPE
Relationship connecting POIs to their types:
- `confidence` (double, optional): Confidence score for classification

### Indexes

Performance optimization indexes:
- `poi_location_idx`: Location-based queries (lat, lon)
- `poi_category_idx`: Category-based queries
- `poi_type_name_idx`: POI type name queries

## Usage

This ontology is used by:

1. **Nebula Graph Ingestion**: `ingestors/nebula/poi/`
   - Schema generation via `nebula_schema_generator.py`
   - Data validation and ingestion via `poi_ingestor.py`

2. **Other Graph Databases**: Future ingestion processes can use this ontology as a reference

## Schema Generation

The ontology is converted to database-specific schemas using conversion scripts located in the ingestion directories. For Nebula Graph, the conversion script is:

```
ingestors/nebula/poi/nebula_schema_generator.py
```

This script:
- Reads the YAML ontology definition
- Generates Nebula Graph schema statements
- Can be used standalone or integrated into the ingestion process

## Configuration

The ontology path and schema setup behavior can be configured in:

```
ingestors/nebula/poi/config.yaml
```

Key configuration options:
- `ontology.path`: Path to the ontology file
- `ontology.auto_setup_schema`: Whether to automatically setup schema during ingestion
