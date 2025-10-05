#!/usr/bin/env python3
"""
Test script for the tourist generator

This script tests the tourist generator functionality and validates the generated data.
Uses the project's virtual environment (.venv).
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path to import the tourist generator
sys.path.append(str(Path(__file__).parent))

from tourist_generator import TouristGenerator, Tourist, TouristBehavior


def test_tourist_generator():
    """Test the tourist generator functionality"""
    
    print("Testing Tourist Generator...")
    
    # Test 1: Initialize generator
    print("\n1. Testing generator initialization...")
    try:
        generator = TouristGenerator()
        print("✓ Generator initialized successfully")
    except Exception as e:
        print(f"✗ Generator initialization failed: {e}")
        return False
    
    # Test 2: Load configuration
    print("\n2. Testing configuration loading...")
    if generator.config:
        print("✓ Configuration loaded successfully")
        print(f"  - Tourist types: {list(generator.tourist_types.keys())}")
    else:
        print("✗ Configuration loading failed")
        return False
    
    # Test 3: Load POI data
    print("\n3. Testing POI data loading...")
    if generator.poi_data:
        print("✓ POI data loaded successfully")
        print(f"  - Available categories: {list(generator.poi_data.keys())}")
        total_pois = sum(len(pois) for pois in generator.poi_data.values())
        print(f"  - Total POIs: {total_pois}")
    else:
        print("⚠ POI data not found (this is expected if POI data doesn't exist yet)")
    
    # Test 4: Generate tourist profiles
    print("\n4. Testing tourist profile generation...")
    try:
        tourists = generator.generate_tourist_profiles(count=10)
        print(f"✓ Generated {len(tourists)} tourist profiles")
        
        # Validate tourist data
        for tourist in tourists[:3]:  # Check first 3 tourists
            print(f"  - Tourist {tourist.tourist_id}: {tourist.tourist_type}, age {tourist.age}")
            assert tourist.tourist_id.startswith("tourist_")
            assert tourist.age > 0
            assert tourist.group_size > 0
            assert tourist.stay_duration > 0
            
    except Exception as e:
        print(f"✗ Tourist profile generation failed: {e}")
        return False
    
    # Test 5: Generate tourist behaviors (if POI data exists)
    print("\n5. Testing tourist behavior generation...")
    if generator.poi_data:
        try:
            behaviors = generator.generate_tourist_behaviors(tourists[:5])  # Use first 5 tourists
            print(f"✓ Generated {len(behaviors)} tourist behaviors")
            
            # Validate behavior data
            for behavior in behaviors[:3]:  # Check first 3 behaviors
                print(f"  - Behavior {behavior.behavior_id}: {behavior.tourist_id} -> {behavior.poi_id}")
                assert behavior.behavior_id.startswith("behavior_")
                assert behavior.duration_hours > 0
                assert len(behavior.activities) > 0
                
        except Exception as e:
            print(f"✗ Tourist behavior generation failed: {e}")
            return False
    else:
        print("⚠ Skipping behavior generation (no POI data available)")
    
    # Test 6: Test data export
    print("\n6. Testing data export...")
    try:
        # Create a temporary output directory
        test_output_dir = "test_tourist_output"
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Generate a small dataset for testing
        test_tourists = generator.generate_tourist_profiles(count=5)
        test_behaviors = []
        
        if generator.poi_data:
            test_behaviors = generator.generate_tourist_behaviors(test_tourists)
        
        # Save test data
        output_data = {
            'tourists': [tourist.__dict__ for tourist in test_tourists],
            'behaviors': [behavior.__dict__ for behavior in test_behaviors],
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_tourists': len(test_tourists),
                'total_behaviors': len(test_behaviors),
                'test_run': True
            }
        }
        
        json_path = os.path.join(test_output_dir, 'test_tourists_data.json')
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✓ Test data exported to {json_path}")
        
        # Clean up test directory
        import shutil
        shutil.rmtree(test_output_dir)
        print("✓ Test directory cleaned up")
        
    except Exception as e:
        print(f"✗ Data export failed: {e}")
        return False
    
    print("\n✓ All tests passed!")
    return True


def test_tourist_types():
    """Test different tourist types and their characteristics"""
    
    print("\nTesting Tourist Types...")
    
    generator = TouristGenerator()
    
    tourist_types = generator.tourist_types.keys()
    print(f"Available tourist types: {list(tourist_types)}")
    
    for tourist_type in tourist_types:
        print(f"\nTesting {tourist_type}:")
        config = generator.tourist_types[tourist_type]
        
        print(f"  - Percentage: {config['percentage']}%")
        print(f"  - Preferences: {config['preferences']}")
        print(f"  - Behavior patterns: {config['behavior_patterns']}")
        print(f"  - Demographics: {config['demographics']}")


def test_behavior_patterns():
    """Test behavior pattern generation"""
    
    print("\nTesting Behavior Patterns...")
    
    generator = TouristGenerator()
    
    # Test visit time generation
    print("Testing visit time generation:")
    for tourist_type in ['cultural_tourist', 'leisure_tourist', 'adventure_tourist']:
        tourist = Tourist(
            tourist_id="test_tourist",
            tourist_type=tourist_type,
            age=30,
            group_size=2,
            stay_duration=3,
            budget_level="medium",
            origin_country="United States",
            origin_city="New York",
            arrival_date="2024-01-01",
            departure_date="2024-01-04",
            preferences=[],
            behavior_patterns=[]
        )
        
        visit_time = generator._generate_visit_time(tourist)
        duration = generator._generate_visit_duration(tourist)
        
        print(f"  - {tourist_type}: {visit_time} ({duration} hours)")


def main():
    """Main test function"""
    
    print("Tourist Generator Test Suite")
    print("=" * 50)
    
    # Run basic functionality tests
    if not test_tourist_generator():
        print("\n✗ Basic functionality tests failed!")
        sys.exit(1)
    
    # Run tourist type tests
    test_tourist_types()
    
    # Run behavior pattern tests
    test_behavior_patterns()
    
    print("\n" + "=" * 50)
    print("✓ All tests completed successfully!")
    print("The tourist generator is working correctly.")


if __name__ == "__main__":
    main()
