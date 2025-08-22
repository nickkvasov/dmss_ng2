"""
Landmark Fetcher

Fetches only exceptional landmarks and tourist attractions from various sources.
Filters out generic POIs to focus on significant destinations.
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
from functools import wraps


def retry_on_failure(max_retries=3, delay=2, backoff_factor=2, exceptions=(requests.RequestException,)):
    """
    Retry decorator for handling transient network errors
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logging.getLogger(__name__).warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logging.getLogger(__name__).error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


@dataclass
class Landmark:
    """Landmark data structure"""
    poi_id: str
    category: str
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    opening_hours: Optional[str] = None
    landmark_type: Optional[str] = None  # museum, monument, park, etc.


class LandmarkFetcher:
    """Fetches exceptional landmarks and tourist attractions"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the landmark fetcher"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Define landmark categories and their OSM tags
        self.landmark_categories = {
            'museums': {
                'osm_tags': ['museum'],
                'min_rating': 4.0,
                'max_count': 50
            },
            'monuments': {
                'osm_tags': ['memorial', 'monument', 'statue'],
                'min_rating': 4.0,
                'max_count': 30
            },
            'parks': {
                'osm_tags': ['leisure=park', 'landuse=recreation_ground', 'garden', 'botanical_garden'],
                'min_rating': 4.0,
                'max_count': 40
            },
            'historic_sites': {
                'osm_tags': ['historic', 'castle', 'palace', 'ruins'],
                'min_rating': 4.0,
                'max_count': 25
            },
            'theaters': {
                'osm_tags': ['theatre', 'cinema', 'concert_hall'],
                'min_rating': 4.0,
                'max_count': 20
            },
            'landmarks': {
                'osm_tags': ['landmark', 'tower', 'bridge'],
                'min_rating': 4.0,
                'max_count': 15
            }
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        return {
            'osm_api_urls': [
                'https://overpass-api.de/api/interpreter',
                'https://overpass.kumi.systems/api/interpreter',
                'https://overpass.nchc.org.tw/api/interpreter'
            ],
            'rate_limit': 1.0,
            'max_landmarks_per_category': 50,
            'min_rating_threshold': 4.0,
            'retry_config': {
                'max_retries': 3,
                'initial_delay': 2,
                'backoff_factor': 2,
                'timeout': 30
            }
        }
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    @retry_on_failure(max_retries=3, delay=2, backoff_factor=2)
    def _make_request_with_retry(self, params: Dict = None, timeout: int = 30) -> requests.Response:
        """
        Make HTTP request with automatic retry logic and endpoint fallback
        
        Args:
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            requests.Response object
            
        Raises:
            requests.RequestException: If all retry attempts fail on all endpoints
        """
        urls = self.config.get('osm_api_urls', ['https://overpass-api.de/api/interpreter'])
        last_exception = None
        
        for url in urls:
            try:
                self.logger.debug(f"Trying endpoint: {url}")
                response = requests.get(url, params=params, timeout=timeout)
                
                # Handle specific HTTP errors that should trigger retries
                if response.status_code in [408, 429, 500, 502, 503, 504]:
                    raise requests.RequestException(f"HTTP {response.status_code}: {response.reason}")
                
                response.raise_for_status()
                self.logger.debug(f"Successfully used endpoint: {url}")
                return response
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Failed to use endpoint {url}: {e}")
                continue
        
        # If we get here, all endpoints failed
        raise last_exception or requests.RequestException("All endpoints failed")
    
    def fetch_landmarks_from_osm(self, bounds: Dict, categories: List[str] = None) -> List[Landmark]:
        """Fetch landmarks from OpenStreetMap with filtering"""
        self.logger.info("Fetching landmarks from OpenStreetMap...")
        
        if not categories:
            categories = list(self.landmark_categories.keys())
        
        all_landmarks = []
        
        for category in categories:
            if category not in self.landmark_categories:
                continue
                
            category_config = self.landmark_categories[category]
            landmarks = self._fetch_category_landmarks(bounds, category, category_config)
            all_landmarks.extend(landmarks)
            
            self.logger.info(f"Fetched {len(landmarks)} {category} landmarks")
            
            # Rate limiting
            time.sleep(1.0 / self.config['rate_limit'])
        
        # Filter and sort by quality
        filtered_landmarks = self._filter_landmarks(all_landmarks)
        
        self.logger.info(f"Total landmarks after filtering: {len(filtered_landmarks)}")
        return filtered_landmarks
    
    def _fetch_category_landmarks(self, bounds: Dict, category: str, config: Dict) -> List[Landmark]:
        """Fetch landmarks for a specific category"""
        landmarks = []
        
        for osm_tag in config['osm_tags']:
            try:
                # Build query for specific landmark types
                query = self._build_landmark_query(bounds, osm_tag)
                
                # Use retry-enabled request method
                timeout = self.config.get('retry_config', {}).get('timeout', 30)
                response = self._make_request_with_retry(
                    params={'data': query},
                    timeout=timeout
                )
                
                data = response.json()
                category_landmarks = self._parse_landmark_response(data, category, osm_tag)
                landmarks.extend(category_landmarks)
                
            except Exception as e:
                self.logger.error(f"Error fetching {osm_tag} landmarks: {e}")
                # Continue with next tag even if one fails
                continue
        
        return landmarks
    
    def _build_landmark_query(self, bounds: Dict, osm_tag: str) -> str:
        """Build Overpass query for landmarks with opening hours"""
        # Handle key=value format for OSM tags
        if '=' in osm_tag:
            key, value = osm_tag.split('=', 1)
            query = f"""
            [out:json][timeout:25];
            (
              node["{key}"="{value}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
              way["{key}"="{value}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
              relation["{key}"="{value}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
            );
            out body;
            >;
            out skel qt;
            """
        else:
            # Handle simple tag format
            query = f"""
            [out:json][timeout:25];
            (
              node["{osm_tag}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
              way["{osm_tag}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
              relation["{osm_tag}"]({bounds['min_lat']},{bounds['min_lon']},{bounds['max_lat']},{bounds['max_lon']});
            );
            out body;
            >;
            out skel qt;
            """
        return query
    
    def _parse_landmark_response(self, data: Dict, category: str, osm_tag: str) -> List[Landmark]:
        """Parse OSM response and convert to Landmark objects"""
        landmarks = []
        
        for element in data.get('elements', []):
            if element['type'] == 'node':
                tags = element.get('tags', {})
                
                # Extract landmark information
                name = tags.get('name', tags.get('brand', ''))
                
                # Skip if no proper name
                if not name or name.lower() in ['unknown', 'unknown amenity', '']:
                    continue
                
                # Check for quality indicators
                if not self._is_quality_landmark(tags):
                    continue
                
                # Extract opening hours from various possible OSM tags
                opening_hours = self._extract_opening_hours(tags)
                
                landmark = Landmark(
                    poi_id=f"landmark_{element['id']}",
                    category=category,
                    name=name,
                    lat=element['lat'],
                    lon=element['lon'],
                    address=tags.get('addr:street', ''),
                    description=tags.get('description', ''),
                    opening_hours=opening_hours,
                    landmark_type=osm_tag
                )
                landmarks.append(landmark)
        
        return landmarks
    
    def _is_quality_landmark(self, tags: Dict) -> bool:
        """Check if a POI is a quality landmark worth including"""
        # Must have a proper name
        name = tags.get('name', '').lower()
        if not name or name in ['unknown', 'unknown amenity', '']:
            return False
        
        # Check for quality indicators
        quality_indicators = [
            'tourism', 'historic', 'landmark', 'museum', 'gallery',
            'theatre', 'cinema', 'concert_hall', 'memorial', 'monument',
            'castle', 'palace', 'park', 'garden', 'botanical_garden'
        ]
        
        # Special handling for parks - they might not have tourism tags
        is_park = any(tag in tags for tag in ['leisure', 'landuse']) and tags.get('leisure') == 'park'
        
        # Must have at least one quality indicator OR be a park
        has_quality = any(indicator in tags for indicator in quality_indicators) or is_park
        
        # Skip generic amenities
        generic_amenities = [
            'parking', 'fuel', 'bank', 'post_office', 'pharmacy',
            'supermarket', 'convenience', 'restaurant', 'cafe', 'bar',
            'hotel', 'hostel', 'school', 'university', 'hospital'
        ]
        
        is_generic = any(amenity in tags.get('amenity', '') for amenity in generic_amenities)
        
        return has_quality and not is_generic
    
    def _filter_landmarks(self, landmarks: List[Landmark]) -> List[Landmark]:
        """Filter landmarks by quality and limit counts"""
        # Sort by category and limit per category
        filtered = []
        category_counts = {}
        
        for landmark in landmarks:
            category = landmark.category
            if category not in category_counts:
                category_counts[category] = 0
            
            max_count = self.landmark_categories.get(category, {}).get('max_count', 50)
            
            if category_counts[category] < max_count:
                filtered.append(landmark)
                category_counts[category] += 1
        
        # Sort by category for better organization
        filtered.sort(key=lambda x: x.category)
        
        return filtered
    
    def _extract_opening_hours(self, tags: Dict) -> Optional[str]:
        """
        Extract opening hours from OSM tags
        
        OSM uses various tags for opening hours:
        - opening_hours: Standard opening hours format
        - hours: Alternative format
        - access: Access restrictions
        - seasonal: Seasonal opening information
        """
        # Try standard opening_hours tag first
        opening_hours = tags.get('opening_hours', '')
        if opening_hours and opening_hours.lower() not in ['no', 'closed', '']:
            return opening_hours
        
        # Try hours tag
        hours = tags.get('hours', '')
        if hours and hours.lower() not in ['no', 'closed', '']:
            return hours
        
        # Check for access restrictions that might indicate opening status
        access = tags.get('access', '')
        if access in ['private', 'no']:
            return 'Private access'
        
        # Check for seasonal information
        seasonal = tags.get('seasonal', '')
        if seasonal:
            return f'Seasonal: {seasonal}'
        
        # For museums and cultural sites, provide default hours if none specified
        if any(tag in tags for tag in ['museum', 'gallery', 'theatre', 'cinema']):
            return 'Typically 10:00-18:00 (check for specific hours)'
        
        # For parks and outdoor sites
        if any(tag in tags for tag in ['park', 'garden', 'memorial', 'monument']) or tags.get('leisure') == 'park':
            return 'Open 24/7'
        
        return None
    
    def fetch_landmarks(self, bounds: Dict, categories: List[str] = None) -> List[Landmark]:
        """Fetch landmarks with filtering"""
        landmarks = self.fetch_landmarks_from_osm(bounds, categories)
        return landmarks
    
    def save_landmarks(self, landmarks: List[Landmark], output_dir: str, area_name: str):
        """Save landmarks to files"""
        output_path = Path(output_dir) / area_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save all landmarks
        json_path = output_path / 'landmarks.json'
        csv_path = output_path / 'landmarks.csv'
        
        with open(json_path, 'w') as f:
            json.dump([asdict(landmark) for landmark in landmarks], f, indent=2)
        
        # Save CSV
        import csv
        with open(csv_path, 'w', newline='') as f:
            if landmarks:
                writer = csv.DictWriter(f, fieldnames=asdict(landmarks[0]).keys())
                writer.writeheader()
                for landmark in landmarks:
                    writer.writerow(asdict(landmark))
        
        # Save by category
        category_counts = {}
        for landmark in landmarks:
            if landmark.category not in category_counts:
                category_counts[landmark.category] = []
            category_counts[landmark.category].append(landmark)
        
        for category, category_landmarks in category_counts.items():
            category_json_path = output_path / f'{category}.json'
            category_csv_path = output_path / f'{category}.csv'
            
            with open(category_json_path, 'w') as f:
                json.dump([asdict(landmark) for landmark in category_landmarks], f, indent=2)
            
            with open(category_csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(category_landmarks[0]).keys())
                writer.writeheader()
                for landmark in category_landmarks:
                    writer.writerow(asdict(landmark))
        
        self.logger.info(f"Saved {len(landmarks)} landmarks to {output_path}")
        for category, count in category_counts.items():
            self.logger.info(f"  {category}: {count} landmarks")


def main():
    """Main function to fetch landmarks"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch exceptional landmarks')
    parser.add_argument('--area', required=True, help='Area name (e.g., new_york)')
    parser.add_argument('--bounds', nargs=4, type=float, 
                       metavar=('MIN_LAT', 'MAX_LAT', 'MIN_LON', 'MAX_LON'),
                       help='Geographic bounds')
    parser.add_argument('--categories', nargs='+', 
                       choices=['museums', 'monuments', 'parks', 'historic_sites', 'theaters', 'landmarks'],
                       help='Landmark categories to fetch')
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
    fetcher = LandmarkFetcher()
    
    # Fetch landmarks
    landmarks = fetcher.fetch_landmarks(bounds, args.categories)
    
    # Save landmarks
    fetcher.save_landmarks(landmarks, args.output_dir, args.area)
    
    print(f"Fetched {len(landmarks)} exceptional landmarks for {args.area}")


if __name__ == "__main__":
    main()
