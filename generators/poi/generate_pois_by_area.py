#!/usr/bin/env python3
"""
Generate POI data for different areas and organize into separate directories.

This script generates POI data for multiple areas and saves them in organized
directories under /data/generated/<area_name>/
"""

import os
import sys
import argparse
from pathlib import Path
from poi_generator import POIGenerator


# Area configurations
AREA_CONFIGS = {
    'new_york': {
        'name': 'New York City',
        'bounds': {
            'min_lat': 40.7,
            'max_lat': 40.8,
            'min_lon': -74.0,
            'max_lon': -73.9
        }
    },
    'london': {
        'name': 'London',
        'bounds': {
            'min_lat': 51.4,
            'max_lat': 51.6,
            'min_lon': -0.2,
            'max_lon': 0.1
        }
    },
    'paris': {
        'name': 'Paris',
        'bounds': {
            'min_lat': 48.8,
            'max_lat': 48.9,
            'min_lon': 2.3,
            'max_lon': 2.4
        }
    },
    'tokyo': {
        'name': 'Tokyo',
        'bounds': {
            'min_lat': 35.6,
            'max_lat': 35.8,
            'min_lon': 139.6,
            'max_lon': 139.8
        }
    },
    'san_francisco': {
        'name': 'San Francisco',
        'bounds': {
            'min_lat': 37.7,
            'max_lat': 37.8,
            'min_lon': -122.5,
            'max_lon': -122.4
        }
    },
    'barcelona': {
        'name': 'Barcelona',
        'bounds': {
            'min_lat': 41.3,
            'max_lat': 41.5,
            'min_lon': 2.1,
            'max_lon': 2.2
        }
    }
}


def create_area_config(area_name: str, area_config: dict) -> dict:
    """Create a configuration for a specific area"""
    config = {
        'city_bounds': {
            'name': area_config['name'],
            **area_config['bounds']
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
                    'Zoo',
                    'Aquarium',
                    'Planetarium',
                    'Observatory',
                    'Library',
                    'Cultural Center'
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
                    '{name} Tower',
                    '{name} Lodge',
                    '{name} Manor',
                    '{name} Palace'
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
                    '{name} Tavern',
                    '{name} Pub',
                    '{name} Steakhouse',
                    '{name} Pizzeria',
                    '{name} Deli',
                    '{name} Bakery',
                    '{name} Sushi Bar',
                    '{name} Wine Bar'
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
                    '{name} Amphitheater',
                    '{name} Exhibition Hall',
                    '{name} Conference Center',
                    '{name} Event Space',
                    '{name} Ballroom',
                    '{name} Opera House',
                    '{name} Cinema',
                    '{name} Music Hall',
                    '{name} Performance Center'
                ]
            },
            'shopping': {
                'count': 40,
                'templates': [
                    '{name} Mall',
                    '{name} Shopping Center',
                    '{name} Market',
                    '{name} Plaza',
                    '{name} Arcade',
                    '{name} Boutique',
                    '{name} Department Store',
                    '{name} Outlet',
                    '{name} Bazaar',
                    '{name} Market Square'
                ]
            },
            'transportation': {
                'count': 25,
                'templates': [
                    '{name} Station',
                    '{name} Terminal',
                    '{name} Hub',
                    '{name} Airport',
                    '{name} Port',
                    '{name} Bus Station',
                    '{name} Train Station',
                    '{name} Metro Station',
                    '{name} Ferry Terminal',
                    '{name} Parking Garage'
                ]
            }
        }
    }
    
    return config


def save_config_to_file(config: dict, config_path: str):
    """Save configuration to YAML file"""
    import yaml
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)


def generate_pois_for_area(area_name: str, area_config: dict, output_base_dir: str, 
                          categories: list = None, save_config: bool = True):
    """Generate POIs for a specific area"""
    
    # Create area directory
    area_dir = Path(output_base_dir) / area_name
    area_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== Generating POIs for {area_config['name']} ===")
    
    # Create configuration for this area
    config = create_area_config(area_name, area_config)
    
    # Save configuration file
    if save_config:
        config_path = area_dir / 'config.yaml'
        save_config_to_file(config, config_path)
        print(f"Configuration saved to: {config_path}")
    
    # Initialize generator with area-specific config
    generator = POIGenerator()
    generator.config = config
    generator.city_bounds = config['city_bounds']
    generator.poi_categories = config['poi_categories']
    
    # Generate POIs
    if categories:
        all_pois = []
        for category in categories:
            if category in generator.poi_categories:
                pois = generator.generate_pois(category)
                all_pois.extend(pois)
                print(f"Generated {len(pois)} {category}")
            else:
                print(f"Warning: Category '{category}' not found in configuration")
    else:
        all_pois = generator.generate_pois()
        print(f"Generated {len(all_pois)} total POIs")
    
    # Save to JSON and CSV
    json_path = area_dir / 'pois.json'
    csv_path = area_dir / 'pois.csv'
    
    generator.save_to_json(all_pois, str(json_path))
    generator.save_to_csv(all_pois, str(csv_path))
    
    # Generate category-specific files
    category_counts = {}
    for poi in all_pois:
        category = poi.category
        if category not in category_counts:
            category_counts[category] = []
        category_counts[category].append(poi)
    
    # Save individual category files
    for category, pois in category_counts.items():
        category_json_path = area_dir / f'{category}.json'
        category_csv_path = area_dir / f'{category}.csv'
        
        generator.save_to_json(pois, str(category_json_path))
        generator.save_to_csv(pois, str(category_csv_path))
        
        print(f"  {category}: {len(pois)} POIs")
    
    return area_dir


def main():
    parser = argparse.ArgumentParser(description='Generate POI data for different areas')
    parser.add_argument('--areas', nargs='+', choices=list(AREA_CONFIGS.keys()) + ['all'],
                       default=['all'], help='Areas to generate POIs for')
    parser.add_argument('--categories', nargs='+', 
                       choices=['attractions', 'hotels', 'restaurants', 'venues', 'shopping', 'transportation'],
                       help='Specific categories to generate (default: all)')
    parser.add_argument('--output-dir', default='../../data/generated',
                       help='Base output directory (default: ../../data/generated)')
    parser.add_argument('--no-config', action='store_true',
                       help='Skip saving configuration files')
    
    args = parser.parse_args()
    
    # Determine areas to process
    if 'all' in args.areas:
        areas_to_process = list(AREA_CONFIGS.keys())
    else:
        areas_to_process = args.areas
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating POI data for areas: {', '.join(areas_to_process)}")
    print(f"Output directory: {output_dir.absolute()}")
    
    if args.categories:
        print(f"Categories: {', '.join(args.categories)}")
    else:
        print("Categories: all")
    
    # Generate POIs for each area
    generated_areas = []
    for area_name in areas_to_process:
        if area_name in AREA_CONFIGS:
            area_config = AREA_CONFIGS[area_name]
            area_dir = generate_pois_for_area(
                area_name, 
                area_config, 
                str(output_dir),
                args.categories,
                not args.no_config
            )
            generated_areas.append(area_dir)
        else:
            print(f"Warning: Unknown area '{area_name}'")
    
    # Summary
    print(f"\n=== Generation Complete ===")
    print(f"Generated POI data for {len(generated_areas)} areas:")
    for area_dir in generated_areas:
        print(f"  {area_dir.name}: {area_dir.absolute()}")


if __name__ == "__main__":
    main()
