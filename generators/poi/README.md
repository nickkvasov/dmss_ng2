# POI Generator

A synthetic data generator for Points of Interest (POIs) designed for tourism and event impact analysis. This generator creates realistic POI data with geospatial coordinates, categories, and properties suitable for knowledge graph applications.

## Features

- **Exceptional Landmarks Only**: Focus on significant tourist attractions and landmarks
- **Quality Filtering**: Filter out generic POIs (parking, gas stations, etc.)
- **Limited Counts**: Manageable numbers (15-50 landmarks per category)
- **Specific Categories**: Museums, monuments, parks, historic sites, theaters, landmarks
- **Geospatial Data**: WGS84 coordinates (EPSG:4326) within configurable city bounds
- **Realistic Properties**: Names, addresses, descriptions, landmark types
- **Flexible Configuration**: YAML-based configuration for different cities and categories
- **Multiple Output Formats**: JSON and CSV export options
- **Real Data Sources**: Fetch actual landmark data from OpenStreetMap
- **Synthetic Data Generation**: Generate realistic synthetic POI data for testing
- **Automatic Retry Logic**: Handles transient network errors and API timeouts with exponential backoff
- **Endpoint Fallback**: Automatically tries multiple Overpass API endpoints if one fails

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate POIs for all categories using default configuration:
```bash
python poi_generator.py
```

### Command Line Options

```bash
python poi_generator.py [OPTIONS]

Options:
  --config PATH        Path to configuration YAML file
  --category CATEGORY  Generate POIs for specific category only
  --output-json PATH   Output JSON file path (default: pois.json)
  --output-csv PATH    Output CSV file path (default: pois.csv)
```

### Examples

Generate POIs for a specific category:
```bash
python poi_generator.py --category restaurants
```

Use custom configuration:
```bash
python poi_generator.py --config config.yaml
```

Generate only hotels and save to custom files:
```bash
python poi_generator.py --category hotels --output-json hotels.json --output-csv hotels.csv
```

### Multi-Area Generation

Generate POI data for multiple areas organized in separate directories:

```bash
# Generate for all available areas
python generate_all_areas.py

# Generate for specific areas
python generate_pois_by_area.py --areas new_york london paris

# Generate specific categories for specific areas
python generate_pois_by_area.py --areas tokyo --categories attractions hotels

# Custom output directory
python generate_pois_by_area.py --areas all --output-dir /path/to/output
```

### Landmark Fetching (Recommended)

Fetch exceptional landmarks only:

```bash
# Fetch landmarks from OpenStreetMap (no API key required)
python landmark_fetcher.py --area new_york --categories museums monuments parks

# Fetch specific landmark categories
python landmark_fetcher.py --area london --categories museums historic_sites

# Fetch with custom bounds
python landmark_fetcher.py --area custom --bounds 40.7 40.8 -74.0 -73.9 --categories museums

# Fetch all landmark categories
python landmark_fetcher.py --area paris

# Note: Data is saved to ../../data/generated/ by default
```

### Generic POI Fetching (Legacy)

Fetch all POI data from internet sources:

```bash
# Fetch from OpenStreetMap (no API key required)
python poi_fetcher.py --area new_york --sources osm

# Fetch from multiple sources
python poi_fetcher.py --area london --sources osm opentripmap

# Fetch with custom bounds
python poi_fetcher.py --area custom --bounds 40.7 40.8 -74.0 -73.9 --sources osm

# Fetch for all configured areas
python fetch_all_areas.py

# Note: Data is saved to ../../data/generated/ by default
```

### Landmark Categories

The landmark fetcher focuses on exceptional destinations:

- **Museums**: Art galleries, science museums, cultural institutions (max 50)
- **Monuments**: Memorials, statues, historical monuments (max 30)
- **Parks**: Public parks, gardens, botanical gardens (max 40)
- **Historic Sites**: Castles, palaces, ruins, historic buildings (max 25)
- **Theaters**: Theaters, cinemas, concert halls (max 20)
- **Landmarks**: Towers, bridges, iconic structures (max 15)

### Quality Filtering

The landmark fetcher automatically filters out:
- Generic amenities (parking, gas stations, banks, etc.)
- POIs without proper names
- Non-tourist destinations
- Duplicate entries

### Data Source Comparison

| Source | Free | API Key | Categories | Data Quality | Rate Limit | Focus |
|--------|------|---------|------------|--------------|------------|-------|
| Landmark Fetcher | ✅ | ❌ | 6 landmark | Exceptional | 1 req/s | Landmarks only |
| Generic POI Fetcher | ✅ | ❌ | 4 main | High | 1 req/s | All POIs |
| OpenTripMap | ✅ | ✅ | 11+ | Very High | 2 req/s | Cultural |

### Available Areas

The generator supports the following areas:
- **new_york**: New York City
- **london**: London
- **paris**: Paris
- **tokyo**: Tokyo
- **san_francisco**: San Francisco
- **barcelona**: Barcelona

