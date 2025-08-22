#!/usr/bin/env python3
"""
Fetch POI data for all configured areas from internet sources.

This script fetches real POI data from OpenStreetMap and other sources
for all configured areas and saves them in organized directories.
"""

import sys
import os
from pathlib import Path
from poi_fetcher import POIFetcher
import yaml


def load_area_config(config_path: str) -> dict:
    """Load area configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('areas', {})


def fetch_pois_for_all_areas(config_path: str = 'fetcher_config.yaml', 
                           sources: list = None, output_dir: str = None):
    """Fetch POI data for all configured areas"""
    
    # Load configuration
    if not Path(config_path).exists():
        print(f"Configuration file {config_path} not found!")
        return
    
    areas = load_area_config(config_path)
    
    if not areas:
        print("No areas configured!")
        return
    
    # Initialize fetcher
    fetcher = POIFetcher(config_path)
    
    # Set default sources if none specified
    if not sources:
        sources = ['osm']  # Default to OpenStreetMap only
    
    # Set output directory
    if not output_dir:
        output_dir = 'data/generated'
    
    print(f"Fetching POI data for {len(areas)} areas...")
    print(f"Sources: {', '.join(sources)}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Fetch POIs for each area
    for area_name, area_config in areas.items():
        print(f"=== Fetching POIs for {area_config['name']} ===")
        
        try:
            # Fetch POIs
            pois = fetcher.fetch_pois(area_config['bounds'], sources)
            
            # Save POIs
            fetcher.save_pois(pois, output_dir, area_name)
            
            print(f"Successfully fetched {len(pois)} POIs for {area_config['name']}")
            
        except Exception as e:
            print(f"Error fetching POIs for {area_config['name']}: {e}")
        
        print()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch POI data for all areas')
    parser.add_argument('--config', default='fetcher_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--sources', nargs='+', choices=['osm', 'opentripmap'],
                       default=['osm'], help='Data sources to use')
    parser.add_argument('--output-dir', default='../../data/generated',
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    output_dir = str(project_root / args.output_dir)
    
    print("Fetching POI data for all configured areas...")
    print(f"Output directory: {output_dir}")
    print()
    
    # Fetch POIs for all areas
    fetch_pois_for_all_areas(args.config, args.sources, output_dir)
    
    print("=== Fetch Complete ===")


if __name__ == "__main__":
    main()
