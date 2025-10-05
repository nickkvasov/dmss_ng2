# Tourist Behavior Generator

A comprehensive generator for synthetic tourist data including visitor profiles, behaviors, and patterns based on Points of Interest (POI) data.

## Overview

The Tourist Behavior Generator creates realistic tourist data for tourism analysis and impact assessment. It generates:

- **Tourist Profiles**: Different types of tourists with varying demographics, preferences, and behaviors
- **Tourist Behaviors**: Visit patterns, activities, spending, satisfaction ratings, and reviews
- **Behavioral Patterns**: Time-based patterns, seasonal variations, and tourist type-specific behaviors

## Features

### Tourist Types

The generator supports multiple tourist types with distinct characteristics:

1. **Cultural Tourist** (25%)
   - Interested in museums, historic sites, and cultural experiences
   - Spends 2-4 hours per POI, visits 3-5 POIs per day
   - Prefers morning visits, takes photos frequently, reads descriptions

2. **Leisure Tourist** (30%)
   - Focused on relaxation, parks, and casual activities
   - Spends 1-3 hours per POI, visits 2-4 POIs per day
   - Prefers afternoon visits, enjoys outdoor activities

3. **Adventure Tourist** (15%)
   - Seeks unique experiences and off-the-beaten-path locations
   - Spends 1-2 hours per POI, visits 5-8 POIs per day
   - Prefers early morning visits, explores quickly

4. **Family Tourist** (20%)
   - Families with children visiting family-friendly attractions
   - Spends 2-5 hours per POI, visits 1-3 POIs per day
   - Prefers mid-morning visits, frequent breaks, educational focus

5. **Business Tourist** (10%)
   - Business travelers with limited time for sightseeing
   - Spends 30 min-1 hour per POI, visits 1-2 POIs per day
   - Prefers evening visits, quick photos, efficient routing

### Generated Data

#### Tourist Profiles
- Tourist ID, type, age, group size
- Stay duration, budget level
- Origin country and city
- Arrival and departure dates
- Preferences and behavior patterns

#### Tourist Behaviors
- Behavior ID, tourist ID, POI ID
- Visit date and time
- Duration, activities performed
- Satisfaction rating (1-5 scale)
- Spending amount
- Number of photos taken
- Review text

## Installation

The tourist generator is part of the DMSS NG2 project and uses the project's virtual environment (`.venv`). Ensure you have the required dependencies:

```bash
# Activate the project's virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate tourist data for New York City using default settings:

```bash
# Using the convenience script (recommended)
./generators/tourists/run_tourist_generator.sh --city new_york

# Or manually with virtual environment
source .venv/bin/activate
python generators/tourists/generate_tourists.py --city new_york
```

### Advanced Usage

Generate tourist data with custom parameters:

```bash
# Using the convenience script (recommended)
./generators/tourists/run_tourist_generator.sh \
    --city new_york \
    --poi-data data/generated/new_york \
    --config generators/tourists/config.yaml \
    --count 500

# Or manually with virtual environment
source .venv/bin/activate
python generators/tourists/generate_tourists.py \
    --city new_york \
    --poi-data data/generated/new_york \
    --config generators/tourists/config.yaml \
    --count 500
```

### Using the Tourist Generator Class

```python
# Make sure to activate the virtual environment first
# source .venv/bin/activate

from generators.tourists.tourist_generator import TouristGenerator

# Initialize generator
generator = TouristGenerator(
    config_path="generators/tourists/config.yaml",
    poi_data_path="data/generated/new_york"
)

# Generate tourist profiles
tourists = generator.generate_tourist_profiles(count=100)

# Generate tourist behaviors
behaviors = generator.generate_tourist_behaviors(tourists)