### Output Structure

When generating for multiple areas, the data is organized as follows:

```
data/generated/
├── new_york/
│   ├── config.yaml
│   ├── pois.json
│   ├── pois.csv
│   ├── attractions.json
│   ├── attractions.csv
│   ├── hotels.json
│   ├── hotels.csv
│   └── ... (other categories)
├── london/
│   ├── config.yaml
│   ├── pois.json
│   └── ... (same structure)
└── ... (other areas)
```

## Configuration

The generator uses YAML configuration files to define:
- City boundaries and coordinates
- POI categories and counts
- Name templates for each category

### Default Configuration

By default, the generator creates POIs for New York City with the following categories:
- **Attractions**: 50 POIs (museums, parks, galleries, etc.)
- **Hotels**: 30 POIs (hotels, inns, resorts, etc.)
- **Restaurants**: 80 POIs (restaurants, cafes, bars, etc.)
- **Venues**: 20 POIs (arenas, theaters, convention centers, etc.)

### Custom Configuration

Create a `config.yaml` file to customize:

```yaml
city_bounds:
  name: "London"
  min_lat: 51.4
  max_lat: 51.6
  min_lon: -0.2
  max_lon: 0.1

poi_categories:
  attractions:
    count: 30
    templates:
      - "Museum of {theme}"
      - "{name} Park"
  # ... other categories
```

## Data Model

Each POI contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `poi_id` | string | Unique UUID identifier |
| `category` | string | POI category (attractions, hotels, etc.) |
| `name` | string | POI name |
| `lat` | float | Latitude (WGS84) |
| `lon` | float | Longitude (WGS84) |
| `address` | string | Street address |
| `capacity` | int | Maximum capacity (varies by category) |
| `rating` | float | Rating score (1.0-5.0) |
| `opening_hours` | string | Operating hours |
| `description` | string | Optional description |

## POI Categories

### Attractions
- Museums, parks, galleries, monuments
- Capacity: 100-2000 people
- Rating: 3.0-5.0
- Opening hours: 9:00-17:00, 10:00-18:00, etc.

### Hotels
- Hotels, inns, resorts, suites
- Capacity: 50-500 rooms
- Rating: 2.5-5.0
- Opening hours: 24/7

### Restaurants
- Restaurants, cafes, bars, diners
- Capacity: 20-200 people
- Rating: 2.0-5.0
- Opening hours: Various (6:00-22:00, 7:00-23:00, etc.)

### Venues
- Arenas, theaters, convention centers
- Capacity: 500-10000 people
- Opening hours: Event-based

## Integration with Knowledge Graph

The generated POI data is designed to integrate with the knowledge graph system described in the POC requirements:

- **Node Type**: POI nodes with `poi_id`, `category`, `name`, `geom` (lat/lon)
- **Relationships**: POIs can be linked to TicketEntry events
- **Raw Data**: Maintains raw coordinates without preprocessing
- **Schema Compliance**: Follows the defined data model structure

## Retry Configuration

The landmark fetcher includes robust retry logic to handle transient network errors:

### Retry Settings
```yaml
retry_config:
  max_retries: 3          # Maximum retry attempts
  initial_delay: 2        # Initial delay between retries (seconds)
  backoff_factor: 2       # Exponential backoff multiplier
  timeout: 30             # Request timeout (seconds)
```

### Error Handling
- **HTTP Errors**: Automatically retries on 408, 429, 500, 502, 503, 504 status codes
- **Network Timeouts**: Handles connection timeouts and gateway timeouts
- **Endpoint Fallback**: Tries multiple Overpass API endpoints if one fails:
  - `https://overpass-api.de/api/interpreter` (primary)
  - `https://overpass.kumi.systems/api/interpreter` (fallback)
  - `https://overpass.nchc.org.tw/api/interpreter` (fallback)

### Logging
- **Warning Level**: Logs retry attempts with delay information
- **Error Level**: Logs final failure after all retries exhausted
- **Debug Level**: Shows endpoint switching and successful connections

## Output Formats

### JSON Format
```json
[
  {
    "poi_id": "uuid-string",
    "category": "attractions",
    "name": "Museum of Modern Art",
    "lat": 40.7614,
    "lon": -73.9776,
    "address": "123 Main St",
    "capacity": 1500,
    "rating": 4.5,
    "opening_hours": "10:00-18:00"
  }
]
```

### CSV Format
The CSV output includes all fields with headers for easy import into databases or analysis tools.

## Development

### Adding New Categories

1. Add category configuration to `config.yaml`
2. Update `_generate_poi_properties()` method in `POIGenerator` class
3. Add appropriate name templates and properties

### Extending Properties

To add new POI properties:
1. Update the `POI` dataclass
2. Modify `_generate_poi_properties()` method
3. Update output methods if needed

## License

This generator is part of the DMSS NG2 project for tourism and event impact analysis.
