"""
POI Data Fetcher

Fetches real POI data from various internet sources including:
- OpenStreetMap (OSM) via Overpass API
- Google Places API
- Foursquare Places API
- OpenTripMap API
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
from poi_generator import POI


@dataclass
class POISource:
    """Configuration for a POI data source"""
    name: str
    api_url: str
    api_key: Optional[str] = None
    rate_limit: Optional[float] = None  # requests per second
    categories: List[str] = None


class POIFetcher:
    """Fetches POI data from various internet sources"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the POI fetcher with configuration"""
        self.config = self._load_config(config_path)
        self.sources = self.config.get('sources', {})
        self.setup_logging()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'sources': {
                'osm': {
                    'name': 'OpenStreetMap',
                    'api_url': 'https://overpass-api.de/api/interpreter',
                    'rate_limit': 1.0,  # 1 request per second
                    'categories': ['amenity', 'tourism', 'leisure', 'shop']
                },
                'opentripmap': {
                    'name': 'OpenTripMap',
                    'api_url': 'https://api.opentripmap.com/0.1/en/places',
                    'api_key': None,  # Will be loaded from environment
                    'rate_limit': 2.0,  # 2 requests per second
                    'categories': ['historic', 'cultural', 'natural', 'entertainment']
                }
            },
            'default_bounds': {
                'min_lat': 40.7,
                'max_lat': 40.8,
                'min_lon': -74.0,
                'max_lon': -73.9
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_from_osm(self, bounds: Dict, categories: List[str] = None) -> List[POI]:
        """Fetch POI data from OpenStreetMap using Overpass API"""
        self.logger.info("Fetching POI data from OpenStreetMap...")
        
        # Default categories if none specified
        if not categories:
            categories = ['amenity', 'tourism', 'leisure', 'shop']
        
        pois = []
        
        for category in categories:
            try:
                # Build Overpass query
                query = self._build_osm_query(bounds, category)
                
                # Make request
                response = requests.get(
                    self.sources['osm']['api_url'],
                    params={'data': query},
                    timeout=30
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                category_pois = self._parse_osm_response(data, category)
                pois.extend(category_pois)
                
                self.logger.info(f"Fetched {len(category_pois)} {category} POIs from OSM")
                
                # Rate limiting
                if self.sources['osm'].get('rate_limit'):
                    time.sleep(1.0 / self.sources['osm']['rate_limit'])
                    
            except Exception as e:
                self.logger.error(f"Error fetching {category} from OSM: {e}")
        
        return pois
    
    def _build_osm_query(self, bounds: Dict, category: str) -> str:
        """Build Overpass API query for a specific category"""
        query = f"""
        [out:json][timeout:25];
        (
          node["{category}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
          way["{category}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
          relation["{category}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
        );
        out body;
        >;
        out skel qt;
        """
        return query
    
    def _parse_osm_response(self, data: Dict, category: str) -> List[POI]:
        """Parse OSM response and convert to POI objects"""
        pois = []
        
        for element in data.get('elements', []):
            if element['type'] == 'node':
                tags = element.get('tags', {})
                
                # Extract POI information
                name = tags.get('name', tags.get('brand', f"Unknown {category}"))
                poi_type = tags.get(category, category)
                
                # Convert to our POI format
                poi = POI(
                    poi_id=f"osm_{element['id']}",
                    category=self._map_osm_category(category, poi_type),
                    name=name,
                    lat=element['lat'],
                    lon=element['lon'],
                    address=tags.get('addr:street', ''),
                    description=tags.get('description', ''),
                    opening_hours=tags.get('opening_hours', '')
                )
                pois.append(poi)
        
        return pois
    
    def _map_osm_category(self, osm_category: str, poi_type: str) -> str:
        """Map OSM categories to our standard categories"""
        category_mapping = {
            'amenity': {
                'restaurant': 'restaurants',
                'cafe': 'restaurants',
                'bar': 'restaurants',
                'pub': 'restaurants',
                'hotel': 'hotels',
                'hostel': 'hotels',
                'motel': 'hotels',
                'theatre': 'venues',
                'cinema': 'venues',
                'museum': 'attractions',
                'library': 'attractions',
                'school': 'attractions',
                'university': 'attractions',
                'hospital': 'attractions',
                'pharmacy': 'shopping',
                'bank': 'shopping',
                'post_office': 'shopping',
                'supermarket': 'shopping',
                'convenience': 'shopping',
                'fuel': 'transportation',
                'parking': 'transportation',
                'bus_station': 'transportation',
                'taxi': 'transportation'
            },
            'tourism': {
                'hotel': 'hotels',
                'hostel': 'hotels',
                'motel': 'hotels',
                'museum': 'attractions',
                'gallery': 'attractions',
                'attraction': 'attractions',
                'viewpoint': 'attractions',
                'information': 'attractions',
                'artwork': 'attractions',
                'theme_park': 'attractions',
                'zoo': 'attractions',
                'aquarium': 'attractions'
            },
            'leisure': {
                'park': 'attractions',
                'garden': 'attractions',
                'playground': 'attractions',
                'sports_centre': 'venues',
                'fitness_centre': 'venues',
                'stadium': 'venues',
                'swimming_pool': 'venues'
            },
            'shop': {
                'supermarket': 'shopping',
                'convenience': 'shopping',
                'department_store': 'shopping',
                'mall': 'shopping',
                'clothes': 'shopping',
                'jewelry': 'shopping',
                'electronics': 'shopping',
                'bookshop': 'shopping',
                'bakery': 'restaurants',
                'butcher': 'shopping',
                'greengrocer': 'shopping'
            }
        }
        
        return category_mapping.get(osm_category, {}).get(poi_type, 'attractions')
    
    def fetch_from_opentripmap(self, bounds: Dict, categories: List[str] = None) -> List[POI]:
        """Fetch POI data from OpenTripMap API"""
        self.logger.info("Fetching POI data from OpenTripMap...")
        
        api_key = self.sources['opentripmap'].get('api_key')
        if not api_key:
            self.logger.warning("OpenTripMap API key not configured, skipping...")
            return []
        
        if not categories:
            categories = ['historic', 'cultural', 'natural', 'entertainment']
        
        pois = []
        
        for category in categories:
            try:
                # Build request parameters
                params = {
                    'apikey': api_key,
                    'bbox': f"{bounds['min_lon']},{bounds['min_lat']},{bounds['max_lon']},{bounds['max_lat']}",
                    'kinds': category,
                    'limit': 50,
                    'format': 'json'
                }
                
                # Make request
                response = requests.get(
                    self.sources['opentripmap']['api_url'],
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                category_pois = self._parse_opentripmap_response(data, category)
                pois.extend(category_pois)
                
                self.logger.info(f"Fetched {len(category_pois)} {category} POIs from OpenTripMap")
                
                # Rate limiting
                if self.sources['opentripmap'].get('rate_limit'):
                    time.sleep(1.0 / self.sources['opentripmap']['rate_limit'])
                    
            except Exception as e:
                self.logger.error(f"Error fetching {category} from OpenTripMap: {e}")
        
        return pois
    
    def _parse_opentripmap_response(self, data: Dict, category: str) -> List[POI]:
        """Parse OpenTripMap response and convert to POI objects"""
        pois = []
        
        for feature in data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            if geometry.get('type') == 'Point':
                coordinates = geometry.get('coordinates', [])
                if len(coordinates) >= 2:
                    poi = POI(
                        poi_id=f"otm_{properties.get('xid', 'unknown')}",
                        category=self._map_opentripmap_category(category),
                        name=properties.get('name', f"Unknown {category}"),
                        lat=coordinates[1],
                        lon=coordinates[0],
                        address=properties.get('address', {}).get('road', ''),
                        description=properties.get('wikipedia_extracts', {}).get('text', ''),
                        rating=properties.get('rate', 0.0)
                    )
                    pois.append(poi)
        
        return pois
    
    def _map_opentripmap_category(self, category: str) -> str:
        """Map OpenTripMap categories to our standard categories"""
        mapping = {
            'historic': 'attractions',
            'cultural': 'attractions',
            'natural': 'attractions',
            'entertainment': 'venues',
            'architecture': 'attractions',
            'museums': 'attractions',
            'theatres_and_entertainments': 'venues',
            'sport': 'venues',
            'tourist_facilities': 'attractions',
            'amusements': 'venues',
            'urban_environment': 'attractions'
        }
        return mapping.get(category, 'attractions')
    
    def fetch_pois(self, bounds: Dict, sources: List[str] = None) -> List[POI]:
        """Fetch POI data from specified sources"""
        if not sources:
            sources = list(self.sources.keys())
        
        all_pois = []
        
        for source in sources:
            if source == 'osm':
                pois = self.fetch_from_osm(bounds)
                all_pois.extend(pois)
            elif source == 'opentripmap':
                pois = self.fetch_from_opentripmap(bounds)
                all_pois.extend(pois)
            else:
                self.logger.warning(f"Unknown source: {source}")
        
        # Remove duplicates based on coordinates and name
        unique_pois = self._remove_duplicates(all_pois)
        
        self.logger.info(f"Total unique POIs fetched: {len(unique_pois)}")
        return unique_pois
    
    def _remove_duplicates(self, pois: List[POI]) -> List[POI]:
        """Remove duplicate POIs based on coordinates and name"""
        seen = set()
        unique_pois = []
        
        for poi in pois:
            # Create a key based on coordinates and name
            key = (round(poi.lat, 6), round(poi.lon, 6), poi.name.lower())
            
            if key not in seen:
                seen.add(key)
                unique_pois.append(poi)
        
        return unique_pois
    
    def save_pois(self, pois: List[POI], output_dir: str, area_name: str):
        """Save fetched POIs to files"""
        output_path = Path(output_dir) / area_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save all POIs
        json_path = output_path / 'pois.json'
        csv_path = output_path / 'pois.csv'
        
        with open(json_path, 'w') as f:
            json.dump([asdict(poi) for poi in pois], f, indent=2)
        
        # Save CSV
        import csv
        with open(csv_path, 'w', newline='') as f:
            if pois:
                writer = csv.DictWriter(f, fieldnames=asdict(pois[0]).keys())
                writer.writeheader()
                for poi in pois:
                    writer.writerow(asdict(poi))
        
        # Save by category
        category_counts = {}
        for poi in pois:
            if poi.category not in category_counts:
                category_counts[poi.category] = []
            category_counts[poi.category].append(poi)
        
        for category, category_pois in category_counts.items():
            category_json_path = output_path / f'{category}.json'
            category_csv_path = output_path / f'{category}.csv'
            
            with open(category_json_path, 'w') as f:
                json.dump([asdict(poi) for poi in category_pois], f, indent=2)
            
            with open(category_csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(category_pois[0]).keys())
                writer.writeheader()
                for poi in category_pois:
                    writer.writerow(asdict(poi))
        
        self.logger.info(f"Saved {len(pois)} POIs to {output_path}")
        for category, count in category_counts.items():
            self.logger.info(f"  {category}: {count} POIs")


def main():
    """Main function to fetch POI data"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch POI data from internet sources')
    parser.add_argument('--config', help='Path to configuration YAML file')
    parser.add_argument('--area', required=True, help='Area name (e.g., new_york)')
    parser.add_argument('--bounds', nargs=4, type=float, 
                       metavar=('MIN_LAT', 'MAX_LAT', 'MIN_LON', 'MAX_LON'),
                       help='Geographic bounds')
    parser.add_argument('--sources', nargs='+', choices=['osm', 'opentripmap'],
                       default=['osm'], help='Data sources to use')
    parser.add_argument('--output-dir', default='../../data/generated',
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Set up bounds
    if args.bounds:
        bounds = {
            'min_lat': args.bounds[0],
            'max_lat': args.bounds[1],
            'min_lon': args.bounds[2],
            'max_lon': args.bounds[3]
        }
    else:
        # Default to NYC bounds
        bounds = {
            'min_lat': 40.7,
            'max_lat': 40.8,
            'min_lon': -74.0,
            'max_lon': -73.9
        }
    
    # Initialize fetcher
    fetcher = POIFetcher(args.config)
    
    # Fetch POIs
    pois = fetcher.fetch_pois(bounds, args.sources)
    
    # Save POIs
    fetcher.save_pois(pois, args.output_dir, args.area)
    
    print(f"Fetched {len(pois)} POIs for {args.area}")


if __name__ == "__main__":
    main()
