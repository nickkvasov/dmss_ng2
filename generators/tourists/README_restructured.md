# Tourist Generators - Restructured Architecture

This document describes the restructured tourist data generation system that separates raw detection data from behavioral/scene data.

## 📁 **New Directory Structure**

```
data/generated/{city}/
├── raw/
│   └── tourists/                    # Raw detection events
│       ├── raw_detections_data.json
│       ├── tourists.csv
│       ├── position_pings.csv
│       └── ticket_entries.csv
├── scene/
│   └── tourists/
│       └── setup/                   # Behavioral and scene data
│           ├── scene_behavior_data.json
│           ├── scene_configuration.json
│           ├── tourists.csv
│           └── groups.csv
└── [other existing directories...]
```

## 🎯 **Data Separation Philosophy**

### **Raw Data** (`data/generated/{city}/raw/tourists/`)
- **Purpose**: Actual detection events that would be captured by sensors/systems
- **Content**: 
  - Position pings (GPS coordinates, timestamps, accuracy)
  - Ticket entries (POI access events)
  - Basic tourist profiles (minimal metadata)
- **Use Case**: Direct ingestion into knowledge graph, sensor simulation, real-time processing

### **Scene Data** (`data/generated/{city}/scene/tourists/setup/`)
- **Purpose**: Behavioral patterns, group dynamics, and scene configuration
- **Content**:
  - Tourist profiles with preferences and behavior patterns
  - Group structures and dynamics
  - Scene configuration (weather, events, distributions)
  - Behavioral pattern definitions
- **Use Case**: Simulation setup, behavioral analysis, scene understanding

## 🚀 **Generators**

### 1. **Raw Detections Generator** (`raw_detections_generator.py`)

Generates raw detection events that conform to the `people_detections_ontology.yaml`.

#### **Features**:
- **Position Pings**: GPS coordinates in WKT format with accuracy
- **Ticket Entries**: POI access events with ticket classes
- **Tourist Profiles**: Basic demographic information
- **Ontology Compliance**: Directly usable with knowledge graph ingestion

#### **Usage**:
```bash
./generators/tourists/run_raw_detections.sh --city new_york --count 50
```

#### **Output Structure**:
```json
{
  "tourists": [
    {
      "person_id": "person_abc123",
      "tourist_type": "cultural_tourist",
      "age": 35,
      "group_size": 2,
      "stay_duration": 5,
      "budget_level": "medium_to_high",
      "origin_country": "Germany",
      "origin_city": "Berlin",
      "arrival_date": "2024-01-15",
      "departure_date": "2024-01-20"
    }
  ],
  "position_pings": [
    {
      "event_id": "ping_def456",
      "person_id": "person_abc123",
      "position": "POINT(-73.9857 40.7484)",
      "event_timestamp": "2024-01-15T10:30:00",
      "accuracy": 15.5
    }
  ],
  "ticket_entries": [
    {
      "event_id": "entry_ghi789",
      "person_id": "person_abc123",
      "poi_id": "museum_12345",
      "entry_timestamp": "2024-01-15T14:00:00",
      "ticket_class": "adult"
    }
  ],
  "metadata": {
    "data_type": "raw_detections",
    "ontology_name": "People Detections Ontology - Raw Data"
  }
}
```

### 2. **Scene Behavior Generator** (`scene_behavior_generator.py`)

Generates comprehensive behavioral and scene setup data.

#### **Features**:
- **Tourist Profiles**: Detailed profiles with preferences and behavior patterns
- **Group Dynamics**: Family, friends, business, and solo traveler groups
- **Behavioral Patterns**: Movement, activity, and social patterns
- **Scene Configuration**: Weather, events, and environmental factors
- **Group Coordination**: Realistic group behavior and decision-making

#### **Usage**:
```bash
./generators/tourists/run_scene_behavior.sh --city new_york --count 50
```

