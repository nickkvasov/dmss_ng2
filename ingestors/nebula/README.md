# Nebula Graph Schema Management System

## Overview

This directory contains a comprehensive system for managing Nebula Graph schemas from ontology definitions. The system provides end-to-end automation from YAML ontology files to live Nebula Graph database deployment.

## 🏗️ **Architecture**

### **Core Components**
- **Ontology Parser**: YAML-based ontology definition system
- **Schema Generator**: Unified schema generation from multiple ontologies
- **Schema Committer**: Database deployment with validation
- **Configuration System**: Centralized configuration management
- **End-to-End Pipeline**: Complete automation workflow

### **Key Features**
- ✅ **Multi-Ontology Support**: Combine multiple domain ontologies into single schema
- ✅ **Environment Management**: Development, staging, production configurations
- ✅ **Error Handling**: Robust error handling and retry mechanisms
- ✅ **Validation**: Comprehensive schema and deployment validation
- ✅ **Automation**: Fully automated end-to-end pipeline
- ✅ **Shell Integration**: User-friendly shell script wrappers
- ✅ **Spatial Data Support**: WKT to GEOGRAPHY conversion with spatial indexing
- ✅ **Index Management**: Proper string length specification and asynchronous handling
- ✅ **Unified Interface**: Consistent command-line parameters across all tools

## 📁 **File Structure**

```
ingestors/nebula/
├── README.md                           # This comprehensive documentation
├── config.yaml                         # Central configuration file
├── config_loader.py                    # Configuration management utility
├── generic_schema_generator.py         # Unified schema generator
├── commit_schema.py                    # Schema deployment tool
├── commit_schema.sh                    # Shell wrapper for schema deployment
├── run_end_to_end.py                   # End-to-end pipeline orchestrator
├── run_end_to_end.sh                   # Shell wrapper for end-to-end pipeline
├── drop_space.py                       # Space management utility
├── rebuild_indexes.py                  # Index creation and rebuilding utilities
├── spatial_examples.ngql               # Spatial data examples and queries
├── schema/                             # Generated schema files
│   ├── README.md                       # Schema directory documentation
│   └── nebula_*.ngql                   # Generated nGQL schema files
└── poi/                                # POI data ingestion tools (unified interface)
```

## 🚀 **Quick Start**

### **1. Basic Usage**
```bash
# Run complete pipeline with default settings
./run_end_to_end.sh

# Run with custom space name
./run_end_to_end.sh --space-name my_space

# Run in dry-run mode (preview only)
./run_end_to_end.sh --dry-run

# Run in mock mode (no database connection)
./run_end_to_end.sh --mock
```

### **2. Environment-Specific Usage**
```bash
# Development environment
./run_end_to_end.sh --environment development

# Staging environment with dry-run
./run_end_to_end.sh --environment staging --dry-run

# Production environment
./run_end_to_end.sh --environment production
```

### **3. Advanced Options**
```bash
# Generate timestamped schema file
./run_end_to_end.sh --timestamped

# Skip validation for faster execution
./run_end_to_end.sh --skip-validation

# Use custom configuration
./run_end_to_end.sh --config my_config.yaml
```

## ⚙️ **Configuration**

### **Configuration File (`config.yaml`)**
The system uses a centralized YAML configuration file with the following sections:

#### **Nebula Connection**
```yaml
nebula:
  host: localhost
  port: 9669
  username: root
  password: password
  pool:
    max_connections: 10
    min_connections: 2
  ssl:
    enabled: false
```

#### **Schema Generation**
```yaml
schema:
  default_space_name: nebula_space
  generation:
    partition_num: 10
    replica_factor: 1
    vid_type: FIXED_STRING(32)
  output:
    base_dir: schema
    timestamped: false
```

#### **Environment-Specific Settings**
```yaml
deployment:
  environments:
    development:
      host: localhost
      port: 9669
    staging:
      host: staging-nebula
      port: 9669
    production:
      host: prod-nebula
      port: 9669
```

### **Environment Variables**
Sensitive configuration can be overridden with environment variables:
```bash
export NEBULA_HOST=my-nebula-host
export NEBULA_PORT=9669
export NEBULA_USERNAME=my-user
export NEBULA_PASSWORD=my-password
```

## 🔧 **Core Tools**

### **1. End-to-End Pipeline (`run_end_to_end.py`)**
**Purpose**: Complete automation from ontology to database deployment

**Features**:
- Orchestrates all pipeline steps
- Comprehensive validation and error handling
- Detailed execution logging and reporting
- Support for dry-run and mock modes

**Usage**:
```bash
python run_end_to_end.py --space-name my_space
```

### **2. Schema Generator (`generic_schema_generator.py`)**
**Purpose**: Generate unified Nebula Graph schemas from multiple ontologies

**Features**:
- Loads all ontologies from configured directories
- Generates unified schema with all entities and relationships
- Supports custom space names and configuration
- Creates timestamped schema files

**Usage**:
```bash
python generic_schema_generator.py --space-name my_space
```