# Generate and save all data
output_data = generator.generate_all_data(city="new_york")
```

## Configuration

The generator is configured via `config.yaml`:

### Tourist Types Configuration

```yaml
tourist_types:
  cultural_tourist:
    description: "Tourists interested in museums, historic sites, and cultural experiences"
    percentage: 25
    preferences:
      - museums
      - historic_sites
      - monuments
      - theaters
    behavior_patterns:
      - "spends_2_4_hours_per_poi"
      - "visits_3_5_pois_per_day"
      - "prefers_morning_visits"
    demographics:
      age_range: [25, 65]
      group_size: [1, 4]
      stay_duration: [3, 7]
      budget_level: "medium_to_high"
```

### Behavior Patterns

```yaml
behavior_patterns:
  visit_duration:
    quick: [0.25, 1.0]      # 15 minutes to 1 hour
    normal: [1.0, 3.0]      # 1 to 3 hours
    extended: [3.0, 6.0]    # 3 to 6 hours
    full_day: [6.0, 12.0]   # 6 to 12 hours

  daily_poi_count:
    low: [1, 2]
    medium: [2, 4]
    high: [4, 6]
    very_high: [6, 10]
```

### Seasonal Patterns

```yaml
seasonal_patterns:
  spring:
    multiplier: 1.2
    preferred_activities: ["parks", "landmarks"]
  summer:
    multiplier: 1.5
    preferred_activities: ["parks", "landmarks", "museums"]
  fall:
    multiplier: 1.1
    preferred_activities: ["historic_sites", "museums"]
  winter:
    multiplier: 0.8
    preferred_activities: ["museums", "theaters"]
```

## Output Format

The generator creates the following files in `data/generated/{city}/tourists/`:

### JSON Format (`tourists_data.json`)

```json
{
  "tourists": [
    {
      "tourist_id": "tourist_abc12345",
      "tourist_type": "cultural_tourist",
      "age": 35,
      "group_size": 2,
      "stay_duration": 5,
      "budget_level": "medium_to_high",
      "origin_country": "United States",
      "origin_city": "Los Angeles",
      "arrival_date": "2024-06-15",
      "departure_date": "2024-06-20",
      "preferences": ["museums", "historic_sites"],
      "behavior_patterns": ["spends_2_4_hours_per_poi", "visits_3_5_pois_per_day"]
    }
  ],
  "behaviors": [
    {
      "behavior_id": "behavior_def67890",
      "tourist_id": "tourist_abc12345",
      "poi_id": "landmark_123456789",
      "visit_date": "2024-06-16",
      "visit_time": "10:30",
      "duration_hours": 2.5,
      "activities": ["taking_photos", "reading_plaques", "viewing_exhibits"],
      "satisfaction_rating": 4.2,
      "spending_amount": 15.50,
      "photos_taken": 18,
      "review_text": "Fascinating exhibits and rich history. Highly educational experience."
    }
  ],
  "metadata": {
    "generation_date": "2024-01-15T10:30:00",
    "total_tourists": 1000,
    "total_behaviors": 4500,
    "city": "new_york",
    "config_used": {...}
  }
}
```

### CSV Format

- `tourists.csv`: Tourist profiles
- `behaviors.csv`: Tourist behaviors

## Testing

Run the test suite to validate the generator:

```bash
# Using the convenience script (recommended)
./generators/tourists/run_tests.sh

