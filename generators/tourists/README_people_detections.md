# People Detections Generator

A specialized generator that creates tourist data in accordance with the `people_detections_ontology.yaml` format. This generator produces raw data that can be directly used for tourism and event impact analysis in knowledge graph systems.

## Overview

The People Detections Generator creates data that conforms to the People Detections Ontology, which defines:

- **POSITION_PING** entities: Raw GPS position events with WKT POINT geometry
- **TICKET_ENTRY** entities: Raw ticket entry events at POI venues
- **PERSON** entities: Tourist profiles with demographics and preferences
- **Relationships**: DETECTED_BY, ENTERED_AT, LOCATED_AT, REGISTERED_AT

## Ontology Compliance

### POSITION_PING Entity
```json
{
  "event_id": "ping_1cfc9179",
  "person_id": "person_8519fcbb",
  "position": "POINT(-73.92839803870777 40.75612450629386)",
  "event_timestamp": "2024-02-22T22:38:01",
  "accuracy": 36.55962381156061
}
```

**Required Fields:**
- `event_id`: Unique identifier for the position event
- `person_id`: Reference to the person who emitted this position
- `position`: GPS position as WKT POINT format
- `event_timestamp`: Timestamp of the position ping

**Optional Fields:**
- `accuracy`: GPS accuracy in meters

### TICKET_ENTRY Entity
```json
{
  "event_id": "entry_5ad4ab3d",
  "person_id": "person_8519fcbb",
  "poi_id": "landmark_357642364",
  "entry_timestamp": "2024-02-22T11:53:18",
  "ticket_class": "adult"
}
```

**Required Fields:**
- `event_id`: Unique identifier for the ticket entry event
- `person_id`: Reference to the person who entered
- `poi_id`: Reference to the POI where entry occurred
- `entry_timestamp`: Timestamp of the ticket entry

**Optional Fields:**
- `ticket_class`: Ticket class or type (adult, student, senior, vip, etc.)

### PERSON Entity
```json
{
  "person_id": "person_8519fcbb",
  "tourist_type": "cultural_tourist",
  "age": 30,
  "group_size": 4,
  "stay_duration": 7,
  "budget_level": "medium_to_high",
  "origin_country": "Canada",
  "origin_city": "New York",
  "arrival_date": "2024-02-22",
  "departure_date": "2024-02-29"
}
```

## Features

### GPS Position Generation
- **WKT Format**: All positions are generated in WKT POINT format as required by the ontology
- **Geographic Bounds**: Positions are constrained to NYC bounds (40.7-40.8°N, -74.0 to -73.9°W)
- **Realistic Patterns**: 10-50 position pings per day per person
- **Accuracy Simulation**: GPS accuracy ranging from 5-50 meters

### Ticket Entry Events
- **POI Integration**: Uses existing POI data from the POI generator
- **Tourist Type Preferences**: Different POI selection based on tourist type
- **Time Patterns**: Entry times based on tourist type (morning, afternoon, evening)
- **Ticket Classes**: Realistic ticket classes based on tourist type and budget

### Person Profiles
- **Tourist Types**: Cultural, leisure, adventure, family, business tourists
- **Demographics**: Age, group size, stay duration, budget level
- **Origin Data**: Country and city of origin
- **Stay Periods**: Arrival and departure dates

## Usage

### Basic Usage
```bash
# Generate people detection data for New York City
./generators/tourists/run_people_detections.sh --city new_york --count 50
```

### Advanced Usage
```bash
# Generate with custom configuration and POI data
./generators/tourists/run_people_detections.sh \
    --city new_york \
    --poi-data data/generated/new_york \
    --config generators/tourists/config.yaml \
    --count 100
```

### Using the Generator Class
```python
from generators.tourists.people_detections_generator import PeopleDetectionsGenerator

# Initialize generator
generator = PeopleDetectionsGenerator(
    config_path="generators/tourists/config.yaml",
    poi_data_path="data/generated/new_york"
)

# Generate people detection data
output_data = generator.generate_people_detections_data(city="new_york")
```

## Output Format

The generator creates the following files in `data/generated/{city}/people_detections/`:

### JSON Format (`people_detections_data.json`)
```json
{
  "persons": [...],
  "position_pings": [...],
  "ticket_entries": [...],
  "metadata": {
    "generation_date": "2025-08-31T04:58:13.100054",
    "total_persons": 12,
    "total_position_pings": 1855,
    "total_ticket_entries": 165,
    "city": "new_york",
    "ontology_version": "1.0",
    "ontology_name": "People Detections Ontology",
    "config_used": {...}
  }
}
```

### CSV Format
- `persons.csv`: Person profiles
- `position_pings.csv`: GPS position events
- `ticket_entries.csv`: POI entry events

## Data Statistics

### Sample Dataset (50 persons)
- **Persons**: 12 (cultural tourists)
- **Position Pings**: 1,855 GPS events
- **Ticket Entries**: 165 POI visits
- **Average Pings per Person**: ~154 per day
- **Average POI Visits per Person**: ~14

### Position Ping Characteristics
- **Format**: WKT POINT (e.g., "POINT(-73.92839803870777 40.75612450629386)")
- **Frequency**: 10-50 pings per day per person
- **Time Range**: 6 AM to 10 PM
- **Accuracy**: 5-50 meters
- **Geographic Coverage**: NYC bounds

### Ticket Entry Characteristics
- **POI Integration**: Uses existing POI data
- **Time Patterns**: Based on tourist type preferences
- **Ticket Classes**: adult, student, senior, vip, family, etc.
- **Visit Distribution**: Spread across stay duration

## Integration with Knowledge Graph

The generated data can be directly used to create:

### Vertices (Nodes)
- **PERSON**: Tourist profiles
- **POSITION_PING**: GPS position events
- **TICKET_ENTRY**: POI entry events
- **POI**: Points of interest (from existing POI data)

### Edges (Relationships)
- **DETECTED_BY**: Person → Position Ping
- **ENTERED_AT**: Person → Ticket Entry
- **LOCATED_AT**: Position Ping → POI
- **REGISTERED_AT**: Ticket Entry → POI

## Configuration

The generator uses the same configuration as the tourist generator:

```yaml
tourist_types:
  cultural_tourist:
    percentage: 25
    preferences: ["museums", "historic_sites"]
    demographics:
      age_range: [25, 65]
      group_size: [1, 4]
      stay_duration: [3, 7]
      budget_level: "medium_to_high"

generation:
  total_tourists: 100
  date_range:
    start_date: "2024-01-01"
    end_date: "2024-12-31"
```

## Dependencies

- POI data from the POI generator
- Python 3.7+
- Required packages: `pyyaml`, `dataclasses`

## File Structure

```
generators/tourists/
├── people_detections_generator.py    # Main generator class
├── run_people_detections.sh          # Convenience script (uses .venv)
├── config.yaml                       # Configuration file
└── README_people_detections.md       # This file
```

## Example Workflow

1. **Generate POI Data**:
   ```bash
   python generators/poi/generate_pois_by_area.py --city new_york
   ```

2. **Generate People Detection Data**:
   ```bash
   ./generators/tourists/run_people_detections.sh --city new_york --count 100
   ```

3. **Use in Knowledge Graph**:
   - Load the JSON data into your knowledge graph system
   - Create vertices for persons, position pings, and ticket entries
   - Create edges based on the ontology relationships
   - Perform spatial and temporal analysis

## Benefits

### Ontology Compliance
- **Standard Format**: Data conforms to the defined ontology schema
- **WKT Geometry**: Proper spatial data format for GIS systems
- **Relationship Ready**: Data structured for knowledge graph relationships

### Realistic Data
- **Tourist Behavior**: Based on real tourist type characteristics
- **Spatial Patterns**: Realistic GPS movement patterns
- **Temporal Patterns**: Time-based visit and movement patterns

### Scalability
- **Configurable Volume**: Generate any number of persons
- **Flexible Timeframes**: Customizable date ranges
- **Multiple Cities**: Extensible to different geographic areas

## License

This project is part of the DMSS NG2 knowledge graph system. See the main LICENSE file for details.
