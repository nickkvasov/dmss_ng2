#!/usr/bin/env python3
"""
Test script for POI ingestion system

Creates sample data and tests the ingestion process.
"""

import json
import tempfile
import os
from pathlib import Path
from poi_ingestor import POIIngestor


def create_sample_data():
    """Create sample POI data for testing"""
    sample_pois = [
        {
            "poi_id": "test_001",
            "name": "Central Park",
            "category": "parks",
            "lat": 40.7829,
            "lon": -73.9654,
            "address": "Central Park, New York, NY",
            "description": "Iconic urban park in Manhattan",
            "rating": 4.8,
            "opening_hours": "Open 24/7",
            "landmark_type": "park"
        },
        {
            "poi_id": "test_002",
            "name": "Metropolitan Museum of Art",
            "category": "museums",
            "lat": 40.7794,
            "lon": -73.9632,
            "address": "1000 5th Ave, New York, NY 10028",
            "description": "World-famous art museum",
            "rating": 4.7,
            "opening_hours": "10:00-17:30",
            "capacity": 5000
        },
        {
            "poi_id": "test_003",
            "name": "Times Square",
            "category": "landmarks",
            "lat": 40.7580,
            "lon": -73.9855,
            "address": "Times Square, New York, NY",
            "description": "Famous intersection and tourist destination",
            "rating": 4.5,
            "opening_hours": "Open 24/7"
        }
    ]
    
    return sample_pois


def test_data_validation():
    """Test data validation functionality"""
    print("Testing data validation...")
    
    ingestor = POIIngestor()
    
    # Test valid data
    valid_data = create_sample_data()
    validated = ingestor.validate_poi_data(valid_data)
    
    assert len(validated) == 3, f"Expected 3 valid records, got {len(validated)}"
    print("✓ Valid data validation passed")
    
    # Test invalid data
    invalid_data = [
        {
            "poi_id": "invalid_001",
            "name": "Invalid POI",
            # Missing required fields
        },
        {
            "poi_id": "invalid_002",
            "name": "Invalid Coordinates",
            "category": "test",
            "lat": 200.0,  # Invalid latitude
            "lon": -73.9654
        }
    ]
    
    validated_invalid = ingestor.validate_poi_data(invalid_data)
    assert len(validated_invalid) == 0, f"Expected 0 valid records, got {len(validated_invalid)}"
    print("✓ Invalid data validation passed")


def test_data_loading():
    """Test data loading functionality"""
    print("Testing data loading...")
    
    ingestor = POIIngestor()
    
    # Create temporary directory with sample data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample JSON file
        sample_data = create_sample_data()
        json_file = temp_path / "test_pois.json"
        
        with open(json_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        # Test loading
        loaded_data = ingestor.load_poi_data(temp_dir)
        
        assert len(loaded_data) == 3, f"Expected 3 loaded records, got {len(loaded_data)}"
        assert loaded_data[0]['poi_id'] == 'test_001'
        print("✓ Data loading passed")


def test_poi_type_extraction():
    """Test POI type extraction functionality"""
    print("Testing POI type extraction...")
    
    ingestor = POIIngestor()
    
    # Test data with different types
    test_pois = [
        {"poi_id": "test_001", "name": "Central Park", "category": "parks", "landmark_type": "park"},
        {"poi_id": "test_002", "name": "Met Museum", "category": "museums", "landmark_type": "museum"},
        {"poi_id": "test_003", "name": "Times Square", "category": "landmarks", "landmark_type": "landmark"},
        {"poi_id": "test_004", "name": "Restaurant", "category": "restaurants"}  # No landmark_type
    ]
    
    poi_types = ingestor.extract_poi_types(test_pois)
    
    # Should extract 4 types: park, museum, landmark, restaurants
    assert len(poi_types) == 4, f"Expected 4 POI types, got {len(poi_types)}"
    
    # Check specific types
    assert "type_park" in poi_types
    assert "type_museum" in poi_types
    assert "type_landmark" in poi_types
    assert "type_restaurants" in poi_types
    
    # Check type structure
    park_type = poi_types["type_park"]
    assert park_type["name"] == "park"
    assert park_type["category"] == "parks"
    
    print("✓ POI type extraction passed")


def main():
    """Run all tests"""
    print("Running POI ingestion tests...")
    print("=" * 50)
    
    try:
        test_data_validation()
        test_data_loading()
        test_poi_type_extraction()
        
        print("=" * 50)
        print("All tests passed! ✓")
        
    except Exception as e:
        print(f"Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