#### **Output Structure**:
```json
{
  "scene_configuration": {
    "scene_id": "scene_abc123",
    "scene_name": "Tourist Scene - New_York",
    "city": "new_york",
    "total_tourists": 50,
    "tourist_types_distribution": {
      "cultural_tourist": 0.25,
      "leisure_tourist": 0.30,
      "family_tourist": 0.20,
      "adventure_tourist": 0.15,
      "business_tourist": 0.10
    },
    "group_size_distribution": {
      "1": 0.30,
      "2": 0.25,
      "3": 0.20,
      "4": 0.15,
      "5+": 0.10
    },
    "behavioral_patterns": [
      {
        "pattern_id": "movement_patterns_fast_pace",
        "pattern_type": "movement_patterns",
        "description": "Fast walking pace, covers more ground quickly",
        "parameters": {
          "speed_multiplier": 1.5,
          "rest_frequency": 0.3
        },
        "probability": 0.2
      }
    ],
    "weather_conditions": {
      "primary_condition": "sunny",
      "temperature_range": [20, 30],
      "precipitation_probability": 0.15,
      "wind_speed": 12.5
    },
    "special_events": ["festivals", "conferences"]
  },
  "tourists": [
    {
      "person_id": "person_abc123",
      "tourist_type": "cultural_tourist",
      "age": 35,
      "group_size": 2,
      "group_id": "group_xyz789",
      "role": "parent",
      "is_group_leader": true,
      "preferences": ["museums", "historic_sites", "art_galleries"],
      "behavior_patterns": [
        "spends_2_4_hours_per_poi",
        "visits_3_5_pois_per_day",
        "photography_focused",
        "movement_patterns_normal_pace",
        "activity_patterns_photography_focused"
      ]
    }
  ],
  "groups": [
    {
      "group_id": "group_xyz789",
      "group_type": "family",
      "group_size": 2,
      "members": ["person_abc123", "person_def456"],
      "group_behavior_patterns": {
        "movement": "coordinated",
        "coordination": "high",
        "separation_probability": 0.1,
        "activity_synchronization": 0.9,
        "decision_making": "parent_led"
      }
    }
  ],
  "metadata": {
    "data_type": "scene_behavior",
    "ontology_name": "Tourist Scene and Behavioral Data"
  }
}
```

## 🔧 **Configuration**

Both generators use YAML configuration files with different focuses:

### **Raw Detections Config**:
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
  detection_settings:
    position_pings_per_day: [10, 50]
    ticket_entries_per_stay: [1, 10]
    gps_accuracy_range: [5.0, 50.0]
    nyc_bounds:
      lat_min: 40.7
      lat_max: 40.8
      lon_min: -74.0
      lon_max: -73.9
```

### **Scene Behavior Config**:
```yaml
tourist_types:
  cultural_tourist:
    percentage: 25
    preferences: ["museums", "historic_sites", "art_galleries"]
    behavior_patterns: ["spends_2_4_hours_per_poi", "photography_focused"]
    demographics:
      age_range: [25, 65]
      group_size: [1, 4]
      stay_duration: [3, 7]
      budget_level: "medium_to_high"

generation:
  scene_settings:
    weather_conditions: ["sunny", "cloudy", "rainy", "snowy"]
    special_events: ["festivals", "conferences", "sports_events"]
    poi_categories: ["museums", "historic_sites", "parks", "landmarks"]
```

## 📊 **Data Statistics**

### **Raw Detections**:
- **Position Pings**: 10-50 per tourist per day
- **Ticket Entries**: 1-10 per tourist per stay
- **GPS Accuracy**: 5-50 meters
- **Coverage**: NYC bounds (40.7-40.8°N, 74.0-73.9°W)

### **Scene Behavior**:
- **Tourist Types**: 5 types with realistic distributions
- **Group Sizes**: 1-8 people with type-specific patterns
- **Behavioral Patterns**: 8+ pattern types across 3 categories
- **Group Types**: Family, friends, business, solo with distinct behaviors

## 🔄 **Integration Workflow**

### **Typical Usage Pattern**:

1. **Generate Scene Data** (Setup):
   ```bash
   ./generators/tourists/run_scene_behavior.sh --city new_york --count 100
   ```

2. **Generate Raw Detections** (Events):
   ```bash
   ./generators/tourists/run_raw_detections.sh --city new_york --count 100
   ```

3. **Use Raw Data for Knowledge Graph**:
   - Position pings → `POSITION_PING` entities
   - Ticket entries → `TICKET_ENTRY` entities
   - Tourist profiles → `PERSON` entities

4. **Use Scene Data for Analysis**:
   - Group dynamics analysis
   - Behavioral pattern recognition
   - Scene understanding and simulation

## 🎯 **Key Benefits**

### **Separation of Concerns**:
- **Raw Data**: Focus on detection events and ontology compliance
- **Scene Data**: Focus on behavioral patterns and group dynamics

### **Flexibility**:
- Generate raw data independently for sensor simulation
- Generate scene data for behavioral analysis
- Mix and match based on use case

### **Scalability**:
- Raw data can be generated at high volumes for performance testing
- Scene data can be generated with complex behavioral patterns
- Independent scaling of detection vs. behavioral complexity

### **Knowledge Graph Integration**:
- Raw data directly maps to ontology entities
- Scene data provides context for understanding behavior
- Clear separation between events and behavioral context

## 🚀 **Quick Start**

```bash
# Generate both raw and scene data
./generators/tourists/run_raw_detections.sh --city new_york --count 50
./generators/tourists/run_scene_behavior.sh --city new_york --count 50

# Check the generated data
ls -la data/generated/new_york/raw/tourists/
ls -la data/generated/new_york/scene/tourists/setup/

# Examine the data structure
jq '.metadata' data/generated/new_york/raw/tourists/raw_detections_data.json
jq '.scene_configuration' data/generated/new_york/scene/tourists/setup/scene_behavior_data.json
```

This restructured approach provides a clean separation between raw detection events and behavioral/scene data, making it easier to use the data for different purposes while maintaining the relationship between them.