### **3. Schema Committer (`commit_schema.py`)**
**Purpose**: Deploy generated schemas to Nebula Graph database

**Features**:
- Live database deployment with validation
- Dry-run mode for preview
- Mock mode for testing
- Error handling and retry mechanisms
- Environment-specific configurations

**Usage**:
```bash
python commit_schema.py schema/nebula_my_space_schema.ngql
```

### **4. Configuration Loader (`config_loader.py`)**
**Purpose**: Centralized configuration management

**Features**:
- YAML configuration parsing
- Environment-specific overrides
- Environment variable support
- Configuration validation
- Default value management

**Usage**:
```python
from config_loader import ConfigLoader
config = ConfigLoader("config.yaml")
nebula_config = config.get_nebula_connection("production")
```

### **5. Spatial Features**
**Purpose**: Native support for geographic data and spatial queries

**Features**:
- **GEOGRAPHY Type**: Native Nebula Graph GEOGRAPHY type for spatial data
- **WKT Support**: Well-Known Text format for POINT, POLYGON, LINESTRING geometries
- **Spatial Indexes**: Optimized S2-based spatial indexes for fast queries
- **Spatial Functions**: Built-in functions for distance, intersection, containment queries
- **Performance Tuning**: Configurable S2 parameters for different geometry types

**Spatial Index Configuration**:
- **POI Locations**: `s2_max_level=30, s2_max_cells=8` (optimized for points)
- **Position Pings**: `s2_max_level=30, s2_max_cells=8` (optimized for points)
- **Anomaly Areas**: `s2_max_level=20, s2_max_cells=16` (optimized for polygons)

**Example Usage**:
```sql
-- Insert with WKT
INSERT VERTEX POI(name, location) VALUES "poi_001":("Dubai Mall", ST_GeogFromText("POINT(55.2744 25.1972)"));

-- Spatial query
LOOKUP ON POI WHERE ST_DWithin(POI.location, ST_GeogFromText("POINT(55.2744 25.1972)"), 1000);
```

**See**: `spatial_examples.ngql` for comprehensive examples

### **5. Space Management (`drop_space.py`)**
**Purpose**: Utility for managing Nebula Graph spaces

**Features**:
- Drop existing spaces
- Space existence checking
- Safe space management

**Usage**:
```bash
python drop_space.py my_space
```

## 📋 **Pipeline Steps**

### **1. Prerequisites Validation**
- ✅ Configuration file validation
- ✅ Required script availability check
- ✅ Ontology directory verification
- ✅ Output directory preparation

### **2. Schema Generation**
- ✅ Load all ontologies from configured directories
- ✅ Parse YAML ontology definitions
- ✅ Generate unified nGQL schema
- ✅ Create schema file with proper formatting

### **3. Schema Validation**
- ✅ File existence and content validation
- ✅ Required schema elements verification
- ✅ Statement count estimation
- ✅ Syntax validation

### **4. Database Deployment**
- ✅ Connect to Nebula Graph
- ✅ Execute CREATE SPACE statement
- ✅ Wait for space propagation
- ✅ Execute all schema statements
- ✅ Validate deployment success

### **5. Summary Reporting**
- ✅ Execution time measurement
- ✅ Success/failure reporting
- ✅ Statistics and metrics
- ✅ Next steps guidance

## 🗂️ **Ontology System**

### **Ontology Structure**
Ontologies are defined in YAML files with the following structure:

```yaml
ontology:
  name: "Example Ontology"
  version: "1.0"
  description: "Description of the ontology"
  
  entities:
    - name: "ENTITY_NAME"
      description: "Entity description"
      properties:
        - name: "property_name"
          type: "string"
          description: "Property description"
          required: true

  relationships:
    - name: "RELATIONSHIP_NAME"
      description: "Relationship description"
      source: "SOURCE_ENTITY"
      target: "TARGET_ENTITY"
      properties:
        - name: "property_name"
          type: "string"
          description: "Property description"
          required: false
```

### **Supported Data Types**
- `string`: Text data
- `int`: Integer numbers
- `double`: Floating-point numbers
- `bool`: Boolean values
- `timestamp`: Date/time values

### **Current Ontologies**
- **POI**: Points of Interest with location and metadata
- **People**: People and role definitions
- **People Locations**: Location events and position tracking

## 🛠️ **Shell Scripts**

### **End-to-End Pipeline (`run_end_to_end.sh`)**
User-friendly shell wrapper for the complete pipeline:

```bash
# Basic usage
./run_end_to_end.sh --space-name my_space

# With options
./run_end_to_end.sh --space-name my_space --environment production --timestamped
```

### **Schema Deployment (`commit_schema.sh`)**
Shell wrapper for schema deployment:

```bash
# Deploy schema
./commit_schema.sh schema/nebula_my_space_schema.ngql

# With options
./commit_schema.sh schema/nebula_my_space_schema.ngql --environment production --dry-run
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Space Already Exists**
```bash
# Drop existing space
python drop_space.py my_space

