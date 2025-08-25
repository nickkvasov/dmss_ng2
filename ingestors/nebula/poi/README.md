# POI Ingestor for Nebula Graph

This module provides tools to ingest Points of Interest (POI) data into Nebula Graph database.

## Overview

The POI ingestion system consists of:

1. **POI Ontology** (`ontology/poi/poi_ontology.yaml`) - Defines the data structure for POIs
2. **Nebula Schema Generator** (`nebula_schema_generator.py`) - Converts ontology to Nebula Graph schema
3. **POI Ingestor** (`poi_ingestor.py`) - Loads POI data into Nebula Graph with automatic schema setup

## Prerequisites

1. **Nebula Graph Database** - Must be running and accessible
2. **Python Dependencies**:
   ```bash
   pip install nebula3-python pyyaml
   ```

## Setup

The ingestion process automatically handles schema setup from the ontology. No manual schema generation is required.

### Manual Schema Generation (Optional)

If you need to generate the schema manually:

```bash
# Generate current schema
python3 nebula_schema_generator.py

# Generate timestamped schema for versioning
python3 nebula_schema_generator.py --timestamped

# Generate with custom output location
python3 nebula_schema_generator.py --output schema/custom_schema.ngql
```

Generated schemas are saved to the `schema/` directory by default.

### Manual Schema Execution (Optional)

Connect to Nebula Graph and execute the generated schema:

```bash
# Connect to Nebula Graph console
nebula-console -u root -p nebula

# Execute the schema file
source "nebula_schema.ngql"
```

## Usage

### Basic Ingestion

Ingest POI data from a generated data directory:

```bash
python3 poi_ingestor.py --data-dir /path/to/generated/poi/data
```

### With Custom Configuration

Use a custom configuration file:

```bash
python3 poi_ingestor.py --data-dir /path/to/generated/poi/data --config config.yaml
```

### Skip Relationship Creation

If you only want to create POI vertices without IS_OF_TYPE relationships:

```bash
python3 poi_ingestor.py --data-dir /path/to/generated/poi/data --no-relationships
```

### Skip Schema Setup

If you want to skip automatic schema setup (e.g., if schema already exists):

```bash
python3 poi_ingestor.py --data-dir /path/to/generated/poi/data --no-schema-setup
```

## Configuration

The ingestor can be configured via a YAML file. See `config.yaml` for available options:

- **Nebula Graph connection settings**
- **Ontology path and schema setup behavior**
- **Batch size for ingestion**
- **Relationship creation parameters**
- **Data validation rules**
- **Logging configuration**

## Data Format

The ingestor expects POI data in JSON format with the following structure:

```json
{
  "poi_id": "unique_identifier",
  "name": "POI Name",
  "category": "category_name",
  "lat": 40.7829,
  "lon": -73.9654,
  "address": "Street address",
  "description": "Description",
  "rating": 4.5,
  "opening_hours": "9:00-17:00",
  "capacity": 1000,
  "landmark_type": "park"
}
```

## Features

### Data Validation

- Validates required fields (poi_id, name, category, lat, lon)
- Checks coordinate bounds (-90 to 90 for lat, -180 to 180 for lon)
- Validates rating range (0.0 to 5.0)
- Cleans and normalizes string data

### Relationship Creation

- Automatically creates IS_OF_TYPE relationships between POIs and their types
- Extracts POI types from landmark_type or category fields
- Creates POI_TYPE vertices for each unique type
- Configurable confidence threshold for type relationships

### Error Handling

- Robust error handling with detailed logging
- Continues processing even if individual records fail
- Batch processing with configurable batch size

## Example Workflow

1. **Generate POI data** using the POI generators
2. **Create Nebula Graph schema** from ontology
3. **Start Nebula Graph** database
4. **Execute schema** in Nebula Graph
5. **Run ingestion**:
   ```bash
   python3 poi_ingestor.py --data-dir ../../data/generated/new_york
   ```

## Querying the Data

After ingestion, you can query the POI data in Nebula Graph:

```cypher
-- Find all POIs
MATCH (p:POI) RETURN p LIMIT 10;

-- Find POIs by category
MATCH (p:POI) WHERE p.category == "museums" RETURN p;

-- Find POIs by type
MATCH (p:POI)-[r:IS_OF_TYPE]->(t:POI_TYPE) 
WHERE t.name == "museum" 
RETURN p.name, t.name, r.confidence;

-- Find POIs within rating range
MATCH (p:POI) 
WHERE p.rating >= 4.0 
RETURN p.name, p.rating 
ORDER BY p.rating DESC;
```

## Troubleshooting

### Connection Issues

- Ensure Nebula Graph is running and accessible
- Check connection settings in config file
- Verify space exists in Nebula Graph

### Data Issues

- Check data format matches expected structure
- Review validation logs for rejected records
- Ensure coordinates are valid

### Performance Issues

- Adjust batch size in configuration
- Consider disabling relationship creation for large datasets
- Monitor Nebula Graph performance metrics
