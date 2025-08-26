# POI Ingestor for Nebula Graph

This module provides tools to ingest Points of Interest (POI) data into Nebula Graph database.

## Overview

The POI ingestion system consists of:

1. **POI Ontology** (`ontology/domain/poi/poi_ontology.yaml`) - Defines the data structure for POIs
2. **Generic Schema Generator** (`../generic_schema_generator.py`) - Converts ontology to Nebula Graph schema with GEOGRAPHY support
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
# Generate current schema using the generic schema generator
cd ..
python3 generic_schema_generator.py --space-name poi_space

# Generate timestamped schema for versioning
python3 generic_schema_generator.py --space-name poi_space --timestamped

# Generate with custom output location
python3 generic_schema_generator.py --space-name poi_space --output schema/custom_schema.ngql
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

### Unified Command-Line Interface

The POI ingestor now follows the same command-line pattern as the schema generator, with `--space-name` as the primary parameter:

```bash
python3 poi_ingestor.py --space-name <space_name> --data-dir /path/to/generated/poi/data
```

### Basic Ingestion

Ingest POI data from a generated data directory:

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york
```

### With Custom Configuration

Use a custom configuration file (command-line arguments override file settings):

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york --config config.yaml
```

### Connection Parameters

Override Nebula Graph connection settings:

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york \
  --host localhost --port 9669 --username root --password nebula
```

### Batch Processing

Control batch size for ingestion:

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york --batch-size 50
```

### Dry Run (Data Validation)

Validate data without ingesting to Nebula Graph:

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york --dry-run
```

### Skip Relationship Creation

If you only want to create POI vertices without IS_OF_TYPE relationships:

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york --no-relationships
```

### Skip Schema Setup

If you want to skip automatic schema setup (e.g., if schema already exists):

```bash
python3 poi_ingestor.py --space-name tourism_test1 --data-dir ../../../data/generated/new_york --no-schema-setup
```

## Configuration

The ingestor can be configured via a YAML file, but command-line arguments take precedence and override file settings. See `config.yaml` for available options:

- **Nebula Graph connection settings** (can be overridden via `--host`, `--port`, `--username`, `--password`)
- **Space name** (must be specified via `--space-name`)
- **Batch size for ingestion** (can be overridden via `--batch-size`)
- **Relationship creation parameters**
- **Data validation rules**
- **Logging configuration**

### Configuration Priority

1. **Command-line arguments** (highest priority)
2. **Configuration file** (if specified)
3. **Default values** (lowest priority)

This allows for flexible deployment scenarios where the same configuration file can be used with different space names and connection parameters.

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

### Spatial Data Handling

The ingestor automatically converts lat/lon coordinates to WKT POINT format for Nebula Graph's GEOGRAPHY type:

- **Input**: `lat: 40.7829, lon: -73.9654`
- **Output**: `location: "POINT(-73.9654 40.7829)"` (WKT format)
- **Database**: `ST_GeogFromText('POINT(-73.9654 40.7829)')` (GEOGRAPHY type)

This enables efficient spatial queries using Nebula Graph's spatial functions and indexes.
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

-- Spatial queries using GEOGRAPHY type
-- Find POIs within 1km of a reference point
LOOKUP ON POI WHERE ST_DWithin(POI.location, ST_GeogFromText("POINT(-73.9654 40.7829)"), 1000);

-- Find POIs within a polygon area
LOOKUP ON POI WHERE ST_Within(POI.location, 
    ST_GeogFromText("POLYGON((-74.0 40.7, -73.9 40.7, -73.9 40.8, -74.0 40.8, -74.0 40.7))"));

-- Find closest POI to a point
GO FROM "some_vertex_id" OVER LOCATED_AT 
YIELD POI.name, ST_Distance(POI.location, ST_GeogFromText("POINT(-73.9654 40.7829)")) as distance 
ORDER BY distance ASC LIMIT 1;
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
