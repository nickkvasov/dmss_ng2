#!/usr/bin/env python3
"""
Group Behavior Generator

Enhanced generator that properly uses group_size to create realistic group behavior
including group formation, coordinated movements, and shared activities.
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
class GroupMember:
    """Individual member within a group"""
    person_id: str
    tourist_type: str
    age: int
    role: str  # leader, follower, child, etc.
    is_group_leader: bool = False


@dataclass
class TouristGroup:
    """A group of tourists traveling together"""
    group_id: str
    members: List[GroupMember]
    group_size: int
    group_type: str  # family, friends, business, solo
    stay_duration: int
    budget_level: str
    origin_country: str
    origin_city: str
    arrival_date: str
    departure_date: str


@dataclass
class GroupPositionPing:
    """Position ping with group context"""
    event_id: str
    person_id: str
    group_id: str
    position: str  # WKT POINT format
    event_timestamp: str
    accuracy: Optional[float] = None
    group_activity: Optional[str] = None  # walking_together, exploring, resting, etc.


@dataclass
class GroupTicketEntry:
    """Ticket entry with group context"""
    event_id: str
    person_id: str
    group_id: str
    poi_id: str
    entry_timestamp: str
    ticket_class: Optional[str] = None
    group_size_entering: Optional[int] = None  # How many from the group entered together


class GroupBehaviorGenerator:
    """Generates tourist data with realistic group behavior"""
    
    def __init__(self, config_path: Optional[str] = None, poi_data_path: Optional[str] = None):
        """Initialize the group behavior generator"""
        self.config = self._load_config(config_path)
        self.poi_data = self._load_poi_data(poi_data_path)
        self.tourist_types = self.config.get('tourist_types', {})
        self.generation_config = self.config.get('generation', {})
        
        # Initialize random seed for reproducibility
        random.seed(42)
        
        # Load country and city data
        self._load_location_data()
        
        # Group behavior patterns
        self._load_group_patterns()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config file {config_path}: {e}")
        
        # Default configuration with group behavior
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
    
    def _load_group_patterns(self):
        """Load group behavior patterns"""
        self.group_patterns = {
            'family': {
                'roles': ['parent', 'child', 'teenager', 'grandparent'],
                'activities': ['walking_together', 'waiting_for_children', 'family_photos', 'educational_activities'],
                'movement_pattern': 'coordinated',  # Family moves together
                'separation_probability': 0.1  # Low chance of family members separating
            },
            'friends': {
                'roles': ['friend', 'travel_buddy', 'colleague'],
                'activities': ['walking_together', 'exploring', 'taking_photos', 'dining'],
                'movement_pattern': 'semi_coordinated',  # Friends may split up occasionally
                'separation_probability': 0.3
            },
            'business': {
                'roles': ['colleague', 'client', 'partner'],
                'activities': ['walking_together', 'business_discussion', 'networking'],
                'movement_pattern': 'coordinated',
                'separation_probability': 0.05
            },
            'solo': {
                'roles': ['solo_traveler'],
                'activities': ['exploring', 'taking_photos', 'reading_maps'],
                'movement_pattern': 'independent',
                'separation_probability': 1.0
            }
        }
    
    def _generate_tourist_groups(self, count: Optional[int] = None) -> List[TouristGroup]:
        """Generate tourist groups with realistic group behavior"""
        if count is None:
            count = self.generation_config.get('total_tourists', 100)
        
        groups = []
        start_date = datetime.strptime(self.generation_config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.generation_config['date_range']['end_date'], '%Y-%m-%d')
        
        for tourist_type, config in self.tourist_types.items():
            type_count = int(count * config['percentage'] / 100)
            
            for _ in range(type_count):
                # Generate group size based on tourist type
                group_size = random.randint(*config['demographics']['group_size'])
                
                # Determine group type based on size and tourist type
                group_type = self._determine_group_type(group_size, tourist_type)
                
                # Generate arrival and departure dates
                arrival_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
                stay_duration = random.randint(*config['demographics']['stay_duration'])
                departure_date = arrival_date + timedelta(days=stay_duration)
                
                # Generate group members
                members = self._generate_group_members(group_size, tourist_type, group_type)
                
                # Create group
                group = TouristGroup(
                    group_id=f"group_{uuid.uuid4().hex[:8]}",
                    members=members,
                    group_size=group_size,
                    group_type=group_type,
                    stay_duration=stay_duration,
                    budget_level=config['demographics']['budget_level'],
                    origin_country=random.choice(self.countries),
                    origin_city=random.choice(self.cities.get(random.choice(self.countries), ["Unknown"])),
                    arrival_date=arrival_date.strftime('%Y-%m-%d'),
                    departure_date=departure_date.strftime('%Y-%m-%d')
                )
                groups.append(group)
        
        return groups
    
    def _determine_group_type(self, group_size: int, tourist_type: str) -> str:
        """Determine group type based on size and tourist type"""
        if group_size == 1:
            return 'solo'
        elif group_size == 2:
            if tourist_type == 'business_tourist':
                return 'business'
            else:
                return random.choice(['friends', 'family'])
        elif group_size >= 3:
            if tourist_type == 'family_tourist':
                return 'family'
            elif tourist_type == 'business_tourist':
                return 'business'
            else:
                return random.choice(['family', 'friends'])
        else:
            return 'solo'
    
    def _generate_group_members(self, group_size: int, tourist_type: str, group_type: str) -> List[GroupMember]:
        """Generate individual members for a group"""
        members = []
        patterns = self.group_patterns.get(group_type, self.group_patterns['solo'])
        
        for i in range(group_size):
            # Determine role based on group type
            if group_type == 'family':
                if group_size >= 4:
                    roles = ['parent', 'parent', 'child', 'child']
                elif group_size == 3:
                    roles = ['parent', 'parent', 'child']
                else:
                    roles = ['parent', 'child']
                role = roles[i] if i < len(roles) else 'child'
            elif group_type == 'friends':
                role = random.choice(patterns['roles'])
            elif group_type == 'business':
                role = random.choice(patterns['roles'])
            else:  # solo
                role = 'solo_traveler'
            
            # Generate age based on role and tourist type
            age = self._generate_age_for_role(role, tourist_type)
            
            # Determine if this person is the group leader
            is_leader = (i == 0) or (group_type == 'family' and role == 'parent')
            
            member = GroupMember(
                person_id=f"person_{uuid.uuid4().hex[:8]}",
                tourist_type=tourist_type,
                age=age,
                role=role,
                is_group_leader=is_leader
            )
            members.append(member)
        
        return members
    
    def _generate_age_for_role(self, role: str, tourist_type: str) -> int:
        """Generate appropriate age based on role and tourist type"""
        if role == 'child':
            return random.randint(5, 12)
        elif role == 'teenager':
            return random.randint(13, 17)
        elif role == 'parent':
            return random.randint(25, 50)
        elif role == 'grandparent':
            return random.randint(60, 75)
        elif role == 'solo_traveler':
            return random.randint(18, 65)
        else:  # friends, colleagues, etc.
            return random.randint(20, 55)
    
    def _generate_group_position_pings(self, groups: List[TouristGroup]) -> List[GroupPositionPing]:
        """Generate position pings with group behavior"""
        position_pings = []
        
        for group in groups:
            patterns = self.group_patterns.get(group.group_type, self.group_patterns['solo'])
            separation_prob = patterns['separation_probability']
            
            # Generate position pings throughout the group's stay
            arrival_date = datetime.strptime(group.arrival_date, '%Y-%m-%d')
            departure_date = datetime.strptime(group.departure_date, '%Y-%m-%d')
            
            # Generate 10-50 position pings per day per group
            pings_per_day = random.randint(10, 50)
            total_days = (departure_date - arrival_date).days
            
            for day in range(total_days):
                current_date = arrival_date + timedelta(days=day)
                
                for ping in range(pings_per_day):
                    # Generate random time during the day
                    hour = random.randint(6, 22)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    ping_time = current_date.replace(hour=hour, minute=minute, second=second)
                    
                    # Determine if group members are together or separated
                    members_together = random.random() > separation_prob
                    
                    if members_together:
                        # Generate a single position for the group
                        base_lat = random.uniform(40.7, 40.8)
                        base_lon = random.uniform(-74.0, -73.9)
                        
                        # Generate positions for each member near the base position
                        for member in group.members:
                            # Add small random offset for group members (within 100m)
                            lat_offset = random.uniform(-0.001, 0.001)  # ~100m
                            lon_offset = random.uniform(-0.001, 0.001)
                            
                            lat = base_lat + lat_offset
                            lon = base_lon + lon_offset
                            
                            position = f"POINT({lon} {lat})"
                            accuracy = random.uniform(5.0, 50.0)
                            
                            # Determine group activity
                            activity = random.choice(patterns['activities'])
                            
                            position_ping = GroupPositionPing(
                                event_id=f"ping_{uuid.uuid4().hex[:8]}",
                                person_id=member.person_id,
                                group_id=group.group_id,
                                position=position,
                                event_timestamp=ping_time.isoformat(),
                                accuracy=accuracy,
                                group_activity=activity
                            )
                            position_pings.append(position_ping)
                    else:
                        # Generate separate positions for each member
                        for member in group.members:
                            lat = random.uniform(40.7, 40.8)
                            lon = random.uniform(-74.0, -73.9)
                            
                            position = f"POINT({lon} {lat})"
                            accuracy = random.uniform(5.0, 50.0)
                            
                            position_ping = GroupPositionPing(
                                event_id=f"ping_{uuid.uuid4().hex[:8]}",
                                person_id=member.person_id,
                                group_id=group.group_id,
                                position=position,
                                event_timestamp=ping_time.isoformat(),
                                accuracy=accuracy,
                                group_activity="separated"
                            )
                            position_pings.append(position_ping)
        
        return position_pings
    
    def _generate_group_ticket_entries(self, groups: List[TouristGroup]) -> List[GroupTicketEntry]:
        """Generate ticket entries with group behavior"""
        ticket_entries = []
        
        for group in groups:
            # Determine number of POIs to visit based on group size and tourist type
            total_pois = self._calculate_total_pois_for_group(group)
            
            # Generate visit dates within group's stay period
            arrival_date = datetime.strptime(group.arrival_date, '%Y-%m-%d')
            departure_date = datetime.strptime(group.departure_date, '%Y-%m-%d')
            
            # Distribute POI visits across the stay duration
            visit_dates = self._distribute_visits(arrival_date, departure_date, total_pois)
            
            # Select POIs based on group preferences
            selected_pois = self._select_pois_for_group(group, total_pois)
            
            for visit_date, poi in zip(visit_dates, selected_pois):
                # Determine if entire group enters together or separately
                group_enters_together = random.random() > 0.2  # 80% chance group enters together
                
                if group_enters_together:
                    # Generate entry time based on group type
                    entry_time = self._generate_entry_time_for_group(group)
                    entry_timestamp = visit_date.replace(
                        hour=entry_time.hour, 
                        minute=entry_time.minute, 
                        second=random.randint(0, 59)
                    )
                    
                    # Generate ticket entries for all group members
                    for member in group.members:
                        ticket_class = self._generate_ticket_class_for_member(member, group)
                        
                        ticket_entry = GroupTicketEntry(
                            event_id=f"entry_{uuid.uuid4().hex[:8]}",
                            person_id=member.person_id,
                            group_id=group.group_id,
                            poi_id=poi['poi_id'],
                            entry_timestamp=entry_timestamp.isoformat(),
                            ticket_class=ticket_class,
                            group_size_entering=group.group_size
                        )
                        ticket_entries.append(ticket_entry)
                else:
                    # Generate separate entry times for group members
                    for member in group.members:
                        entry_time = self._generate_entry_time_for_group(group)
                        entry_timestamp = visit_date.replace(
                            hour=entry_time.hour, 
                            minute=entry_time.minute, 
                            second=random.randint(0, 59)
                        )
                        
                        # Add some time variation for separate entries
                        entry_timestamp = entry_timestamp + timedelta(minutes=random.randint(-30, 30))
                        
                        ticket_class = self._generate_ticket_class_for_member(member, group)
                        
                        ticket_entry = GroupTicketEntry(
                            event_id=f"entry_{uuid.uuid4().hex[:8]}",
                            person_id=member.person_id,
                            group_id=group.group_id,
                            poi_id=poi['poi_id'],
                            entry_timestamp=entry_timestamp.isoformat(),
                            ticket_class=ticket_class,
                            group_size_entering=1
                        )
                        ticket_entries.append(ticket_entry)
        
        return ticket_entries
    
    def _calculate_total_pois_for_group(self, group: TouristGroup) -> int:
        """Calculate total number of POIs to visit based on group characteristics"""
        base_pois_per_day = {
            'cultural_tourist': 3,
            'leisure_tourist': 2,
            'adventure_tourist': 6,
            'family_tourist': 2,
            'business_tourist': 1
        }
        
        tourist_type = group.members[0].tourist_type
        base_pois = base_pois_per_day.get(tourist_type, 2)
        
        # Adjust based on group size (larger groups visit fewer POIs per day)
        group_size_factor = max(0.5, 1.0 - (group.group_size - 1) * 0.1)
        
        return min(int(base_pois * group.group_size * group_size_factor * group.stay_duration), 20)
    
    def _distribute_visits(self, arrival_date: datetime, departure_date: datetime, total_pois: int) -> List[datetime]:
        """Distribute POI visits across the stay duration"""
        stay_days = (departure_date - arrival_date).days
        if stay_days <= 0:
            return [arrival_date] * total_pois
        
        visit_dates = []
        for _ in range(total_pois):
            visit_day = arrival_date + timedelta(days=random.randint(0, stay_days - 1))
            visit_dates.append(visit_day)
        
        visit_dates.sort()
        return visit_dates
    
    def _select_pois_for_group(self, group: TouristGroup, total_pois: int) -> List[Dict]:
        """Select POIs based on group preferences"""
        available_pois = []
        
        # Get preferences from tourist type config
        tourist_type = group.members[0].tourist_type
        config = self.tourist_types.get(tourist_type, {})
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
    
    def _generate_entry_time_for_group(self, group: TouristGroup) -> datetime:
        """Generate entry time based on group type"""
        time_patterns = {
            'cultural_tourist': [9, 12],      # Morning
            'leisure_tourist': [12, 17],      # Afternoon
            'adventure_tourist': [6, 10],     # Early morning
            'family_tourist': [10, 14],       # Mid-morning
            'business_tourist': [17, 22]      # Evening
        }
        
        tourist_type = group.members[0].tourist_type
        start_hour, end_hour = time_patterns.get(tourist_type, [9, 17])
        hour = random.randint(start_hour, end_hour)
        minute = random.randint(0, 59)
        
        return datetime.now().replace(hour=hour, minute=minute)
    
    def _generate_ticket_class_for_member(self, member: GroupMember, group: TouristGroup) -> str:
        """Generate ticket class based on member role and group type"""
        if member.role == 'child':
            return 'child'
        elif member.role == 'teenager':
            return 'student'
        elif member.role == 'grandparent':
            return 'senior'
        elif group.budget_level == 'high':
            return random.choice(['adult', 'vip', 'premium'])
        else:
            return random.choice(['adult', 'student', 'senior'])
    
    def generate_group_behavior_data(self, city: str = "new_york", output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Generate all group behavior data and save to files"""
        if output_dir is None:
            output_dir = f"data/generated/{city}/group_behavior"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate tourist groups
        print("Generating tourist groups...")
        groups = self._generate_tourist_groups()
        
        # Generate group position pings
        print("Generating group position pings...")
        position_pings = self._generate_group_position_pings(groups)
        
        # Generate group ticket entries
        print("Generating group ticket entries...")
        ticket_entries = self._generate_group_ticket_entries(groups)
        
        # Create output data structure
        output_data = {
            'groups': [asdict(group) for group in groups],
            'position_pings': [asdict(ping) for ping in position_pings],
            'ticket_entries': [asdict(entry) for entry in ticket_entries],
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_groups': len(groups),
                'total_members': sum(len(group.members) for group in groups),
                'total_position_pings': len(position_pings),
                'total_ticket_entries': len(ticket_entries),
                'city': city,
                'ontology_version': '1.0',
                'ontology_name': 'People Detections Ontology with Group Behavior',
                'config_used': self.config
            }
        }
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'group_behavior_data.json')
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save as CSV files
        csv_groups_path = os.path.join(output_dir, 'groups.csv')
        with open(csv_groups_path, 'w', newline='') as f:
            if groups:
                # Flatten group data for CSV
                group_rows = []
                for group in groups:
                    for member in group.members:
                        row = {
                            'group_id': group.group_id,
                            'person_id': member.person_id,
                            'group_size': group.group_size,
                            'group_type': group.group_type,
                            'tourist_type': member.tourist_type,
                            'age': member.age,
                            'role': member.role,
                            'is_group_leader': member.is_group_leader,
                            'stay_duration': group.stay_duration,
                            'budget_level': group.budget_level,
                            'origin_country': group.origin_country,
                            'origin_city': group.origin_city,
                            'arrival_date': group.arrival_date,
                            'departure_date': group.departure_date
                        }
                        group_rows.append(row)
                
                if group_rows:
                    writer = csv.DictWriter(f, fieldnames=group_rows[0].keys())
                    writer.writeheader()
                    for row in group_rows:
                        writer.writerow(row)
        
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
        
        print(f"Generated {len(groups)} groups, {len(position_pings)} position pings, and {len(ticket_entries)} ticket entries")
        print(f"Data saved to {output_dir}")
        
        return output_data


def main():
    """Main function to run the group behavior generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate group behavior data')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--poi-data', type=str, help='Path to POI data directory')
    parser.add_argument('--city', type=str, default='new_york', help='City name')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--count', type=int, help='Number of tourists to generate')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = GroupBehaviorGenerator(
        config_path=args.config,
        poi_data_path=args.poi_data
    )
    
    # Override tourist count if specified
    if args.count:
        generator.generation_config['total_tourists'] = args.count
    
    # Generate data
    output_data = generator.generate_group_behavior_data(
        city=args.city,
        output_dir=args.output
    )
    
    print("Group behavior data generation completed successfully!")


if __name__ == "__main__":
    main()
