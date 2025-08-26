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
- **double**: Decimal numbers (coordinates, ratings, scores)
- **bool**: Boolean values (true/false flags)
- **timestamp**: Date and time values (ISO 8601 format)

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
