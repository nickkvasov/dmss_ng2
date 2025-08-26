# DMSS NG2 - Knowledge Graph System

## Overview

DMSS NG2 is a comprehensive knowledge graph system designed for tourism and event impact analysis. The system provides end-to-end capabilities from data generation to graph database deployment, with a focus on geospatial and temporal data modeling.

## 🏗️ **System Architecture**

### **Core Components**
- **Data Generation**: Synthetic data generators for POIs, people, and events
- **Ontology Management**: YAML-based ontology definitions for consistent data modeling
- **Schema Generation**: Automated schema generation for graph databases
- **Data Ingestion**: Tools for loading data into graph databases
- **Graph Database**: Nebula Graph for storing and querying knowledge graphs
- **Testing**: Comprehensive test suite for system validation

### **Key Features**
- ✅ **Multi-Ontology Support**: Combine multiple domain ontologies into unified schemas
- ✅ **Geospatial Data**: WGS84 coordinate system with spatial relationships
- ✅ **Temporal Analysis**: Timestamp-based event tracking and analysis
- ✅ **Automated Pipeline**: End-to-end automation from ontology to database
- ✅ **Environment Management**: Development, staging, and production configurations
- ✅ **Comprehensive Testing**: Automated test suite with Docker integration

## 📁 **Project Structure**

```
dmss_ng2/
├── README.md                           # This comprehensive documentation
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
├── ONTOLOGY_REORGANIZATION_SUMMARY.md # Historical reorganization notes
├── data/                              # Generated and ingested data
├── docs/                              # Project documentation
│   └── POC_draft_v0.1.md             # Technical POC requirements
├── generators/                        # Data generation tools
│   └── poi/                          # POI data generation
├── ingestors/                        # Data ingestion tools
│   └── nebula/                       # Nebula Graph ingestion
│       ├── README.md                 # Comprehensive ingestion documentation
│       ├── config.yaml               # Central configuration
│       ├── generic_schema_generator.py # Unified schema generator
│       ├── commit_schema.py          # Schema deployment
│       ├── run_end_to_end.py         # End-to-end pipeline
│       ├── run_end_to_end.sh         # Pipeline shell wrapper
│       ├── drop_space.py             # Space management
│       ├── schema/                   # Generated schemas
│       └── poi/                      # POI data ingestion tools
├── nebula_infrastructure/            # Nebula Graph infrastructure setup
│   ├── nebula-docker-compose/        # Docker Compose configuration
│   └── nebula-graph-studio-3.10.0/   # Graph Studio setup
├── ontology/                         # Ontology definitions
│   ├── README.md                     # Ontology documentation
│   ├── domain/                       # Domain-specific ontologies
│   │   ├── poi/                      # Points of Interest ontology
│   │   └── people/                   # People ontology
│   ├── system/                       # System-level ontologies
│   │   └── people_detections/        # People detection and tracking
│   └── app/                          # Application ontologies
│       └── anomaly_ontology.yaml     # Anomaly detection and alerts
├── scripts/                          # Utility scripts
├── tests/                            # Test suite
│   ├── README.md                     # Test documentation
│   ├── test_nebula.py                # Python test script
│   └── run_nebula_tests.sh           # Test runner script
└── .venv/                            # Python virtual environment
```

## 🚀 **Quick Start**

### **1. Prerequisites**
```bash
# Python 3.8+ and pip
python3 --version
pip3 --version

# Docker (for Nebula Graph)
docker --version
docker-compose --version
```

### **2. Setup**
```bash
# Clone repository
git clone <repository-url>
cd dmss_ng2

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Start Nebula Graph Infrastructure**
```bash
# Start Nebula Graph with Docker
cd nebula_infrastructure/nebula-docker-compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### **4. Start Nebula Graph Studio**
```bash
# Start Nebula Graph Studio
cd nebula_infrastructure/nebula-graph-studio-3.10.0
docker-compose up -d

# Access Studio at: http://localhost:7001
# Default credentials: root/nebula
```

**Important Notes:**
- **Studio Access**: Nebula Graph Studio is accessible at `http://localhost:7001`
- **Graph Connection**: When connecting to the graph from Studio, use the actual system host IP (not localhost)
  - Example: If your system IP is `192.168.1.100`, use that instead of `localhost`
  - This is required because Studio runs in a Docker container and needs the host network IP

### **5. Run End-to-End Pipeline**
```bash
# Navigate to ingestion directory
cd ingestors/nebula

# Run complete pipeline
./run_end_to_end.sh --space-name tourism_data

# Or with custom options
./run_end_to_end.sh --space-name tourism_data --environment development --timestamped
```

## 📋 **Core Workflows**

### **1. Data Generation**
```bash
# Generate POI data
cd generators/poi
python poi_generator.py --area "New York" --count 1000

# Generate synthetic position data
python landmark_fetcher.py --area "New York"
```

