# System Ontologies

This directory contains system ontologies that represent operational data, events, and system-level entities related to position detection, ticket entries, and other system operations.

## Overview

System ontologies define entities and relationships that are related to system operations, data collection, and operational events. These ontologies represent the "how" of data collection and system behavior rather than the "what" of domain concepts.

## Ontologies

### **People Detections (Position Detection)**
- **File**: `people_detections/people_detections_ontology.yaml`
- **Description**: Location events, position tracking, and spatial-temporal data
- **Entities**: POSITION_PING, TICKET_ENTRY
- **Relationships**: DETECTED_BY, ENTERED_AT, LOCATED_AT, REGISTERED_AT
- **Purpose**: Represents system events for position detection and venue entry
- **Key Features**:
  - Raw GPS position events with accuracy metrics
  - Ticket entry events with venue associations
  - Geospatial POI associations via nearest-neighbor
  - Temporal tracking with precise timestamps
  - Source and confidence tracking for data quality
  - Clear relationship naming for better semantic understanding

### **System Events (planned)**
- **File**: `system_events/system_events_ontology.yaml`
- **Description**: System-level events and operational data
- **Entities**: SYSTEM_EVENT, EVENT_TYPE, EVENT_SOURCE
- **Relationships**: GENERATED_BY, PROCESSED_BY, TRIGGERED
- **Purpose**: Represents system events and operational data

### **Data Collection (planned)**
- **File**: `data_collection/data_collection_ontology.yaml`
- **Description**: Data collection processes and metadata
- **Entities**: DATA_SOURCE, COLLECTION_SESSION, DATA_QUALITY
- **Relationships**: COLLECTED_FROM, VALIDATED_BY, PROCESSED_IN
- **Purpose**: Represents data collection processes and quality metrics

## Characteristics

### **Operational Focus**
- Focused on system operations and data collection
- Represents "how" data is collected and processed
- Includes technical and operational metadata

### **Event-Driven**
- Based on events and operational data
- Temporal and spatial tracking
- Real-time and batch processing support

### **System-Critical**
- Essential for understanding system behavior
- Used for monitoring and operational analytics
- Supports data quality and system reliability

## Usage

System ontologies are used by:
- **Data Ingestion**: To structure operational data
- **System Monitoring**: To track system performance and events
- **Data Quality**: To monitor data collection quality
- **Operational Analytics**: To understand system behavior

## Adding New System Ontologies

When adding new system ontologies:

1. **Validate Operational Relevance**: Ensure the ontology represents system operations
2. **Focus on Events**: Base the ontology on events and operational data
3. **Include Metadata**: Include technical and operational metadata
4. **Maintain Consistency**: Follow established patterns and naming conventions
5. **Document**: Provide clear descriptions of system behavior

## Relationships with Other Ontologies

System ontologies reference:
- **Domain Ontologies**: For domain entities (PERSON, POI)
- **App Ontologies**: For application-specific processing
- **Cross-System**: For integration with other systems

## Examples

### **Position Detection Events**
- GPS position pings from mobile devices
- WiFi-based location detection
- Bluetooth beacon proximity events

### **Ticket Entry Events**
- Venue entry scans
- Ticket validation events
- Access control events

### **System Monitoring Events**
- Data collection sessions
- Quality validation events
- System performance metrics