# Then recreate
./run_end_to_end.sh --space-name my_space
```

#### **2. Connection Issues**
- Check Nebula Graph server status
- Verify connection parameters in `config.yaml`
- Use environment variables for credentials

#### **3. Schema Generation Errors**
- Validate ontology YAML syntax
- Check for reserved keywords (e.g., `timestamp`)
- Ensure all required properties are defined

#### **4. Deployment Failures**
- Use `--dry-run` to preview changes
- Check Nebula Graph logs
- Verify space permissions

### **Debugging Commands**
```bash
# Test configuration
python config_loader.py

# Validate ontologies
python generic_schema_generator.py --list-ontologies

# Test connection
python commit_schema.py schema/test.ngql --dry-run

# Check space status
python drop_space.py my_space --check-only
```

## 📊 **Performance**

### **Typical Execution Times**
- **Schema Generation**: ~0.05 seconds
- **Database Deployment**: ~7 seconds (including 5s delay)
- **Total Pipeline**: ~7-10 seconds

### **Resource Usage**
- **Memory**: Minimal (< 100MB)
- **CPU**: Low usage
- **Network**: Only during database operations

## 🔮 **Future Enhancements**

### **Planned Features**
- **Schema Versioning**: Track schema changes over time
- **Rollback Support**: Revert to previous schema versions
- **Performance Indexes**: Automatic index generation
- **Data Validation**: Schema-based data validation
- **Monitoring**: Performance and usage monitoring

### **Advanced Capabilities**
- **Schema Comparison**: Compare different schema versions
- **Migration Scripts**: Automated schema migrations
- **Backup/Restore**: Schema backup and restoration
- **Multi-Space Support**: Manage multiple spaces simultaneously

## 🌍 **Spatial Data Features**

### **WKT to GEOGRAPHY Conversion**
The system automatically converts `geometry` type properties from ontologies to Nebula Graph's native `GEOGRAPHY` type:

```yaml
# In ontology file
properties:
  - name: "location"
    type: "geometry"  # WKT format
    description: "Geographic location"
```

```sql
-- Generated in schema
CREATE TAG POI (
  location GEOGRAPHY NULL
);
```

### **Spatial Indexes**
S2-based spatial indexes are automatically created for geometry properties:

```sql
-- Generated spatial index
CREATE TAG INDEX poi_location_idx ON POI(location) WITH (s2_max_level=30, s2_max_cells=8);
```

### **Spatial Functions**
The system supports Nebula Graph's spatial functions for queries:

```sql
-- Find POIs within 5km of a point
LOOKUP ON POI WHERE ST_DWithin(POI.location, ST_Point(55.27, 25.20), 5000);

-- Find POIs intersecting with a polygon
LOOKUP ON POI WHERE ST_Intersects(POI.location, ST_GeogFromText("POLYGON((...))"));
```

### **Spatial Examples**
See `spatial_examples.ngql` for comprehensive spatial query examples.

## 🔧 **Index Management**

### **String Length Specification**
Variable-length string properties require prefix length specification in indexes:

```sql
-- Correct: Specify length for string properties
CREATE TAG INDEX poi_category_idx ON POI(category(64));

-- Incorrect: Missing length specification
CREATE TAG INDEX poi_category_idx ON POI(category);
```

### **Asynchronous Index Creation**
Index creation in Nebula Graph is asynchronous. Use `rebuild_indexes.py` to rebuild after creation:

```bash
# Wait for index creation, then rebuild
python rebuild_indexes.py --space-name tourism_data --wait 20

# Rebuild specific indexes
python rebuild_indexes.py --space-name tourism_data --indexes poi_category_idx poi_rating_idx

# List existing indexes
python rebuild_indexes.py --space-name tourism_data --list
```

### **Index Types**
- **Basic Indexes**: String, numeric, and timestamp properties
- **Spatial Indexes**: GEOGRAPHY properties with S2 parameters
- **Composite Indexes**: Multiple properties on the same tag

## 📚 **Examples**

### **Complete Workflow Example**
```bash
# 1. Set up environment
export NEBULA_PASSWORD="my-secure-password"

# 2. Run complete pipeline
./run_end_to_end.sh --space-name tourism_data --environment production

# 3. Verify deployment
python commit_schema.py schema/nebula_tourism_data_schema.ngql --dry-run
```

### **Development Workflow**
```bash
# 1. Test with mock mode
./run_end_to_end.sh --space-name test_space --mock

# 2. Preview with dry-run
./run_end_to_end.sh --space-name test_space --dry-run

# 3. Deploy to development
./run_end_to_end.sh --space-name test_space --environment development
```

## 🤝 **Contributing**

### **Development Setup**
1. Install dependencies: `pip install -r requirements.txt`
2. Set up configuration: Copy and modify `config.yaml`
3. Test with mock mode: `./run_end_to_end.sh --mock`

### **Testing**
- Use `--dry-run` for safe testing
- Use `--mock` for offline testing
- Test with different environments
- Validate schema outputs

## 📄 **License**

This project is part of the DMSS NG2 knowledge graph system.

---

**For more information, see the individual tool documentation and configuration files.**
