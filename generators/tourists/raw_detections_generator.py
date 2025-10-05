#!/usr/bin/env python3
"""
Raw Detections Generator

Generates raw detection data (position pings, ticket entries) for tourists
and saves to data/generated/{city}/raw/tourists directory.
"""

import json
import random
import uuid
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import yaml
from pathlib import Path


@dataclass
class RawPositionPing:
    """Raw position ping detection event"""
    event_id: str
    person_id: str
    position: str  # WKT POINT format
    event_timestamp: str
    accuracy: Optional[float] = None


@dataclass
class RawTicketEntry:
    """Raw ticket entry detection event"""
    event_id: str
    person_id: str
    poi_id: str
    entry_timestamp: str
    ticket_class: Optional[str] = None


class RawDetectionsGenerator:
    """Generates raw detection data for tourists"""
    
    def __init__(self, config_path: Optional[str] = None, poi_data_path: Optional[str] = None):
        """Initialize the raw detections generator"""
        self.config = self._load_config(config_path)
        self.poi_data = self._load_poi_data(poi_data_path)
        self.tourist_types = self.config.get('tourist_types', {})
        self.generation_config = self.config.get('generation', {})
        
        # Initialize random seed for reproducibility
        random.seed(42)
        
        # Load country and city data
        self._load_location_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config file {config_path}: {e}")
        
        # Default configuration for raw detections
        return {
            'tourist_types': {
                'cultural_tourist': {
                    'percentage': 25,
                    'preferences': ['museums', 'historic_sites'],
                    'demographics': {
                        'age_range': [25, 65],
                        'group_size': [1, 4],
                        'stay_duration': [3, 7],
                        'budget_level': 'medium_to_high'
                    }
                }
            },
            'generation': {
                'total_tourists': 100,
                'date_range': {
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31'
                },
                'detection_settings': {
                    'position_pings_per_day': [10, 50],
                    'ticket_entries_per_stay': [1, 10],
                    'gps_accuracy_range': [5.0, 50.0],
                    'nyc_bounds': {
                        'lat_min': 40.7,
                        'lat_max': 40.8,
                        'lon_min': -74.0,
                        'lon_max': -73.9
                    }
                }
            }
        }
    
    def _load_poi_data(self, poi_data_path: Optional[str]) -> Dict[str, List[Dict]]:
        """Load POI data from JSON files"""
        poi_data = {}
        
        if not poi_data_path:
            default_path = Path("data/generated/new_york")
            if default_path.exists():
                poi_data_path = str(default_path)
        
        if poi_data_path and os.path.exists(poi_data_path):
            poi_path = Path(poi_data_path)
            for json_file in poi_path.glob("*.json"):
                category = json_file.stem
                try:
                    with open(json_file, 'r') as f:
                        poi_data[category] = json.load(f)
                except Exception as e:
                    print(f"Error loading POI data from {json_file}: {e}")
        
        return poi_data
    
    def _load_location_data(self):
        """Load country and city data for origin generation"""
        self.countries = [
            "United States", "Canada", "United Kingdom", "Germany", "France", 
            "Italy", "Spain", "Japan", "China", "Australia", "Brazil", "Mexico",
            "India", "South Korea", "Netherlands", "Switzerland", "Sweden", "Norway"
        ]
        
        self.cities = {
            "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
            "United Kingdom": ["London", "Manchester", "Birmingham", "Liverpool", "Edinburgh"],
            "Germany": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt"],
            "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
            "Italy": ["Rome", "Milan", "Naples", "Turin", "Florence"],
            "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"],
            "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya"],
            "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu"],
            "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"]
        }
    
    def _generate_tourist_profiles(self, count: Optional[int] = None) -> List[Dict]:
        """Generate tourist profiles for raw detections"""
        if count is None:
            count = self.generation_config.get('total_tourists', 100)
        
        tourists = []
        start_date = datetime.strptime(self.generation_config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.generation_config['date_range']['end_date'], '%Y-%m-%d')
        
        for tourist_type, config in self.tourist_types.items():
            type_count = int(count * config['percentage'] / 100)
            
            for _ in range(type_count):
                # Generate tourist profile
                arrival_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
                stay_duration = random.randint(*config['demographics']['stay_duration'])
                departure_date = arrival_date + timedelta(days=stay_duration)
                
                tourist = {
                    'person_id': f"person_{uuid.uuid4().hex[:8]}",
                    'tourist_type': tourist_type,
                    'age': random.randint(*config['demographics']['age_range']),
                    'group_size': random.randint(*config['demographics']['group_size']),
                    'stay_duration': stay_duration,
                    'budget_level': config['demographics']['budget_level'],
                    'origin_country': random.choice(self.countries),
                    'origin_city': random.choice(self.cities.get(random.choice(self.countries), ["Unknown"])),
                    'arrival_date': arrival_date.strftime('%Y-%m-%d'),
                    'departure_date': departure_date.strftime('%Y-%m-%d')
                }
                tourists.append(tourist)
        
        return tourists
    
    def _generate_raw_position_pings(self, tourists: List[Dict]) -> List[RawPositionPing]:
        """Generate raw position ping detections"""
        position_pings = []
        detection_settings = self.generation_config.get('detection_settings', {})
        bounds = detection_settings.get('nyc_bounds', {})
        accuracy_range = detection_settings.get('gps_accuracy_range', [5.0, 50.0])
        pings_per_day_range = detection_settings.get('position_pings_per_day', [10, 50])
        
        for tourist in tourists:
            arrival_date = datetime.strptime(tourist['arrival_date'], '%Y-%m-%d')
            departure_date = datetime.strptime(tourist['departure_date'], '%Y-%m-%d')
            
            # Generate position pings throughout the tourist's stay
            pings_per_day = random.randint(*pings_per_day_range)
            total_days = (departure_date - arrival_date).days
            
            for day in range(total_days):
                current_date = arrival_date + timedelta(days=day)
                
                for ping in range(pings_per_day):
                    # Generate random time during the day
                    hour = random.randint(6, 22)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    ping_time = current_date.replace(hour=hour, minute=minute, second=second)
                    
                    # Generate GPS position within NYC bounds
                    lat = random.uniform(bounds.get('lat_min', 40.7), bounds.get('lat_max', 40.8))
                    lon = random.uniform(bounds.get('lon_min', -74.0), bounds.get('lon_max', -73.9))
                    
                    position = f"POINT({lon} {lat})"
                    accuracy = random.uniform(*accuracy_range)
                    
                    position_ping = RawPositionPing(
                        event_id=f"ping_{uuid.uuid4().hex[:8]}",
                        person_id=tourist['person_id'],
                        position=position,
                        event_timestamp=ping_time.isoformat(),
                        accuracy=accuracy
                    )
                    position_pings.append(position_ping)
        
        return position_pings
    
    def _generate_raw_ticket_entries(self, tourists: List[Dict]) -> List[RawTicketEntry]:
        """Generate raw ticket entry detections"""
        ticket_entries = []
        detection_settings = self.generation_config.get('detection_settings', {})
        entries_per_stay_range = detection_settings.get('ticket_entries_per_stay', [1, 10])
        
        # Collect all available POIs
        available_pois = []
        for category_pois in self.poi_data.values():
            available_pois.extend(category_pois)
        
        if not available_pois:
            print("Warning: No POI data available for ticket entries")
            return ticket_entries
        
        for tourist in tourists:
            arrival_date = datetime.strptime(tourist['arrival_date'], '%Y-%m-%d')
            departure_date = datetime.strptime(tourist['departure_date'], '%Y-%m-%d')
            
            # Determine number of POI visits
            total_entries = random.randint(*entries_per_stay_range)
            
            # Distribute visits across the stay duration
            stay_days = (departure_date - arrival_date).days
            if stay_days <= 0:
                continue
            
            for _ in range(total_entries):
                # Select random POI
                poi = random.choice(available_pois)
                
                # Generate random visit date
                visit_day = arrival_date + timedelta(days=random.randint(0, stay_days - 1))
                
                # Generate entry time
                hour = random.randint(9, 18)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                entry_timestamp = visit_day.replace(hour=hour, minute=minute, second=second)
                
                # Generate ticket class based on tourist characteristics
                ticket_class = self._generate_ticket_class(tourist)
                
                ticket_entry = RawTicketEntry(
                    event_id=f"entry_{uuid.uuid4().hex[:8]}",
                    person_id=tourist['person_id'],
                    poi_id=poi['poi_id'],
                    entry_timestamp=entry_timestamp.isoformat(),
                    ticket_class=ticket_class
                )
                ticket_entries.append(ticket_entry)
        
        return ticket_entries
    
    def _generate_ticket_class(self, tourist: Dict) -> str:
        """Generate ticket class based on tourist characteristics"""
        age = tourist['age']
        budget_level = tourist['budget_level']
        
        if age < 18:
            return 'child' if age < 12 else 'student'
        elif age >= 65:
            return 'senior'
        elif budget_level == 'high':
            return random.choice(['adult', 'vip', 'premium'])
        else:
            return random.choice(['adult', 'student', 'senior'])
    
    def generate_raw_detections_data(self, city: str = "new_york", output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Generate raw detection data and save to files"""
        if output_dir is None:
            output_dir = f"data/generated/{city}/raw/tourists"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate tourist profiles
        print("Generating tourist profiles...")
        tourists = self._generate_tourist_profiles()
        
        # Generate raw position pings
        print("Generating raw position pings...")
        position_pings = self._generate_raw_position_pings(tourists)
        
        # Generate raw ticket entries
        print("Generating raw ticket entries...")
        ticket_entries = self._generate_raw_ticket_entries(tourists)
        
        # Create output data structure
        output_data = {
            'tourists': tourists,
            'position_pings': [asdict(ping) for ping in position_pings],
            'ticket_entries': [asdict(entry) for entry in ticket_entries],
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_tourists': len(tourists),
                'total_position_pings': len(position_pings),
                'total_ticket_entries': len(ticket_entries),
                'city': city,
                'data_type': 'raw_detections',
                'ontology_version': '1.0',
                'ontology_name': 'People Detections Ontology - Raw Data',
                'config_used': self.config
            }
        }
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'raw_detections_data.json')
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save as CSV files
        csv_tourists_path = os.path.join(output_dir, 'tourists.csv')
        with open(csv_tourists_path, 'w', newline='') as f:
            if tourists:
                writer = csv.DictWriter(f, fieldnames=tourists[0].keys())
                writer.writeheader()
                for tourist in tourists:
                    writer.writerow(tourist)
        
        csv_position_pings_path = os.path.join(output_dir, 'position_pings.csv')
        with open(csv_position_pings_path, 'w', newline='') as f:
            if position_pings:
                writer = csv.DictWriter(f, fieldnames=asdict(position_pings[0]).keys())
                writer.writeheader()
                for ping in position_pings:
                    writer.writerow(asdict(ping))
        
        csv_ticket_entries_path = os.path.join(output_dir, 'ticket_entries.csv')
        with open(csv_ticket_entries_path, 'w', newline='') as f:
            if ticket_entries:
                writer = csv.DictWriter(f, fieldnames=asdict(ticket_entries[0]).keys())
                writer.writeheader()
                for entry in ticket_entries:
                    writer.writerow(asdict(entry))
        
        print(f"Generated {len(tourists)} tourists, {len(position_pings)} position pings, and {len(ticket_entries)} ticket entries")
        print(f"Raw detection data saved to {output_dir}")
        
        return output_data


def main():
    """Main function to run the raw detections generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate raw detection data')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--poi-data', type=str, help='Path to POI data directory')
    parser.add_argument('--city', type=str, default='new_york', help='City name')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--count', type=int, help='Number of tourists to generate')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = RawDetectionsGenerator(
        config_path=args.config,
        poi_data_path=args.poi_data
    )
    
    # Override tourist count if specified
    if args.count:
        generator.generation_config['total_tourists'] = args.count
    
    # Generate data
    output_data = generator.generate_raw_detections_data(
        city=args.city,
        output_dir=args.output
    )
    
    print("Raw detection data generation completed successfully!")


if __name__ == "__main__":
    main()
