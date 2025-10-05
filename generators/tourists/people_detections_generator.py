#!/usr/bin/env python3
"""
People Detections Generator

Generates tourist data in accordance with the people_detections_ontology.yaml format.
This generator creates POSITION_PING and TICKET_ENTRY events that can be used
for tourism and event impact analysis.
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
import math


@dataclass
class PositionPing:
    """Position ping event conforming to people_detections_ontology.yaml"""
    event_id: str
    person_id: str
    position: str  # WKT POINT format
    event_timestamp: str
    accuracy: Optional[float] = None


@dataclass
class TicketEntry:
    """Ticket entry event conforming to people_detections_ontology.yaml"""
    event_id: str
    person_id: str
    poi_id: str
    entry_timestamp: str
    ticket_class: Optional[str] = None


@dataclass
class Person:
    """Person entity (referenced by the ontology)"""
    person_id: str
    tourist_type: str
    age: int
    group_size: int
    stay_duration: int
    budget_level: str
    origin_country: str
    origin_city: str
    arrival_date: str
    departure_date: str


class PeopleDetectionsGenerator:
    """Generates people detection data conforming to the people_detections_ontology.yaml"""
    
    def __init__(self, config_path: Optional[str] = None, poi_data_path: Optional[str] = None):
        """Initialize the people detections generator"""
        self.config = self._load_config(config_path)
        self.poi_data = self._load_poi_data(poi_data_path)
        self.tourist_types = self.config.get('tourist_types', {})
        self.generation_config = self.config.get('generation', {})
        
        # Initialize random seed for reproducibility
        random.seed(42)
        
        # Load country and city data for origin generation
        self._load_location_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config file {config_path}: {e}")
        
        # Default configuration
        return {
            'tourist_types': {
                'cultural_tourist': {
                    'percentage': 25,
                    'preferences': ['museums', 'historic_sites'],
                    'behavior_patterns': ['spends_2_4_hours_per_poi', 'visits_3_5_pois_per_day'],
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
                }
            }
        }
    
    def _load_poi_data(self, poi_data_path: Optional[str]) -> Dict[str, List[Dict]]:
        """Load POI data from JSON files"""
        poi_data = {}
        
        if not poi_data_path:
            # Try to find POI data in the default location
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
        # Simplified location data
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
    
    def _generate_person_profiles(self, count: Optional[int] = None) -> List[Person]:
        """Generate person profiles based on configured types and percentages"""
        if count is None:
            count = self.generation_config.get('total_tourists', 100)
        
        persons = []
        start_date = datetime.strptime(self.generation_config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.generation_config['date_range']['end_date'], '%Y-%m-%d')
        
        for tourist_type, config in self.tourist_types.items():
            type_count = int(count * config['percentage'] / 100)
            
            for _ in range(type_count):
                # Generate arrival and departure dates
                arrival_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
                stay_duration = random.randint(*config['demographics']['stay_duration'])
                departure_date = arrival_date + timedelta(days=stay_duration)
                
                # Generate person profile
                person = Person(
                    person_id=f"person_{uuid.uuid4().hex[:8]}",
                    tourist_type=tourist_type,
                    age=random.randint(*config['demographics']['age_range']),
                    group_size=random.randint(*config['demographics']['group_size']),
                    stay_duration=stay_duration,
                    budget_level=config['demographics']['budget_level'],
                    origin_country=random.choice(self.countries),
                    origin_city=random.choice(self.cities.get(random.choice(self.countries), ["Unknown"])),
                    arrival_date=arrival_date.strftime('%Y-%m-%d'),
                    departure_date=departure_date.strftime('%Y-%m-%d')
                )
                persons.append(person)
        
        # Shuffle to randomize order
        random.shuffle(persons)
        return persons
    
    def _generate_position_pings(self, persons: List[Person]) -> List[PositionPing]:
        """Generate position ping events for persons"""
        position_pings = []
        
        for person in persons:
            # Generate position pings throughout the person's stay
            arrival_date = datetime.strptime(person.arrival_date, '%Y-%m-%d')
            departure_date = datetime.strptime(person.departure_date, '%Y-%m-%d')
            
            # Generate 10-50 position pings per day
            pings_per_day = random.randint(10, 50)
            total_days = (departure_date - arrival_date).days
            
            for day in range(total_days):
                current_date = arrival_date + timedelta(days=day)
                
                for ping in range(pings_per_day):
                    # Generate random time during the day
                    hour = random.randint(6, 22)  # 6 AM to 10 PM
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    ping_time = current_date.replace(hour=hour, minute=minute, second=second)
                    
                    # Generate random position within NYC bounds
                    lat = random.uniform(40.7, 40.8)
                    lon = random.uniform(-74.0, -73.9)
                    
                    # Format as WKT POINT
                    position = f"POINT({lon} {lat})"
                    
                    # Generate accuracy (5-50 meters)
                    accuracy = random.uniform(5.0, 50.0)
                    
                    position_ping = PositionPing(
                        event_id=f"ping_{uuid.uuid4().hex[:8]}",
                        person_id=person.person_id,
                        position=position,
                        event_timestamp=ping_time.isoformat(),
                        accuracy=accuracy
                    )
                    position_pings.append(position_ping)
        
        return position_pings
    
    def _generate_ticket_entries(self, persons: List[Person]) -> List[TicketEntry]:
        """Generate ticket entry events for persons visiting POIs"""
        ticket_entries = []
        
        for person in persons:
            # Determine number of POIs to visit based on stay duration and tourist type
            total_pois = self._calculate_total_pois(person)
            
            # Generate visit dates within person's stay period
            arrival_date = datetime.strptime(person.arrival_date, '%Y-%m-%d')
            departure_date = datetime.strptime(person.departure_date, '%Y-%m-%d')
            
            # Distribute POI visits across the stay duration
            visit_dates = self._distribute_visits(arrival_date, departure_date, total_pois)
            
            # Select POIs based on person preferences
            selected_pois = self._select_pois_for_person(person, total_pois)
            
            for visit_date, poi in zip(visit_dates, selected_pois):
                # Generate entry time based on tourist type
                entry_time = self._generate_entry_time(person)
                entry_timestamp = visit_date.replace(
                    hour=entry_time.hour, 
                    minute=entry_time.minute, 
                    second=random.randint(0, 59)
                )
                
                # Generate ticket class based on tourist type and budget
                ticket_class = self._generate_ticket_class(person)
                
                ticket_entry = TicketEntry(
                    event_id=f"entry_{uuid.uuid4().hex[:8]}",
                    person_id=person.person_id,
                    poi_id=poi['poi_id'],
                    entry_timestamp=entry_timestamp.isoformat(),
                    ticket_class=ticket_class
                )
                ticket_entries.append(ticket_entry)
        
        return ticket_entries
    
    def _calculate_total_pois(self, person: Person) -> int:
        """Calculate total number of POIs to visit based on person type and stay duration"""
        base_pois_per_day = {
            'cultural_tourist': 3,
            'leisure_tourist': 2,
            'adventure_tourist': 6,
            'family_tourist': 2,
            'business_tourist': 1
        }
        
        base_pois = base_pois_per_day.get(person.tourist_type, 2)
        return min(base_pois * person.stay_duration, 20)  # Cap at 20 POIs
    
    def _distribute_visits(self, arrival_date: datetime, departure_date: datetime, total_pois: int) -> List[datetime]:
        """Distribute POI visits across the stay duration"""
        stay_days = (departure_date - arrival_date).days
        if stay_days <= 0:
            return [arrival_date] * total_pois
        
        # Distribute visits across available days
        visit_dates = []
        for _ in range(total_pois):
            visit_day = arrival_date + timedelta(days=random.randint(0, stay_days - 1))
            visit_dates.append(visit_day)
        
        # Sort by date
        visit_dates.sort()
        return visit_dates
    
    def _select_pois_for_person(self, person: Person, total_pois: int) -> List[Dict]:
        """Select POIs based on person preferences"""
        available_pois = []
        
        # Get preferences from tourist type config
        config = self.tourist_types.get(person.tourist_type, {})
        preferences = config.get('preferences', ['landmarks'])
        
        # Collect POIs from preferred categories
        for category in preferences:
            if category in self.poi_data:
                available_pois.extend(self.poi_data[category])
        
        if not available_pois:
            # Fallback to all available POIs
            for category_pois in self.poi_data.values():
                available_pois.extend(category_pois)
        
        # Sample POIs based on preferences and availability
        if len(available_pois) <= total_pois:
            return available_pois
        else:
            return random.sample(available_pois, total_pois)
    
    def _generate_entry_time(self, person: Person) -> datetime:
        """Generate entry time based on person type"""
        time_patterns = {
            'cultural_tourist': [9, 12],      # Morning
            'leisure_tourist': [12, 17],      # Afternoon
            'adventure_tourist': [6, 10],     # Early morning
            'family_tourist': [10, 14],       # Mid-morning
            'business_tourist': [17, 22]      # Evening
        }
        
        start_hour, end_hour = time_patterns.get(person.tourist_type, [9, 17])
        hour = random.randint(start_hour, end_hour)
        minute = random.randint(0, 59)
        
        return datetime.now().replace(hour=hour, minute=minute)
    
    def _generate_ticket_class(self, person: Person) -> str:
        """Generate ticket class based on person type and budget"""
        ticket_classes = {
            'cultural_tourist': ['adult', 'senior', 'student'],
            'leisure_tourist': ['adult', 'family', 'group'],
            'adventure_tourist': ['adult', 'student', 'youth'],
            'family_tourist': ['family', 'child', 'adult'],
            'business_tourist': ['adult', 'vip', 'business']
        }
        
        available_classes = ticket_classes.get(person.tourist_type, ['adult'])
        
        # Adjust based on budget level
        if person.budget_level == 'high':
            available_classes.extend(['vip', 'premium'])
        elif person.budget_level == 'low_to_medium':
            available_classes.extend(['student', 'youth'])
        
        return random.choice(available_classes)
    
    def generate_people_detections_data(self, city: str = "new_york", output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Generate all people detection data and save to files"""
        if output_dir is None:
            output_dir = f"data/generated/{city}/people_detections"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate person profiles
        print("Generating person profiles...")
        persons = self._generate_person_profiles()
        
        # Generate position pings
        print("Generating position pings...")
        position_pings = self._generate_position_pings(persons)
        
        # Generate ticket entries
        print("Generating ticket entries...")
        ticket_entries = self._generate_ticket_entries(persons)
        
        # Create output data structure conforming to ontology
        output_data = {
            'persons': [asdict(person) for person in persons],
            'position_pings': [asdict(ping) for ping in position_pings],
            'ticket_entries': [asdict(entry) for entry in ticket_entries],
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_persons': len(persons),
                'total_position_pings': len(position_pings),
                'total_ticket_entries': len(ticket_entries),
                'city': city,
                'ontology_version': '1.0',
                'ontology_name': 'People Detections Ontology',
                'config_used': self.config
            }
        }
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'people_detections_data.json')
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save as CSV files
        csv_persons_path = os.path.join(output_dir, 'persons.csv')
        with open(csv_persons_path, 'w', newline='') as f:
            if persons:
                writer = csv.DictWriter(f, fieldnames=asdict(persons[0]).keys())
                writer.writeheader()
                for person in persons:
                    writer.writerow(asdict(person))
        
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
        
        print(f"Generated {len(persons)} persons, {len(position_pings)} position pings, and {len(ticket_entries)} ticket entries")
        print(f"Data saved to {output_dir}")
        
        return output_data


def main():
    """Main function to run the people detections generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate people detection data conforming to ontology')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--poi-data', type=str, help='Path to POI data directory')
    parser.add_argument('--city', type=str, default='new_york', help='City name')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--count', type=int, help='Number of persons to generate')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = PeopleDetectionsGenerator(
        config_path=args.config,
        poi_data_path=args.poi_data
    )
    
    # Override person count if specified
    if args.count:
        generator.generation_config['total_tourists'] = args.count
    
    # Generate data
    output_data = generator.generate_people_detections_data(
        city=args.city,
        output_dir=args.output
    )
    
    print("People detection data generation completed successfully!")


if __name__ == "__main__":
    main()