### **2. Schema Management**
```bash
# Generate schema from ontologies
cd ingestors/nebula
python generic_schema_generator.py --space-name my_space

# Deploy schema to database
python commit_schema.py schema/nebula_my_space_schema.ngql

# Or use end-to-end pipeline
./run_end_to_end.sh --space-name my_space
```

### **3. Data Ingestion**
```bash
# Ingest POI data with unified command-line interface
cd ingestors/nebula/poi
python poi_ingestor.py --space-name tourism_data --data-dir ../../../data/generated/new_york

# Or use shell wrapper
./run_ingestion.sh --data-dir ../../data/generated/poi
```

### **4. Testing**
```bash
# Run comprehensive tests
cd tests
./run_nebula_tests.sh

# Or run Python tests directly
python test_nebula.py --save-results
```

## 🗂️ **Ontology System**

### **Overview**
The ontology system provides a structured approach to defining knowledge graph schemas using YAML-based ontology definitions. This enables consistent data modeling across different domains and database technologies.

### **Current Ontologies**

#### **Domain Ontologies** (`ontology/domain/`)
- **POI (Points of Interest)**: Tourism attractions, venues, and locations with geospatial metadata
- **People**: Individual persons with demographic information and role classifications

#### **System Ontologies** (`ontology/system/`)
- **People Detections**: Location events, position tracking, and spatial-temporal data

#### **Application Ontologies** (`ontology/app/`)
- **Anomaly Detection**: Anomaly detection, alerting, and pattern recognition

### **Key Features**
- ✅ **Domain-Specific**: Tailored for tourism and event impact analysis
- ✅ **Geospatial Support**: WGS84 coordinate system with spatial relationships
- ✅ **Temporal Tracking**: Timestamp-based event and position tracking
- ✅ **Role-Based Modeling**: Person classification with role hierarchies
- ✅ **Event-Driven**: Position pings and ticket entry events
- ✅ **Cross-Domain Integration**: Unified schema generation from multiple ontologies

### **Ontology Structure**
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
- `string`: Text data (names, descriptions, categories)
- `int`: Integer numbers (ages, capacities, counts)
- `double`: Floating-point numbers (coordinates, ratings, distances)
- `bool`: Boolean values (flags, status indicators)
- `timestamp`: Date/time values (event timestamps, creation dates)
- `geometry`: Geospatial data (WKT format) - automatically converted to Nebula Graph GEOGRAPHY type

### **Ontology Benefits**
- **Consistency**: Standardized data modeling across the system
- **Flexibility**: Easy to extend and modify domain models
- **Reusability**: Ontologies can be used by multiple database technologies
- **Validation**: Schema-based data validation and constraints
- **Documentation**: Self-documenting data models with descriptions

## ⚙️ **Configuration**

### **Central Configuration**
The system uses a centralized YAML configuration system:

```yaml
# ingestors/nebula/config.yaml
nebula:
  host: localhost
  port: 9669
  username: root
  password: password

schema:
  default_space_name: nebula_space
  generation:
    partition_num: 10
    replica_factor: 1
    vid_type: FIXED_STRING(32)

deployment:
  environments:
    development:
      host: localhost
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

### **Unified Command-Line Interface**
All tools now follow a consistent command-line pattern with `--space-name` as the primary parameter:

```bash
# Schema generation
python generic_schema_generator.py --space-name tourism_data

# Schema deployment
python commit_schema.py schema/nebula_tourism_data_schema.ngql

# POI data ingestion
python poi_ingestor.py --space-name tourism_data --data-dir ../../../data/generated/new_york

# Index rebuilding
python rebuild_indexes.py --space-name tourism_data
```

### **Schema Management**
- **`generic_schema_generator.py`**: Generate unified schemas from multiple ontologies
- **`commit_schema.py`**: Deploy schemas to Nebula Graph
- **`run_end_to_end.py`**: Complete automation pipeline
- **`drop_space.py`**: Space management utility
- **`rebuild_indexes.py`**: Index creation and rebuilding utilities

### **Data Generation**
- **`poi_generator.py`**: Generate synthetic POI data
- **`landmark_fetcher.py`**: Fetch real POI data from APIs
- **`fetch_all_areas.py`**: Batch area data fetching

### **Data Ingestion**
- **`poi_ingestor.py`**: Load POI data into graph database (unified command-line interface)
- **`test_ingestion.py`**: Test ingestion processes

### **Testing**
- **`test_nebula.py`**: Comprehensive Python test suite
- **`run_nebula_tests.sh`**: Test runner with Docker integration

## 🛠️ **Shell Scripts**

### **End-to-End Pipeline**
```bash
# Complete workflow
./run_end_to_end.sh --space-name tourism_data

# With options
./run_end_to_end.sh --space-name tourism_data --environment production --timestamped
```

### **Schema Deployment**
```bash
# Deploy schema
./commit_schema.sh schema/nebula_my_space_schema.ngql

# With options
./commit_schema.sh schema/nebula_my_space_schema.ngql --environment production --dry-run
```

### **Testing**
```bash
# Run tests
./run_nebula_tests.sh