# Or manually with virtual environment
source .venv/bin/activate
python generators/tourists/test_tourist_generator.py
```

## Examples

Run the example script to see the tourist generator in action:

```bash
# Using the virtual environment
source .venv/bin/activate
python generators/tourists/example_usage.py
```

The example script demonstrates:
- Basic tourist profile generation
- Custom configuration usage
- Data export functionality
- Integration with POI data

The test suite validates:
- Generator initialization
- Configuration loading
- POI data loading
- Tourist profile generation
- Tourist behavior generation
- Data export functionality

## Dependencies

- POI data from the POI generator
- Python 3.7+
- Required packages: `pyyaml`, `dataclasses` (Python 3.7+)

## File Structure

```
generators/tourists/
├── __init__.py                           # Module initialization
├── config.yaml                           # Configuration file
├── tourist_generator.py                  # Main tourist generator class
├── people_detections_generator.py        # People detections generator (ontology-compliant)
├── generate_tourists.py                  # Command-line script
├── test_tourist_generator.py             # Test suite
├── example_usage.py                      # Example usage script
├── run_tourist_generator.sh              # Convenience script (uses .venv)
├── run_people_detections.sh              # People detections script (uses .venv)
├── run_tests.sh                          # Test runner script (uses .venv)
├── README.md                             # This file
└── README_people_detections.md           # People detections documentation
```

## Integration with POI Generator

The tourist generator depends on POI data generated by the POI generator. Ensure POI data exists before running the tourist generator:

1. Run the POI generator first:
   ```bash
   source .venv/bin/activate
   python generators/poi/generate_pois_by_area.py --city new_york
   ```

2. Then run the tourist generator:
   ```bash
   # Using the convenience script (recommended)
   ./generators/tourists/run_tourist_generator.sh --city new_york
   
   # Or manually with virtual environment
   source .venv/bin/activate
   python generators/tourists/generate_tourists.py --city new_york
   ```

## Customization

### Adding New Tourist Types

1. Add the tourist type to `config.yaml`:
   ```yaml
   new_tourist_type:
     description: "Description of the new tourist type"
     percentage: 10
     preferences: ["category1", "category2"]
     behavior_patterns: ["pattern1", "pattern2"]
     demographics:
       age_range: [20, 50]
       group_size: [1, 3]
       stay_duration: [2, 5]
       budget_level: "medium"
   ```

2. Update behavior generation methods in `tourist_generator.py` if needed.

### Modifying Behavior Patterns

Edit the behavior pattern methods in `tourist_generator.py`:
- `_generate_visit_time()`: Customize visit time patterns
- `_generate_visit_duration()`: Customize visit duration patterns
- `_generate_activities()`: Customize activity generation
- `_generate_spending_amount()`: Customize spending patterns

## Contributing

When contributing to the tourist generator:

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for new features
4. Ensure compatibility with existing POI data format

## People Detections Generator

For ontology-compliant data generation that conforms to the `people_detections_ontology.yaml`, use the People Detections Generator:

```bash
# Generate ontology-compliant people detection data
./generators/tourists/run_people_detections.sh --city new_york --count 100
```

This generator creates:
- **POSITION_PING** entities with WKT POINT geometry
- **TICKET_ENTRY** entities for POI visits
- **PERSON** entities with tourist profiles
- Data ready for knowledge graph relationships

See `README_people_detections.md` for detailed documentation.

## Restructured Generators (New Architecture)

The project now includes restructured generators that separate raw detection data from behavioral/scene data:

### Raw Detections Generator

The `raw_detections_generator.py` generates actual detection events for knowledge graph ingestion.

**Output**: `data/generated/{city}/raw/tourists/`
- Raw position pings and ticket entries
- Basic tourist profiles
- Ontology-compliant data for direct ingestion

**Usage**:
```bash
./generators/tourists/run_raw_detections.sh --city new_york --count 50
```

### Scene Behavior Generator

The `scene_behavior_generator.py` generates behavioral and scene setup data.

**Output**: `data/generated/{city}/scene/tourists/setup/`
- Detailed tourist profiles with preferences and behavior patterns
- Group structures and dynamics
- Scene configuration (weather, events, distributions)
- Behavioral pattern definitions

**Usage**:
```bash
./generators/tourists/run_scene_behavior.sh --city new_york --count 50
```

### Group Behavior Generator

The `group_behavior_generator.py` demonstrates advanced group behavior using `group_size` properly.

**Features**:
- Realistic group formation and coordination
- Coordinated movement patterns
- Group entry behavior at POIs
- Role-based behavior within groups

**Usage**:
```bash
./generators/tourists/run_group_behavior.sh --city new_york --count 50
```

See `README_restructured.md` for comprehensive documentation of the new architecture.

## License

This project is part of the DMSS NG2 knowledge graph system. See the main LICENSE file for details.
