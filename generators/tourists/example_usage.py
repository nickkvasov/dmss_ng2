#!/usr/bin/env python3
"""
Example usage of the Tourist Generator

This script demonstrates how to use the tourist generator to create
synthetic tourist data for analysis and testing.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import the tourist generator
sys.path.append(str(Path(__file__).parent))

from tourist_generator import TouristGenerator


def example_basic_usage():
    """Example of basic tourist generator usage"""
    print("=== Basic Tourist Generator Usage ===")
    
    # Initialize the generator
    generator = TouristGenerator()
    
    # Generate a small number of tourist profiles
    print("Generating 10 tourist profiles...")
    tourists = generator.generate_tourist_profiles(count=10)
    
    print(f"Generated {len(tourists)} tourists:")
    for tourist in tourists[:3]:  # Show first 3
        print(f"  - {tourist.tourist_type}: {tourist.age} years old, "
              f"group of {tourist.group_size}, staying {tourist.stay_duration} days")
    
    # Generate behaviors if POI data is available
    if generator.poi_data:
        print("\nGenerating tourist behaviors...")
        behaviors = generator.generate_tourist_behaviors(tourists[:5])  # Use first 5 tourists
        
        print(f"Generated {len(behaviors)} behaviors:")
        for behavior in behaviors[:3]:  # Show first 3
            print(f"  - {behavior.tourist_id} visited {behavior.poi_id} "
                  f"on {behavior.visit_date} at {behavior.visit_time} "
                  f"for {behavior.duration_hours} hours")
    else:
        print("\nNo POI data available - skipping behavior generation")


def example_custom_configuration():
    """Example of using custom configuration"""
    print("\n=== Custom Configuration Example ===")
    
    # Create a custom configuration
    custom_config = {
        'tourist_types': {
            'cultural_tourist': {
                'percentage': 50,  # Increase cultural tourists
                'preferences': ['museums', 'historic_sites'],
                'behavior_patterns': ['spends_2_4_hours_per_poi', 'visits_3_5_pois_per_day'],
                'demographics': {
                    'age_range': [25, 65],
                    'group_size': [1, 4],
                    'stay_duration': [3, 7],
                    'budget_level': 'medium_to_high'
                }
            },
            'leisure_tourist': {
                'percentage': 50,  # Increase leisure tourists
                'preferences': ['parks', 'landmarks'],
                'behavior_patterns': ['spends_1_3_hours_per_poi', 'visits_2_4_pois_per_day'],
                'demographics': {
                    'age_range': [20, 50],
                    'group_size': [2, 6],
                    'stay_duration': [2, 5],
                    'budget_level': 'medium'
                }
            }
        },
        'generation': {
            'total_tourists': 20,
            'date_range': {
                'start_date': '2024-06-01',
                'end_date': '2024-08-31'
            }
        }
    }
    
    # Initialize generator with custom config
    generator = TouristGenerator()
    generator.config = custom_config
    generator.tourist_types = custom_config['tourist_types']
    generator.generation_config = custom_config['generation']
    
    # Generate tourists with custom configuration
    print("Generating tourists with custom configuration...")
    tourists = generator.generate_tourist_profiles()
    
    print(f"Generated {len(tourists)} tourists with custom config:")
    tourist_types = {}
    for tourist in tourists:
        tourist_types[tourist.tourist_type] = tourist_types.get(tourist.tourist_type, 0) + 1
    
    for tourist_type, count in tourist_types.items():
        print(f"  - {tourist_type}: {count} tourists")


def example_data_export():
    """Example of exporting generated data"""
    print("\n=== Data Export Example ===")
    
    # Initialize generator
    generator = TouristGenerator()
    
    # Generate a small dataset
    print("Generating sample data for export...")
    tourists = generator.generate_tourist_profiles(count=5)
    behaviors = []
    
    if generator.poi_data:
        behaviors = generator.generate_tourist_behaviors(tourists)
    
    # Create output directory
    output_dir = "example_tourist_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Export data
    output_data = {
        'tourists': [tourist.__dict__ for tourist in tourists],
        'behaviors': [behavior.__dict__ for behavior in behaviors],
        'metadata': {
            'generation_date': '2024-01-15T10:30:00',
            'total_tourists': len(tourists),
            'total_behaviors': len(behaviors),
            'example_run': True
        }
    }
    
    # Save as JSON
    import json
    json_path = os.path.join(output_dir, 'example_tourists_data.json')
    with open(json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Data exported to {json_path}")
    print(f"  - {len(tourists)} tourists")
    print(f"  - {len(behaviors)} behaviors")
    
    # Clean up
    import shutil
    shutil.rmtree(output_dir)
    print("Example output directory cleaned up")


def main():
    """Main example function"""
    print("Tourist Generator Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_custom_configuration()
    example_data_export()
    
    print("\n" + "=" * 50)
    print("Examples completed successfully!")
    print("\nTo run the full tourist generator:")
    print("  ./generators/tourists/run_tourist_generator.sh --city new_york")


if __name__ == "__main__":
    main()
