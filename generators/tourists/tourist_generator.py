"""
Tourist Behavior Generator

Generates synthetic tourist data including visitor profiles, behaviors, and patterns
based on POI data for tourism analysis and impact assessment.
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
class Tourist:
    """Tourist profile data structure"""
    tourist_id: str
    tourist_type: str
    age: int
    group_size: int
    stay_duration: int  # days
    budget_level: str
    origin_country: str
    origin_city: str
    arrival_date: str
    departure_date: str
    preferences: List[str]
    behavior_patterns: List[str]


@dataclass
class TouristBehavior:
    """Tourist behavior data structure"""
    behavior_id: str
    tourist_id: str
    poi_id: str
    visit_date: str
    visit_time: str
    duration_hours: float
    activities: List[str]
    satisfaction_rating: Optional[float] = None
    spending_amount: Optional[float] = None
    photos_taken: Optional[int] = None
    review_text: Optional[str] = None


class TouristGenerator:
    """Generates synthetic tourist data and behaviors based on POI data"""
    
    def __init__(self, config_path: Optional[str] = None, poi_data_path: Optional[str] = None):
        """Initialize the tourist generator with configuration and POI data"""
        self.config = self._load_config(config_path)
        self.poi_data = self._load_poi_data(poi_data_path)
        self.tourist_types = self.config.get('tourist_types', {})
        self.behavior_patterns = self.config.get('behavior_patterns', {})
        self.seasonal_patterns = self.config.get('seasonal_patterns', {})
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
        # Simplified location data - in a real implementation, this would be more comprehensive
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
    
    def generate_tourist_profiles(self, count: Optional[int] = None) -> List[Tourist]:
        """Generate tourist profiles based on configured types and percentages"""
        if count is None:
            count = self.generation_config.get('total_tourists', 100)
        
        tourists = []
        start_date = datetime.strptime(self.generation_config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.generation_config['date_range']['end_date'], '%Y-%m-%d')
        
        for tourist_type, config in self.tourist_types.items():
            type_count = int(count * config['percentage'] / 100)
            
            for _ in range(type_count):
                # Generate arrival and departure dates
                arrival_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
                stay_duration = random.randint(*config['demographics']['stay_duration'])
                departure_date = arrival_date + timedelta(days=stay_duration)
                
                # Generate tourist profile
                tourist = Tourist(
                    tourist_id=f"tourist_{uuid.uuid4().hex[:8]}",
                    tourist_type=tourist_type,
                    age=random.randint(*config['demographics']['age_range']),
                    group_size=random.randint(*config['demographics']['group_size']),
                    stay_duration=stay_duration,
                    budget_level=config['demographics']['budget_level'],
                    origin_country=random.choice(self.countries),
                    origin_city=random.choice(self.cities.get(random.choice(self.countries), ["Unknown"])),
                    arrival_date=arrival_date.strftime('%Y-%m-%d'),
                    departure_date=departure_date.strftime('%Y-%m-%d'),
                    preferences=config['preferences'].copy(),
                    behavior_patterns=config['behavior_patterns'].copy()
                )
                tourists.append(tourist)
        
        # Shuffle to randomize order
        random.shuffle(tourists)
        return tourists
    
    def generate_tourist_behaviors(self, tourists: List[Tourist]) -> List[TouristBehavior]:
        """Generate tourist behaviors based on POI data and tourist profiles"""
        behaviors = []
        
        for tourist in tourists:
            # Determine number of POIs to visit based on stay duration and tourist type
            total_pois = self._calculate_total_pois(tourist)
            
            # Generate visit dates within tourist's stay period
            arrival_date = datetime.strptime(tourist.arrival_date, '%Y-%m-%d')
            departure_date = datetime.strptime(tourist.departure_date, '%Y-%m-%d')
            
            # Distribute POI visits across the stay duration
            visit_dates = self._distribute_visits(arrival_date, departure_date, total_pois)
            
            # Select POIs based on tourist preferences
            selected_pois = self._select_pois_for_tourist(tourist, total_pois)
            
            for i, (visit_date, poi) in enumerate(zip(visit_dates, selected_pois)):
                # Generate visit time based on tourist type
                visit_time = self._generate_visit_time(tourist)
                
                # Generate visit duration
                duration_hours = self._generate_visit_duration(tourist)
                
                # Generate activities
                activities = self._generate_activities(tourist, poi)
                
                # Generate satisfaction rating
                satisfaction_rating = self._generate_satisfaction_rating(tourist, poi)
                
                # Generate spending amount
                spending_amount = self._generate_spending_amount(tourist, poi, duration_hours)
                
                # Generate number of photos
                photos_taken = self._generate_photos_taken(tourist, poi)
                
                # Generate review text
                review_text = self._generate_review_text(tourist, poi, satisfaction_rating)
                
                behavior = TouristBehavior(
                    behavior_id=f"behavior_{uuid.uuid4().hex[:8]}",
                    tourist_id=tourist.tourist_id,
                    poi_id=poi['poi_id'],
                    visit_date=visit_date.strftime('%Y-%m-%d'),
                    visit_time=visit_time,
                    duration_hours=duration_hours,
                    activities=activities,
                    satisfaction_rating=satisfaction_rating,
                    spending_amount=spending_amount,
                    photos_taken=photos_taken,
                    review_text=review_text
                )
                behaviors.append(behavior)
        
        return behaviors
    
    def _calculate_total_pois(self, tourist: Tourist) -> int:
        """Calculate total number of POIs to visit based on tourist type and stay duration"""
        base_pois_per_day = {
            'cultural_tourist': 3,
            'leisure_tourist': 2,
            'adventure_tourist': 6,
            'family_tourist': 2,
            'business_tourist': 1
        }
        
        base_pois = base_pois_per_day.get(tourist.tourist_type, 2)
        return min(base_pois * tourist.stay_duration, 20)  # Cap at 20 POIs
    
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
    
    def _select_pois_for_tourist(self, tourist: Tourist, total_pois: int) -> List[Dict]:
        """Select POIs based on tourist preferences"""
        available_pois = []
        
        # Collect POIs from preferred categories
        for category in tourist.preferences:
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
    
    def _generate_visit_time(self, tourist: Tourist) -> str:
        """Generate visit time based on tourist type"""
        time_patterns = {
            'cultural_tourist': [9, 12],      # Morning
            'leisure_tourist': [12, 17],      # Afternoon
            'adventure_tourist': [6, 10],     # Early morning
            'family_tourist': [10, 14],       # Mid-morning
            'business_tourist': [17, 22]      # Evening
        }
        
        start_hour, end_hour = time_patterns.get(tourist.tourist_type, [9, 17])
        hour = random.randint(start_hour, end_hour)
        minute = random.randint(0, 59)
        
        return f"{hour:02d}:{minute:02d}"
    
    def _generate_visit_duration(self, tourist: Tourist) -> float:
        """Generate visit duration based on tourist type"""
        duration_patterns = {
            'cultural_tourist': [2.0, 4.0],
            'leisure_tourist': [1.0, 3.0],
            'adventure_tourist': [1.0, 2.0],
            'family_tourist': [2.0, 5.0],
            'business_tourist': [0.5, 1.0]
        }
        
        min_duration, max_duration = duration_patterns.get(tourist.tourist_type, [1.0, 3.0])
        return round(random.uniform(min_duration, max_duration), 1)
    
    def _generate_activities(self, tourist: Tourist, poi: Dict) -> List[str]:
        """Generate activities based on tourist type and POI category"""
        base_activities = {
            'museums': ['viewing_exhibits', 'taking_photos', 'reading_plaques'],
            'historic_sites': ['taking_photos', 'reading_history', 'guided_tour'],
            'monuments': ['taking_photos', 'reading_plaques', 'walking_around'],
            'parks': ['walking', 'picnicking', 'taking_photos', 'relaxing'],
            'landmarks': ['taking_photos', 'sightseeing', 'walking_around'],
            'theaters': ['watching_performance', 'taking_photos', 'dining']
        }
        
        activities = base_activities.get(poi.get('category', 'landmarks'), ['taking_photos'])
        
        # Add tourist-specific activities
        if tourist.tourist_type == 'cultural_tourist':
            activities.extend(['reading_descriptions', 'learning_history'])
        elif tourist.tourist_type == 'family_tourist':
            activities.extend(['educational_activities', 'family_photos'])
        elif tourist.tourist_type == 'adventure_tourist':
            activities.extend(['exploring', 'finding_unique_angles'])
        
        return random.sample(activities, min(len(activities), random.randint(2, 4)))
    
    def _generate_satisfaction_rating(self, tourist: Tourist, poi: Dict) -> float:
        """Generate satisfaction rating based on tourist type and POI"""
        base_rating = random.uniform(3.0, 5.0)
        
        # Adjust based on tourist type preferences
        if poi.get('category') in tourist.preferences:
            base_rating += random.uniform(0.0, 0.5)
        
        return round(min(base_rating, 5.0), 1)
    
    def _generate_spending_amount(self, tourist: Tourist, poi: Dict, duration_hours: float) -> float:
        """Generate spending amount based on tourist budget and POI type"""
        base_spending = {
            'museums': 15.0,
            'historic_sites': 10.0,
            'monuments': 5.0,
            'parks': 0.0,
            'landmarks': 5.0,
            'theaters': 50.0
        }
        
        base_amount = base_spending.get(poi.get('category', 'landmarks'), 10.0)
        
        # Adjust based on budget level
        budget_multipliers = {
            'low': 0.5,
            'low_to_medium': 0.7,
            'medium': 1.0,
            'medium_to_high': 1.3,
            'high': 1.8
        }
        
        multiplier = budget_multipliers.get(tourist.budget_level, 1.0)
        
        # Add some randomness
        final_amount = base_amount * multiplier * random.uniform(0.8, 1.2)
        
        return round(final_amount, 2)
    
    def _generate_photos_taken(self, tourist: Tourist, poi: Dict) -> int:
        """Generate number of photos taken based on tourist type"""
        base_photos = {
            'cultural_tourist': 15,
            'leisure_tourist': 10,
            'adventure_tourist': 25,
            'family_tourist': 20,
            'business_tourist': 5
        }
        
        base_count = base_photos.get(tourist.tourist_type, 10)
        return random.randint(max(1, base_count - 5), base_count + 5)
    
    def _generate_review_text(self, tourist: Tourist, poi: Dict, satisfaction_rating: float) -> Optional[str]:
        """Generate review text based on satisfaction rating and tourist type"""
        if satisfaction_rating < 3.0:
            return None  # Less likely to leave reviews for poor experiences
        
        review_templates = {
            'cultural_tourist': [
                "Fascinating exhibits and rich history. Highly educational experience.",
                "Great cultural experience with informative displays.",
                "Worth visiting for the historical significance and cultural value."
            ],
            'leisure_tourist': [
                "Beautiful place to relax and enjoy the atmosphere.",
                "Perfect spot for a leisurely visit and great photos.",
                "Lovely experience, very peaceful and enjoyable."
            ],
            'adventure_tourist': [
                "Amazing find! Unique perspective and great photo opportunities.",
                "Hidden gem with incredible views and interesting history.",
                "Exciting place to explore and discover new angles."
            ],
            'family_tourist': [
                "Great family-friendly attraction with educational value.",
                "Perfect for kids and adults alike. Educational and fun.",
                "Family enjoyed the visit, lots to see and learn."
            ],
            'business_tourist': [
                "Convenient location and interesting history.",
                "Quick visit but worth the time. Good photo opportunity.",
                "Efficient way to see a key landmark during business trip."
            ]
        }
        
        templates = review_templates.get(tourist.tourist_type, ["Great experience, worth visiting."])
        return random.choice(templates)
    
    def generate_all_data(self, city: str = "new_york", output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Generate all tourist data and save to files"""
        if output_dir is None:
            output_dir = f"data/generated/{city}/tourists"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate tourist profiles
        print("Generating tourist profiles...")
        tourists = self.generate_tourist_profiles()
        
        # Generate tourist behaviors
        print("Generating tourist behaviors...")
        behaviors = self.generate_tourist_behaviors(tourists)
        
        # Save data
        output_data = {
            'tourists': [asdict(tourist) for tourist in tourists],
            'behaviors': [asdict(behavior) for behavior in behaviors],
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_tourists': len(tourists),
                'total_behaviors': len(behaviors),
                'city': city,
                'config_used': self.config
            }
        }
        
        # Save as JSON
        json_path = os.path.join(output_dir, 'tourists_data.json')
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save as CSV
        csv_tourists_path = os.path.join(output_dir, 'tourists.csv')
        with open(csv_tourists_path, 'w', newline='') as f:
            if tourists:
                writer = csv.DictWriter(f, fieldnames=asdict(tourists[0]).keys())
                writer.writeheader()
                for tourist in tourists:
                    writer.writerow(asdict(tourist))
        
        csv_behaviors_path = os.path.join(output_dir, 'behaviors.csv')
        with open(csv_behaviors_path, 'w', newline='') as f:
            if behaviors:
                writer = csv.DictWriter(f, fieldnames=asdict(behaviors[0]).keys())
                writer.writeheader()
                for behavior in behaviors:
                    writer.writerow(asdict(behavior))
        
        print(f"Generated {len(tourists)} tourists and {len(behaviors)} behaviors")
        print(f"Data saved to {output_dir}")
        
        return output_data


def main():
    """Main function to run the tourist generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate tourist behavior data')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--poi-data', type=str, help='Path to POI data directory')
    parser.add_argument('--city', type=str, default='new_york', help='City name')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--count', type=int, help='Number of tourists to generate')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TouristGenerator(
        config_path=args.config,
        poi_data_path=args.poi_data
    )
    
    # Generate data
    output_data = generator.generate_all_data(
        city=args.city,
        output_dir=args.output
    )
    
    print("Tourist data generation completed successfully!")


if __name__ == "__main__":
    main()
