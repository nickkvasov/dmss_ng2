#!/usr/bin/env python3
"""
Generate tourist data for different cities

This script generates tourist behavior data based on POI data for specified cities.
Uses the project's virtual environment (.venv).
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import the tourist generator
sys.path.append(str(Path(__file__).parent))

from tourist_generator import TouristGenerator


def generate_tourists_for_city(city: str, poi_data_path: str = None, config_path: str = None, count: int = None):
    """Generate tourist data for a specific city"""
    
    if poi_data_path is None:
        poi_data_path = f"data/generated/{city}"
    
    if config_path is None:
        config_path = "generators/tourists/config.yaml"
    
    print(f"Generating tourist data for {city}...")
    print(f"POI data path: {poi_data_path}")
    print(f"Config path: {config_path}")
    
    # Check if POI data exists
    if not os.path.exists(poi_data_path):
        print(f"Error: POI data not found at {poi_data_path}")
        print("Please run the POI generator first to create POI data.")
        return False
    
    # Initialize tourist generator
    generator = TouristGenerator(
        config_path=config_path,
        poi_data_path=poi_data_path
    )
    
    # Override tourist count if specified
    if count:
        generator.generation_config['total_tourists'] = count
    
    # Generate tourist data
    try:
        output_data = generator.generate_all_data(city=city)
        print(f"Successfully generated tourist data for {city}")
        print(f"Generated {len(output_data['tourists'])} tourists")
        print(f"Generated {len(output_data['behaviors'])} behaviors")
        return True
    except Exception as e:
        print(f"Error generating tourist data: {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate tourist data for cities')
    parser.add_argument('--city', type=str, default='new_york', help='City name')
    parser.add_argument('--poi-data', type=str, help='Path to POI data directory')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--count', type=int, help='Number of tourists to generate')
    
    args = parser.parse_args()
    
    success = generate_tourists_for_city(
        city=args.city,
        poi_data_path=args.poi_data,
        config_path=args.config,
        count=args.count
    )
    
    if success:
        print("Tourist data generation completed successfully!")
        sys.exit(0)
    else:
        print("Tourist data generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
