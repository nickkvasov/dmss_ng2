#!/usr/bin/env python3
"""
Scene Behavior Generator

Generates behavioral and scene setup data for tourists including group structures,
behavioral patterns, preferences, and scene configurations.
Saves to data/generated/{city}/scene/tourists/setup directory.
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
class SceneTourist:
    """Tourist profile for scene/behavioral data"""
    person_id: str
    tourist_type: str
    age: int
    group_size: int
    group_id: Optional[str] = None
    role: Optional[str] = None
    is_group_leader: bool = False
    stay_duration: int = 0
    budget_level: str = ""
    origin_country: str = ""
    origin_city: str = ""
    arrival_date: str = ""
    departure_date: str = ""
    preferences: List[str] = None
    behavior_patterns: List[str] = None


@dataclass
class TouristGroup:
    """Tourist group structure for scene data"""
    group_id: str
    group_type: str  # family, friends, business, solo
    group_size: int
    members: List[str]  # List of person_ids
    stay_duration: int
    budget_level: str
    origin_country: str
    origin_city: str
    arrival_date: str
    departure_date: str
    group_behavior_patterns: Dict[str, Any] = None


@dataclass
class BehavioralPattern:
    """Behavioral pattern configuration"""
    pattern_id: str
    pattern_type: str  # movement, activity, social, etc.
    description: str
    parameters: Dict[str, Any]
    probability: float
    conditions: Dict[str, Any] = None


@dataclass
class SceneConfiguration:
    """Scene configuration for tourist behavior"""
    scene_id: str
    scene_name: str
    city: str
    date_range: Dict[str, str]
    total_tourists: int
    tourist_types_distribution: Dict[str, float]
    group_size_distribution: Dict[int, float]
    behavioral_patterns: List[BehavioralPattern]
    poi_categories: List[str]
    weather_conditions: Dict[str, Any] = None
    special_events: List[str] = None


class SceneBehaviorGenerator:
    """Generates scene and behavioral data for tourists"""
    
    def __init__(self, config_path: Optional[str] = None, poi_data_path: Optional[str] = None):
        """Initialize the scene behavior generator"""
        self.config = self._load_config(config_path)
        self.poi_data = self._load_poi_data(poi_data_path)
        self.tourist_types = self.config.get('tourist_types', {})
        self.generation_config = self.config.get('generation', {})
        
        # Initialize random seed for reproducibility
        random.seed(42)
        
        # Load country and city data
        self._load_location_data()
        
        # Load behavioral patterns
        self._load_behavioral_patterns()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config file {config_path}: {e}")
        
        # Default configuration for scene/behavioral data
        return {
            'tourist_types': {
                'cultural_tourist': {
                    'percentage': 25,
                    'preferences': ['museums', 'historic_sites', 'art_galleries'],
                    'behavior_patterns': ['spends_2_4_hours_per_poi', 'visits_3_5_pois_per_day', 'photography_focused'],
                    'demographics': {
                        'age_range': [25, 65],
                        'group_size': [1, 4],
                        'stay_duration': [3, 7],
                        'budget_level': 'medium_to_high'
                    }
                },
                'leisure_tourist': {
                    'percentage': 30,
                    'preferences': ['parks', 'shopping', 'restaurants'],
                    'behavior_patterns': ['relaxed_pace', 'visits_2_3_pois_per_day', 'dining_focused'],
                    'demographics': {
                        'age_range': [20, 60],
                        'group_size': [1, 6],
                        'stay_duration': [2, 5],
                        'budget_level': 'medium'
                    }
                },
                'adventure_tourist': {
                    'percentage': 15,
                    'preferences': ['outdoor_activities', 'adventure_sports', 'exploration'],
                    'behavior_patterns': ['fast_pace', 'visits_6_8_pois_per_day', 'outdoor_focused'],
                    'demographics': {
                        'age_range': [18, 45],
                        'group_size': [1, 3],
                        'stay_duration': [1, 4],
                        'budget_level': 'low_to_medium'
                    }
                },
                'family_tourist': {
                    'percentage': 20,
                    'preferences': ['family_attractions', 'parks', 'museums'],
                    'behavior_patterns': ['child_friendly_pace', 'visits_2_4_pois_per_day', 'family_activities'],
                    'demographics': {
                        'age_range': [25, 50],
                        'group_size': [3, 8],
                        'stay_duration': [4, 10],
                        'budget_level': 'medium_to_high'
                    }
                },
                'business_tourist': {
                    'percentage': 10,
                    'preferences': ['business_districts', 'conference_centers', 'fine_dining'],
                    'behavior_patterns': ['efficient_pace', 'visits_1_2_pois_per_day', 'business_focused'],
                    'demographics': {
                        'age_range': [30, 60],
                        'group_size': [1, 3],
                        'stay_duration': [1, 3],
                        'budget_level': 'high'
                    }
                }
            },
            'generation': {
                'total_tourists': 100,
                'date_range': {
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31'
                },
                'scene_settings': {
                    'weather_conditions': ['sunny', 'cloudy', 'rainy', 'snowy'],
                    'special_events': ['festivals', 'conferences', 'sports_events', 'holidays'],
                    'poi_categories': ['museums', 'historic_sites', 'parks', 'landmarks', 'theaters', 'monuments']
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
    
    def _load_behavioral_patterns(self):
        """Load behavioral patterns for different tourist types"""
        self.behavioral_patterns = {
            'movement_patterns': {
                'fast_pace': {
                    'description': 'Fast walking pace, covers more ground quickly',
                    'parameters': {'speed_multiplier': 1.5, 'rest_frequency': 0.3},
                    'probability': 0.2
                },
                'normal_pace': {
                    'description': 'Normal walking pace, balanced exploration',
                    'parameters': {'speed_multiplier': 1.0, 'rest_frequency': 0.5},
                    'probability': 0.6
                },
                'slow_pace': {
                    'description': 'Slow walking pace, detailed observation',
                    'parameters': {'speed_multiplier': 0.7, 'rest_frequency': 0.7},
                    'probability': 0.2
                }
            },
            'activity_patterns': {
                'photography_focused': {
                    'description': 'Frequently stops for photos',
                    'parameters': {'photo_frequency': 0.8, 'stop_duration': 120},
                    'probability': 0.4
                },
                'dining_focused': {
                    'description': 'Prioritizes dining experiences',
                    'parameters': {'meal_frequency': 3, 'dining_duration': 90},
                    'probability': 0.3
                },
                'shopping_focused': {
                    'description': 'Frequently visits shops and markets',
                    'parameters': {'shopping_frequency': 0.6, 'shop_duration': 45},
                    'probability': 0.3
                }
            },
            'social_patterns': {
                'group_coordinated': {
                    'description': 'Moves and acts as a coordinated group',
                    'parameters': {'separation_probability': 0.1, 'group_activity_frequency': 0.8},
                    'probability': 0.7
                },
                'independent': {
                    'description': 'Acts independently within group',
                    'parameters': {'separation_probability': 0.4, 'group_activity_frequency': 0.3},
                    'probability': 0.3
                }
            }
        }
    
    def _generate_scene_tourists(self, count: Optional[int] = None) -> List[SceneTourist]:
        """Generate scene tourists with behavioral patterns"""
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
                
                # Generate group size
                group_size = random.randint(*config['demographics']['group_size'])
                
                # Generate preferences and behavior patterns
                preferences = config.get('preferences', []).copy()
                behavior_patterns = config.get('behavior_patterns', []).copy()
                
                # Add random behavioral patterns
                for pattern_category, patterns in self.behavioral_patterns.items():
                    for pattern_name, pattern_data in patterns.items():
                        if random.random() < pattern_data['probability']:
                            behavior_patterns.append(f"{pattern_category}_{pattern_name}")
                
                tourist = SceneTourist(
                    person_id=f"person_{uuid.uuid4().hex[:8]}",
                    tourist_type=tourist_type,
                    age=random.randint(*config['demographics']['age_range']),
                    group_size=group_size,
                    stay_duration=stay_duration,
                    budget_level=config['demographics']['budget_level'],
                    origin_country=random.choice(self.countries),
                    origin_city=random.choice(self.cities.get(random.choice(self.countries), ["Unknown"])),
                    arrival_date=arrival_date.strftime('%Y-%m-%d'),
                    departure_date=departure_date.strftime('%Y-%m-%d'),
                    preferences=preferences,
                    behavior_patterns=behavior_patterns
                )
                tourists.append(tourist)
        
        return tourists
    
    def _generate_tourist_groups(self, tourists: List[SceneTourist]) -> List[TouristGroup]:
        """Generate tourist groups from individual tourists"""
        groups = []
        tourists_by_group_size = {}
        
        # Group tourists by their group size
        for tourist in tourists:
            group_size = tourist.group_size
            if group_size not in tourists_by_group_size:
                tourists_by_group_size[group_size] = []
            tourists_by_group_size[group_size].append(tourist)
        
        # Create groups
        for group_size, group_tourists in tourists_by_group_size.items():
            if group_size == 1:
                # Solo tourists
                for tourist in group_tourists:
                    group = TouristGroup(
                        group_id=f"group_{uuid.uuid4().hex[:8]}",
                        group_type='solo',
                        group_size=1,
                        members=[tourist.person_id],
                        stay_duration=tourist.stay_duration,
                        budget_level=tourist.budget_level,
                        origin_country=tourist.origin_country,
                        origin_city=tourist.origin_city,
                        arrival_date=tourist.arrival_date,
                        departure_date=tourist.departure_date,
                        group_behavior_patterns={
                            'movement': 'independent',
                            'coordination': 'none',
                            'separation_probability': 1.0
                        }
                    )
                    groups.append(group)
                    tourist.group_id = group.group_id
                    tourist.role = 'solo_traveler'
                    tourist.is_group_leader = True
            else:
                # Group tourists
                for i in range(0, len(group_tourists), group_size):
                    group_members = group_tourists[i:i + group_size]
                    if len(group_members) == group_size:
                        # Determine group type
                        tourist_types = [t.tourist_type for t in group_members]
                        group_type = self._determine_group_type(group_size, tourist_types[0])
                        
                        # Generate group behavior patterns
                        group_behavior_patterns = self._generate_group_behavior_patterns(group_type, group_size)
                        
                        group = TouristGroup(
                            group_id=f"group_{uuid.uuid4().hex[:8]}",
                            group_type=group_type,
                            group_size=group_size,
                            members=[t.person_id for t in group_members],
                            stay_duration=group_members[0].stay_duration,
                            budget_level=group_members[0].budget_level,
                            origin_country=group_members[0].origin_country,
                            origin_city=group_members[0].origin_city,
                            arrival_date=group_members[0].arrival_date,
                            departure_date=group_members[0].departure_date,
                            group_behavior_patterns=group_behavior_patterns
                        )
                        groups.append(group)
                        
                        # Update tourist group information
                        for j, tourist in enumerate(group_members):
                            tourist.group_id = group.group_id
                            tourist.role = self._assign_role(group_type, j, group_size)
                            tourist.is_group_leader = (j == 0)
        
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
    
    def _assign_role(self, group_type: str, member_index: int, group_size: int) -> str:
        """Assign role to group member"""
        if group_type == 'family':
            if group_size >= 4:
                roles = ['parent', 'parent', 'child', 'child']
            elif group_size == 3:
                roles = ['parent', 'parent', 'child']
            else:
                roles = ['parent', 'child']
            return roles[member_index] if member_index < len(roles) else 'child'
        elif group_type == 'friends':
            return random.choice(['friend', 'travel_buddy', 'colleague'])
        elif group_type == 'business':
            return random.choice(['colleague', 'client', 'partner'])
        else:  # solo
            return 'solo_traveler'
    
    def _generate_group_behavior_patterns(self, group_type: str, group_size: int) -> Dict[str, Any]:
        """Generate behavior patterns for a group"""
        patterns = {
            'family': {
                'movement': 'coordinated',
                'coordination': 'high',
                'separation_probability': 0.1,
                'activity_synchronization': 0.9,
                'decision_making': 'parent_led'
            },
            'friends': {
                'movement': 'semi_coordinated',
                'coordination': 'medium',
                'separation_probability': 0.3,
                'activity_synchronization': 0.7,
                'decision_making': 'consensus'
            },
            'business': {
                'movement': 'coordinated',
                'coordination': 'high',
                'separation_probability': 0.05,
                'activity_synchronization': 0.95,
                'decision_making': 'hierarchical'
            },
            'solo': {
                'movement': 'independent',
                'coordination': 'none',
                'separation_probability': 1.0,
                'activity_synchronization': 0.0,
                'decision_making': 'individual'
            }
        }
        
        return patterns.get(group_type, patterns['solo'])
    
    def _generate_scene_configuration(self, city: str, tourists: List[SceneTourist], groups: List[TouristGroup]) -> SceneConfiguration:
        """Generate scene configuration"""
        # Calculate distributions
        tourist_types_distribution = {}
        group_size_distribution = {}
        
        for tourist in tourists:
            tourist_types_distribution[tourist.tourist_type] = tourist_types_distribution.get(tourist.tourist_type, 0) + 1
            group_size_distribution[tourist.group_size] = group_size_distribution.get(tourist.group_size, 0) + 1
        
        # Convert to percentages
        total_tourists = len(tourists)
        tourist_types_distribution = {k: v/total_tourists for k, v in tourist_types_distribution.items()}
        group_size_distribution = {k: v/total_tourists for k, v in group_size_distribution.items()}
        
        # Generate behavioral patterns
        behavioral_patterns = []
        for pattern_category, patterns in self.behavioral_patterns.items():
            for pattern_name, pattern_data in patterns.items():
                behavioral_pattern = BehavioralPattern(
                    pattern_id=f"{pattern_category}_{pattern_name}",
                    pattern_type=pattern_category,
                    description=pattern_data['description'],
                    parameters=pattern_data['parameters'],
                    probability=pattern_data['probability']
                )
                behavioral_patterns.append(behavioral_pattern)
        
        # Generate weather conditions
        weather_conditions = {
            'primary_condition': random.choice(self.generation_config['scene_settings']['weather_conditions']),
            'temperature_range': [random.randint(10, 30), random.randint(15, 35)],
            'precipitation_probability': random.uniform(0.1, 0.4),
            'wind_speed': random.uniform(5, 20)
        }
        
        # Generate special events
        special_events = []
        if random.random() < 0.3:  # 30% chance of special events
            num_events = random.randint(1, 3)
            special_events = random.sample(self.generation_config['scene_settings']['special_events'], num_events)
        
        scene_config = SceneConfiguration(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            scene_name=f"Tourist Scene - {city.title()}",
            city=city,
            date_range=self.generation_config['date_range'],
            total_tourists=total_tourists,
            tourist_types_distribution=tourist_types_distribution,
            group_size_distribution=group_size_distribution,
            behavioral_patterns=behavioral_patterns,
            poi_categories=self.generation_config['scene_settings']['poi_categories'],
            weather_conditions=weather_conditions,
            special_events=special_events
        )
        
        return scene_config
    
    def generate_scene_behavior_data(self, city: str = "new_york", output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Generate scene and behavioral data and save to files"""
        if output_dir is None:
            output_dir = f"data/generated/{city}/scene/tourists/setup"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate scene tourists
        print("Generating scene tourists...")
        tourists = self._generate_scene_tourists()
        
        # Generate tourist groups
        print("Generating tourist groups...")
        groups = self._generate_tourist_groups(tourists)
        
        # Generate scene configuration
        print("Generating scene configuration...")
        scene_config = self._generate_scene_configuration(city, tourists, groups)
        
        # Create output data structure
        output_data = {
            'scene_configuration': asdict(scene_config),
            'tourists': [asdict(tourist) for tourist in tourists],
            'groups': [asdict(group) for group in groups],
            'behavioral_patterns': self.behavioral_patterns,
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_tourists': len(tourists),
                'total_groups': len(groups),
                'city': city,
                'data_type': 'scene_behavior',
                'ontology_version': '1.0',
                'ontology_name': 'Tourist Scene and Behavioral Data',
                'config_used': self.config
            }
        }
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'scene_behavior_data.json')
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save as CSV files
        csv_tourists_path = os.path.join(output_dir, 'tourists.csv')
        with open(csv_tourists_path, 'w', newline='') as f:
            if tourists:
                writer = csv.DictWriter(f, fieldnames=asdict(tourists[0]).keys())
                writer.writeheader()
                for tourist in tourists:
                    writer.writerow(asdict(tourist))
        
        csv_groups_path = os.path.join(output_dir, 'groups.csv')
        with open(csv_groups_path, 'w', newline='') as f:
            if groups:
                writer = csv.DictWriter(f, fieldnames=asdict(groups[0]).keys())
                writer.writeheader()
                for group in groups:
                    writer.writerow(asdict(group))
        
        # Save scene configuration separately
        scene_config_path = os.path.join(output_dir, 'scene_configuration.json')
        with open(scene_config_path, 'w') as f:
            json.dump(asdict(scene_config), f, indent=2)
        
        print(f"Generated {len(tourists)} tourists, {len(groups)} groups, and scene configuration")
        print(f"Scene behavior data saved to {output_dir}")
        
        return output_data


def main():
    """Main function to run the scene behavior generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate scene and behavioral data')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--poi-data', type=str, help='Path to POI data directory')
    parser.add_argument('--city', type=str, default='new_york', help='City name')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--count', type=int, help='Number of tourists to generate')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = SceneBehaviorGenerator(
        config_path=args.config,
        poi_data_path=args.poi_data
    )
    
    # Override tourist count if specified
    if args.count:
        generator.generation_config['total_tourists'] = args.count
    
    # Generate data
    output_data = generator.generate_scene_behavior_data(
        city=args.city,
        output_dir=args.output
    )
    
    print("Scene behavior data generation completed successfully!")


if __name__ == "__main__":
    main()
