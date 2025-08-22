#!/usr/bin/env python3
"""
Generate POI data for all available areas.

This is a convenience script that generates POI data for all configured areas
and saves them in organized directories.
"""

import sys
from pathlib import Path
from generate_pois_by_area import main as generate_main

def main():
    """Generate POI data for all areas"""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Set up arguments for the main generation script
    sys.argv = [
        'generate_pois_by_area.py',
        '--areas', 'all',
        '--output-dir', str(project_root / 'data' / 'generated')
    ]
    
    print("Generating POI data for all available areas...")
    print(f"Output directory: {project_root / 'data' / 'generated'}")
    print()
    
    # Run the main generation script
    generate_main()

if __name__ == "__main__":
    main()
