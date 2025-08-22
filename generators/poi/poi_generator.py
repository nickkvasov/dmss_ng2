"""
POI (Points of Interest) Generator

Generates synthetic POI data for tourism and event impact analysis.
Supports attractions, hotels, restaurants, and other venue types.
"""

import json
import random
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import yaml


@dataclass
class POI:
    """Point of Interest data structure"""
    poi_id: str
    category: str
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    capacity: Optional[int] = None
    rating: Optional[float] = None
    opening_hours: Optional[str] = None
    description: Optional[str] = None


class POIGenerator:
    """Generates synthetic POI data for tourism and event analysis"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the POI generator with configuration"""
        self.config = self._load_config(config_path)
        self.poi_categories = self.config.get('poi_categories', {})
        self.city_bounds = self.config.get('city_bounds', {})
        self._load_poi_templates()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except FileNotFoundError:
                print(f"Config file {config_path} not found, using defaults")
        
        # Default configuration
        return {
            'city_bounds': {
                'min_lat': 40.7,
                'max_lat': 40.8,
                'min_lon': -74.0,
                'max_lon': -73.9,
                'name': 'New York City'
            },
            'poi_categories': {
                'attractions': {
                    'count': 50,
                    'templates': [
                        'Museum of {theme}',
                        '{name} Park',
                        '{name} Gallery',
                        'Historic {name}',
                        '{name} Monument',
                        'Science Center',
                        'Art Museum',
                        'Natural History Museum',
                        'Botanical Gardens',
                        'Zoo'
                    ]
                },
                'hotels': {
                    'count': 30,
                    'templates': [
                        '{name} Hotel',
                        '{name} Inn',
                        '{name} Resort',
                        '{name} Suites',
                        'Grand {name} Hotel',
                        '{name} Plaza',
                        '{name} Tower'
                    ]
                },
                'restaurants': {
                    'count': 80,
                    'templates': [
                        '{name} Restaurant',
                        '{name} Bistro',
                        '{name} Cafe',
                        '{name} Grill',
                        '{name} Kitchen',
                        '{name} Diner',
                        '{name} Bar & Grill',
                        '{name} Tavern'
                    ]
                },
                'venues': {
                    'count': 20,
                    'templates': [
                        '{name} Arena',
                        '{name} Stadium',
                        '{name} Theater',
                        '{name} Concert Hall',
                        '{name} Convention Center',
                        '{name} Auditorium',
                        '{name} Amphitheater'
                    ]
                }
            }
        }
    
    def _load_poi_templates(self):
        """Load POI name templates and themes"""
        self.themes = [
            'Modern Art', 'Contemporary', 'Classical', 'Aviation', 'Maritime',
            'Technology', 'History', 'Culture', 'Nature', 'Science',
            'Children', 'Photography', 'Sculpture', 'Design', 'Architecture'
        ]
        
        self.names = [
            'Central', 'Riverside', 'Downtown', 'Uptown', 'Midtown',
            'Brooklyn', 'Manhattan', 'Queens', 'Bronx', 'Staten',
            'Hudson', 'East', 'West', 'North', 'South',
            'Liberty', 'Freedom', 'Unity', 'Harmony', 'Serenity',
            'Golden', 'Silver', 'Platinum', 'Diamond', 'Emerald',
            'Royal', 'Imperial', 'Majestic', 'Grand', 'Noble'
        ]
    
    def _generate_coordinates(self) -> Tuple[float, float]:
        """Generate random coordinates within city bounds"""
        lat = random.uniform(
            self.city_bounds['min_lat'],
            self.city_bounds['max_lat']
        )
        lon = random.uniform(
            self.city_bounds['min_lon'],
            self.city_bounds['max_lon']
        )
        return lat, lon
    
    def _generate_name(self, category: str) -> str:
        """Generate a POI name based on category templates"""
        templates = self.poi_categories[category]['templates']
        template = random.choice(templates)
        
        if '{theme}' in template:
            return template.format(theme=random.choice(self.themes))
        elif '{name}' in template:
            return template.format(name=random.choice(self.names))
        else:
            return template
    
    def _generate_poi_properties(self, category: str) -> Dict:
        """Generate additional POI properties based on category"""
        properties = {}
        
        if category == 'hotels':
            properties['capacity'] = random.randint(50, 500)
            properties['rating'] = round(random.uniform(2.5, 5.0), 1)
            properties['opening_hours'] = '24/7'
        elif category == 'restaurants':
            properties['capacity'] = random.randint(20, 200)
            properties['rating'] = round(random.uniform(2.0, 5.0), 1)
            properties['opening_hours'] = random.choice([
                '6:00-22:00', '7:00-23:00', '8:00-21:00', '11:00-24:00'
            ])
        elif category == 'attractions':
            properties['capacity'] = random.randint(100, 2000)
            properties['rating'] = round(random.uniform(3.0, 5.0), 1)
            properties['opening_hours'] = random.choice([
                '9:00-17:00', '10:00-18:00', '9:00-21:00', '10:00-22:00'
            ])
        elif category == 'venues':
            properties['capacity'] = random.randint(500, 10000)
            properties['opening_hours'] = 'Event-based'
        
        # Generate address
        street_numbers = [str(i) for i in range(1, 1000)]
        street_names = [
            'Main St', 'Broadway', '5th Ave', 'Park Ave', 'Madison Ave',
            'Lexington Ave', '3rd Ave', '2nd Ave', '1st Ave', 'West End Ave',
            'Riverside Dr', 'Central Park West', 'Columbus Ave', 'Amsterdam Ave'
        ]
        
        properties['address'] = f"{random.choice(street_numbers)} {random.choice(street_names)}"
        
        return properties
    
    def generate_poi(self, category: str) -> POI:
        """Generate a single POI for the specified category"""
        poi_id = str(uuid.uuid4())
        name = self._generate_name(category)
        lat, lon = self._generate_coordinates()
        properties = self._generate_poi_properties(category)
        
        return POI(
            poi_id=poi_id,
            category=category,
            name=name,
            lat=lat,
            lon=lon,
            **properties
        )
    
    def generate_pois(self, category: Optional[str] = None) -> List[POI]:
        """Generate POIs for all categories or a specific category"""
        pois = []
        
        if category:
            if category not in self.poi_categories:
                raise ValueError(f"Unknown category: {category}")
            
            count = self.poi_categories[category]['count']
            for _ in range(count):
                pois.append(self.generate_poi(category))
        else:
            for category_name, config in self.poi_categories.items():
                count = config['count']
                for _ in range(count):
                    pois.append(self.generate_poi(category_name))
        
        return pois
    
    def save_to_json(self, pois: List[POI], output_path: str):
        """Save POIs to JSON file"""
        poi_data = [asdict(poi) for poi in pois]
        
        with open(output_path, 'w') as f:
            json.dump(poi_data, f, indent=2)
        
        print(f"Saved {len(pois)} POIs to {output_path}")
    
    def save_to_csv(self, pois: List[POI], output_path: str):
        """Save POIs to CSV file"""
        import csv
        
        with open(output_path, 'w', newline='') as f:
            if not pois:
                return
            
            writer = csv.DictWriter(f, fieldnames=asdict(pois[0]).keys())
            writer.writeheader()
            
            for poi in pois:
                writer.writerow(asdict(poi))
        
        print(f"Saved {len(pois)} POIs to {output_path}")


def main():
    """Main function to generate POI data"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic POI data')
    parser.add_argument('--config', help='Path to configuration YAML file')
    parser.add_argument('--category', help='Generate POIs for specific category only')
    parser.add_argument('--output-json', default='pois.json', help='Output JSON file path')
    parser.add_argument('--output-csv', default='pois.csv', help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = POIGenerator(args.config)
    
    # Generate POIs
    pois = generator.generate_pois(args.category)
    
    # Save outputs
    generator.save_to_json(pois, args.output_json)
    generator.save_to_csv(pois, args.output_csv)
    
    # Print summary
    print(f"\nGenerated {len(pois)} POIs:")
    category_counts = {}
    for poi in pois:
        category_counts[poi.category] = category_counts.get(poi.category, 0) + 1
    
    for category, count in category_counts.items():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
