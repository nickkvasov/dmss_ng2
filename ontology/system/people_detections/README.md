# People Detections Ontology

This ontology defines the data structure for handling position detection and location events related to people in the tourism and event impact system.

## Overview

The People Detections Ontology is designed to handle:
- **Raw position events** (GPS pings) with spatiotemporal attributes
- **Raw ticket entry events** at POI venues
- **Geospatial associations** between positions and POIs
- **Movement and attendance tracking** for tourism and event impact analysis

## Domain Context

This ontology is specifically designed for:
- **Tourism & Event Impact Analysis**: Understanding movement patterns and event participation
- **Geospatial Anomaly Detection**: Foundation for detecting unusual patterns in tourist/local behavior
- **Raw Data Retention**: Preserving unprocessed observations for later analysis
- **Multi-role Analysis**: Supporting tourists, locals, staff, and police data

## Entity Types (Vertices)

### POSITION_PING
Raw GPS position event emitted by a person:
- **Required fields**: `event_id`, `person_id`, `lat`, `lon`, `timestamp`
- **Optional fields**: `accuracy` (GPS accuracy in meters)
- **Coordinate system**: WGS84 (EPSG:4326)

### TICKET_ENTRY
Raw ticket entry event at a POI venue:
- **Required fields**: `event_id`, `person_id`, `poi_id`, `timestamp`
- **Optional fields**: `ticket_class` (ticket type/class)

## Relationship Types (Edges)

### Event Relationships
- **DETECTED_BY**: Person → PositionPing (person detected by a position ping event)
- **ENTERED_AT**: Person → TicketEntry (person entered a POI via ticket entry)

### Geospatial Relationships
- **LOCATED_AT**: PositionPing → POI (position occurred at/near a POI via nearest-neighbor association)
- **REGISTERED_AT**: TicketEntry → POI (ticket entry registered at a POI)

## Key Design Principles

### Raw Data Focus
- **No preprocessing**: Store raw events as-is beyond schema validation
- **No abstractions**: Exclude derived groups, itineraries, or embeddings
- **Raw links only**: Preserve original event relationships

### Geospatial Handling
- **WGS84 coordinates**: Standard coordinate system for all spatial data
- **Optional POI association**: Link positions to POIs via nearest-neighbor, but preserve raw lat/lon
- **No trajectory processing**: No staypoint detection or trajectory segmentation

## Usage Examples

### Position Ping Event
```yaml
event_id: "pos001"
person_id: "p001"
lat: 40.7829
lon: -73.9654
timestamp: "2024-08-26T10:30:00Z"
accuracy: 5.2
```

### Ticket Entry Event
```yaml
event_id: "ticket001"
person_id: "p001"
poi_id: "poi123"
timestamp: "2024-08-26T14:15:00Z"
ticket_class: "vip"
```

### Geospatial Association
```yaml
source: "pos001"  # position_ping event_id
target: "poi123"  # poi_id
relationship: "LOCATED_AT"
properties:
  distance: 25.5
  location_type: "nearest"
  association_confidence: 0.95
```

## Data Types

The ontology supports the following data types:
- **string**: Text data (IDs, ticket classes, entry methods)
- **double**: Decimal numbers (coordinates, accuracy, distance)
- **timestamp**: Date and time values (event timestamps)

## Indexes

Performance indexes are defined for:
- Position events by person and time (for movement analysis)
- Position events by location (for spatial queries)
- Ticket entries by person and time (for attendance analysis)
- Ticket entries by POI and time (for venue analysis)

## Query Patterns

This ontology supports the following query patterns:
- Retrieve all `PositionPings` for a person in a time window
- Retrieve all `TicketEntries` for a POI in a time window
- Retrieve raw co-occurrence of persons at the same POI within Δt
- Analyze movement patterns by person role
- Detect spatial anomalies in position data

## Integration

This ontology works in conjunction with:
- **People Ontology**: For person-role relationships
- **POI Ontology**: For POI definitions and categories
- **Position Events**: For real-time location tracking

## Version History

- **v1.0**: Initial version focused on position and location tracking
- Raw event modeling for position pings and ticket entries
- Geospatial association capabilities
- Performance optimization with strategic indexing
