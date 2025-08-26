# Ontology Directory

This directory contains ontology definitions for the knowledge graph system. Ontologies define the structure, entities, relationships, and properties that will be used across different graph databases and ingestion processes.

The ontologies are organized into three main categories:

### **Domain Ontologies** (`domain/`)
Core business entities and concepts that represent confirmed facts in the tourism and event impact analysis domain. These are stable, business-critical ontologies that define the fundamental entities of the domain.

### **System Ontologies** (`system/`)
Operational data, events, and system-level entities related to data collection, position detection, and system operations. These ontologies represent the "how" of data collection and system behavior.

### **Application Ontologies** (`app/`)
Application-specific features, analytics, and business logic such as anomaly detection, alert management, and workflow processes. These ontologies represent the "why" and "what for" of application functionality.

## Structure

```
ontology/
├── domain/                 # Domain-specific ontologies (confirmed facts)
│   ├── poi/               # Points of Interest ontology
│   │   ├── poi_ontology.yaml
│   │   └── README.md
│   ├── people/            # People ontology
│   │   ├── people_ontology.yaml
│   │   └── README.md
│   ├── location/          # Location ontology (confirmed facts)
│   │   ├── location_ontology.yaml
│   │   └── README.md
│   └── README.md          # Domain ontologies documentation
├── system/                 # System ontologies (operational data)
│   ├── people_detections/ # Position detection and events
│   │   ├── people_detections_ontology.yaml
│   │   └── README.md
│   ├── system_events/     # System events and operations
│   ├── data_collection/   # Data collection processes
│   └── README.md          # System ontologies documentation
├── app/                    # Application ontologies (features & analytics)
│   ├── anomaly_ontology.yaml # Anomaly detection and alerts
│   ├── analytics/         # Analytics models and insights
│   ├── workflow/          # Business workflows and processes
│   └── README.md          # Application ontologies documentation
└── README.md              # This file
```

## Ontology Files

Each ontology is defined in YAML format and contains:

- **Entities**: Vertex types and their properties
- **Relationships**: Edge types and their properties  
- **Indexes**: Performance optimization definitions (when applicable)
- **Metadata**: Version, description, and other metadata

## Current Ontologies

### **Domain Ontologies** (`domain/`)
- **POI**: Points of Interest with geospatial and categorical data
- **People**: Individual persons with demographic and role information

### **System Ontologies** (`system/`)
- **People Detections**: Position tracking and venue entry events

### **Application Ontologies** (`app/`)
- **Anomaly Detection**: Anomaly detection patterns and alert management

## Relationship Naming Standards

All ontologies follow consistent relationship naming conventions:

### **Semantic Patterns**
- **`DETECTED_BY`**: Entity A was detected by Entity B
- **`LOCATED_AT`**: Entity A is located at Entity B
- **`ENTERED_AT`**: Entity A entered at Entity B
- **`REGISTERED_AT`**: Entity A was registered at Entity B
- **`HAS_ROLE`**: Entity A has role Entity B
- **`IS_OF_TYPE`**: Entity A is of type Entity B
- **`TRIGGERED`**: Entity A triggered Entity B
- **`ASSIGNED_TO`**: Entity A was assigned to Entity B

### **Direction Guidelines**
- Source entity is typically the "actor" or "subject"
- Target entity is typically the "object" or "location"
- Relationships flow logically from source to target

## Usage

Ontologies are used by:

1. **Schema Generators**: Convert ontology definitions to database-specific schemas
2. **Ingestion Processes**: Validate and structure data according to ontology
3. **Query Interfaces**: Provide consistent data models across the system
4. **Analytics**: Enable cross-ontology queries and insights

## Ontology Integration

The ontologies are designed to work together seamlessly:

### **Cross-Ontology Relationships**
- **Domain → System**: People and POI entities are referenced by detection events
- **System → App**: Detection events can trigger anomaly detection
- **App → Domain**: Anomalies and alerts can be assigned to people and located at POIs

### **Integration Examples**
- Person detected at POI → Anomaly detection → Alert generation → Assignment to staff
- Ticket entry at venue → Attendance analysis → Behavioral anomaly → Alert escalation
- Position tracking → Movement pattern analysis → Spatial anomaly → Location-based alert

## Conversion Scripts

Conversion scripts that transform ontologies to database-specific schemas are located in their respective ingestion directories:

### Nebula Graph Schema Generation
- **Generic Schema Generator**: `ingestors/nebula/generic_schema_generator.py` - Combines all ontologies into a single space
- **Schema Committer**: `ingestors/nebula/commit_schema.py` - Deploys schemas to Nebula Graph database

### Other databases
- Located in their respective ingestion directories

This separation ensures that:
- Ontologies remain database-agnostic
- Conversion logic is specific to each database technology
- Ingestion processes can handle their own schema requirements

## Adding New Ontologies

To add a new ontology:

1. **Choose the appropriate category**:
   - **Domain**: For core business entities and confirmed facts
   - **System**: For operational data and system events
   - **App**: For application features and business logic

2. **Create the ontology structure**:
   - Create a new subdirectory under the appropriate category
   - Define the ontology in YAML format
   - Create a README.md file with documentation

3. **Follow naming conventions**:
   - Directory names: lowercase with underscores (e.g., `people_detections`)
   - YAML files: `{ontology_name}_ontology.yaml`
   - Entity names: UPPERCASE (e.g., `PERSON`, `POI`)
   - Relationship names: UPPERCASE (e.g., `HAS_ROLE`, `IS_OF_TYPE`)

4. **Update documentation**:
   - Update the category README.md
   - Update this main README.md
   - Create appropriate conversion scripts in ingestion directories

## Data Types

The ontologies support the following data types:
- **string**: Text data (IDs, names, descriptions)
- **int**: Integer numbers (ages, capacities, counts)
- **double**: Decimal numbers (ratings, scores, accuracy)
- **bool**: Boolean values (true/false flags)
- **timestamp**: Date and time values (ISO 8601 format)
- **geometry**: Spatial data in WKT format (POINT, POLYGON, LINESTRING) stored as strings

## WKT Geometry Types

The ontologies use Well-Known Text (WKT) format for spatial data, stored as strings in Nebula Graph:

### **POINT Geometry**
- **Format**: `POINT(longitude latitude)`
- **Example**: `POINT(-73.9654 40.7829)`
- **Usage**: GPS coordinates, venue locations, anomaly points
- **Storage**: String field in Nebula Graph

### **POLYGON Geometry**
- **Format**: `POLYGON((lon1 lat1, lon2 lat2, lon3 lat3, lon1 lat1))`
- **Example**: `POLYGON((-73.9654 40.7829, -73.9655 40.7830, -73.9653 40.7831, -73.9654 40.7829))`
- **Usage**: Venue boundaries, anomaly areas, event zones
- **Storage**: String field in Nebula Graph

### **LINESTRING Geometry**
- **Format**: `LINESTRING(lon1 lat1, lon2 lat2, lon3 lat3)`
- **Example**: `LINESTRING(-73.9654 40.7829, -73.9655 40.7830, -73.9656 40.7831)`
- **Usage**: Movement paths, route tracking, boundary lines
- **Storage**: String field in Nebula Graph

### **Coordinate System**
- **Standard**: WGS84 (EPSG:4326)
- **Order**: Longitude first, then Latitude
- **Precision**: 6 decimal places recommended
- **Implementation**: WKT strings stored in Nebula Graph string fields

## Spatial Data Usage

### **Data Insertion Examples**
```cypher
// Insert POI with WKT POINT
INSERT VERTEX POI(poi_id, name, category, location) VALUES 
"poi001":("poi001", "Central Park", "park", "POINT(-73.9654 40.7829)");

// Insert position ping with WKT POINT
INSERT VERTEX POSITION_PING(event_id, person_id, position, event_timestamp) VALUES 
"pos001":("pos001", "p001", "POINT(-73.9654 40.7829)", "2024-08-26T10:30:00Z");

// Insert anomaly with WKT POLYGON
INSERT VERTEX ANOMALY(anomaly_id, anomaly_type, severity, confidence, detected_at, location) VALUES 
"anom001":("anom001", "spatial", "high", 0.95, "2024-08-26T10:30:00Z", 
"POLYGON((-73.9654 40.7829, -73.9655 40.7830, -73.9653 40.7831, -73.9654 40.7829))");
```

### **Spatial Query Examples**
```cypher
// Find POIs within a polygon area
MATCH (p:POI) 
WHERE st_contains("POLYGON((-73.97 40.78, -73.96 40.78, -73.96 40.79, -73.97 40.79, -73.97 40.78))", p.location)
RETURN p;

// Find position pings near a POI
MATCH (pos:POSITION_PING), (p:POI)
WHERE st_distance(pos.position, p.location) < 100
RETURN pos, p;

// Find anomalies overlapping with a specific area
MATCH (a:ANOMALY)
WHERE st_intersects(a.location, "POLYGON((-73.9654 40.7829, -73.9655 40.7830, -73.9653 40.7831, -73.9654 40.7829))")
RETURN a;
```

## Best Practices

1. **Entity Design**:
   - Use clear, descriptive names in UPPERCASE
   - Include required and optional properties
   - Provide detailed descriptions for all elements
   - Use consistent data types across ontologies

2. **Relationship Design**:
   - Define clear source and target entities
   - Include relevant properties on relationships
   - Use descriptive relationship names in UPPERCASE
   - Follow semantic naming patterns (e.g., `DETECTED_BY`, `LOCATED_AT`, `ENTERED_AT`)
   - Ensure relationship direction makes logical sense

3. **Documentation**:
   - Maintain comprehensive README files
   - Include usage examples
   - Document integration points with other ontologies
   - Keep documentation synchronized with ontology changes