# With options
./run_nebula_tests.sh --host 192.168.1.100 --timeout 600
```

## 📊 **Data Model**

### **Core Entities**
- **Person**: People with demographic information and roles
- **POI**: Points of Interest with location and metadata
- **PositionPing**: GPS position events with timestamps
- **TicketEntry**: Venue entry events with timestamps

### **Core Relationships**
- **EMITTED**: Person to PositionPing relationships
- **ENTERED**: Person to TicketEntry relationships
- **AT_POI**: PositionPing to POI spatial relationships
- **HAS_ROLE**: Person to Role relationships
- **IS_OF_TYPE**: POI to POI_TYPE relationships

### **Geospatial Features**
- **Coordinate System**: WGS84 (EPSG:4326)
- **Spatial Relationships**: Nearest-neighbor associations
- **Raw Position Storage**: Preserves original lat/lon coordinates
- **Distance Calculations**: Spatial proximity analysis
- **Nebula Graph GEOGRAPHY**: Native spatial data type with WKT support
- **Spatial Indexes**: S2-based spatial indexing for optimal performance
- **Spatial Functions**: ST_DWithin, ST_Intersects, ST_Distance, ST_Within, ST_Centroid

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Nebula Graph Connection**
```bash
# Check if Nebula is running
docker-compose ps

# Check logs
docker-compose logs nebula-graphd

# Restart services
docker-compose restart
```

#### **2. Schema Deployment**
```bash
# Drop existing space
python drop_space.py my_space

# Recreate space
./run_end_to_end.sh --space-name my_space
```

#### **3. Data Generation**
```bash
# Check configuration
python config_loader.py

# Test with mock mode
./run_end_to_end.sh --mock
```

#### **4. Nebula Graph Studio Connection**
```bash
# Check Studio is running
docker-compose ps

# Access Studio at http://localhost:7001
# Use system host IP (not localhost) when connecting to graph
# Example: 192.168.1.100:9669 instead of localhost:9669
```

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

## 📈 **Performance**

### **Typical Execution Times**
- **Schema Generation**: ~0.05 seconds
- **Database Deployment**: ~7 seconds (including 5s delay)
- **Data Ingestion**: Varies by data volume
- **Test Suite**: ~30-60 seconds

### **Resource Usage**
- **Memory**: Minimal (< 100MB for most operations)
- **CPU**: Low usage
- **Network**: Only during database operations
- **Storage**: Depends on data volume

## 🆕 **Recent Improvements**

### **Index Creation Fixes**
- ✅ **String Length Specification**: Fixed variable-length string index creation with proper prefix lengths
- ✅ **Asynchronous Index Handling**: Proper waiting periods for index creation and rebuilding
- ✅ **Index Rebuild Script**: Dedicated `rebuild_indexes.py` for manual index management
- ✅ **Quote Handling**: Fixed index name parsing from Nebula Graph ResultSet

### **Spatial Data Enhancements**
- ✅ **WKT Support**: Ontology files maintain WKT representation for geometry fields
- ✅ **GEOGRAPHY Type**: Automatic conversion from `geometry` to Nebula Graph `GEOGRAPHY` type
- ✅ **Spatial Indexes**: S2-based spatial indexing with configurable parameters
- ✅ **Spatial Examples**: Comprehensive examples in `spatial_examples.ngql`

### **Unified Command-Line Interface**
- ✅ **Consistent Parameters**: All tools use `--space-name` as primary parameter
- ✅ **Configuration Priority**: Command-line arguments override file settings
- ✅ **Dry Run Support**: Data validation without database connection
- ✅ **Flexible Configuration**: Support for both file-based and command-line configuration

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

## 📚 **Documentation**

### **Detailed Documentation**
- **Ingestion System**: `ingestors/nebula/README.md`
- **Ontology System**: `ontology/README.md`
- **Testing System**: `tests/README.md`
- **POC Requirements**: `docs/POC_draft_v0.1.md`
- **Infrastructure**: `nebula_infrastructure/` - Docker and Studio setup

### **Configuration**
- **Main Configuration**: `ingestors/nebula/config.yaml`
- **POI Configuration**: `ingestors/nebula/poi/config.yaml`
- **Generator Configuration**: `generators/poi/config.yaml`

## 🤝 **Contributing**

### **Development Setup**
1. Install dependencies: `pip install -r requirements.txt`
2. Set up configuration: Copy and modify configuration files
3. Test with mock mode: `./run_end_to_end.sh --mock`

### **Testing**
- Use `--dry-run` for safe testing
- Use `--mock` for offline testing
- Test with different environments
- Validate schema outputs

### **Code Style**
- Follow Python PEP 8 guidelines
- Use meaningful variable and function names
- Add comprehensive docstrings
- Include error handling

## 📄 **License**

MIT License

Copyright (c) 2025 DMSS NG2 Knowledge Graph System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**For detailed information about specific components, see the individual README files in each directory.**
