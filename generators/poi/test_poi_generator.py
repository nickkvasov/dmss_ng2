"""
Test suite for POI Generator

Tests the POI generator functionality including data generation,
configuration loading, and output formatting.
"""

import unittest
import tempfile
import os
import json
import csv
from poi_generator import POIGenerator, POI


class TestPOIGenerator(unittest.TestCase):
    """Test cases for POI Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = POIGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_poi_dataclass(self):
        """Test POI dataclass creation"""
        poi = POI(
            poi_id="test-id",
            category="attractions",
            name="Test Museum",
            lat=40.7614,
            lon=-73.9776,
            address="123 Test St",
            capacity=1000,
            rating=4.5,
            opening_hours="9:00-17:00"
        )
        
        self.assertEqual(poi.poi_id, "test-id")
        self.assertEqual(poi.category, "attractions")
        self.assertEqual(poi.name, "Test Museum")
        self.assertEqual(poi.lat, 40.7614)
        self.assertEqual(poi.lon, -73.9776)
        self.assertEqual(poi.capacity, 1000)
        self.assertEqual(poi.rating, 4.5)
    
    def test_generator_initialization(self):
        """Test generator initialization with default config"""
        self.assertIsNotNone(self.generator.config)
        self.assertIn('city_bounds', self.generator.config)
        self.assertIn('poi_categories', self.generator.config)
        self.assertIn('attractions', self.generator.poi_categories)
        self.assertIn('hotels', self.generator.poi_categories)
        self.assertIn('restaurants', self.generator.poi_categories)
        self.assertIn('venues', self.generator.poi_categories)
    
    def test_coordinate_generation(self):
        """Test coordinate generation within city bounds"""
        lat, lon = self.generator._generate_coordinates()
        
        # Check coordinates are within NYC bounds
        self.assertGreaterEqual(lat, 40.7)
        self.assertLessEqual(lat, 40.8)
        self.assertGreaterEqual(lon, -74.0)
        self.assertLessEqual(lon, -73.9)
    
    def test_name_generation(self):
        """Test POI name generation for different categories"""
        # Test attractions
        name = self.generator._generate_name('attractions')
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        
        # Test hotels
        name = self.generator._generate_name('hotels')
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        
        # Test restaurants
        name = self.generator._generate_name('restaurants')
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
    
    def test_poi_properties_generation(self):
        """Test POI properties generation for different categories"""
        # Test attractions properties
        props = self.generator._generate_poi_properties('attractions')
        self.assertIn('capacity', props)
        self.assertIn('rating', props)
        self.assertIn('opening_hours', props)
        self.assertIn('address', props)
        self.assertGreaterEqual(props['capacity'], 100)
        self.assertLessEqual(props['capacity'], 2000)
        self.assertGreaterEqual(props['rating'], 3.0)
        self.assertLessEqual(props['rating'], 5.0)
        
        # Test hotels properties
        props = self.generator._generate_poi_properties('hotels')
        self.assertEqual(props['opening_hours'], '24/7')
        self.assertGreaterEqual(props['capacity'], 50)
        self.assertLessEqual(props['capacity'], 500)
    
    def test_single_poi_generation(self):
        """Test single POI generation"""
        poi = self.generator.generate_poi('attractions')
        
        self.assertIsInstance(poi, POI)
        self.assertIsInstance(poi.poi_id, str)
        self.assertEqual(poi.category, 'attractions')
        self.assertIsInstance(poi.name, str)
        self.assertIsInstance(poi.lat, float)
        self.assertIsInstance(poi.lon, float)
        self.assertIsInstance(poi.address, str)
        self.assertIsInstance(poi.capacity, int)
        self.assertIsInstance(poi.rating, float)
        self.assertIsInstance(poi.opening_hours, str)
    
    def test_multiple_pois_generation(self):
        """Test multiple POIs generation"""
        pois = self.generator.generate_pois('attractions')
        
        self.assertIsInstance(pois, list)
        self.assertEqual(len(pois), 50)  # Default count for attractions
        
        for poi in pois:
            self.assertIsInstance(poi, POI)
            self.assertEqual(poi.category, 'attractions')
    
    def test_all_categories_generation(self):
        """Test generation of POIs for all categories"""
        pois = self.generator.generate_pois()
        
        self.assertIsInstance(pois, list)
        self.assertGreater(len(pois), 0)
        
        categories = set(poi.category for poi in pois)
        expected_categories = {'attractions', 'hotels', 'restaurants', 'venues'}
        self.assertEqual(categories, expected_categories)
    
    def test_invalid_category(self):
        """Test error handling for invalid category"""
        with self.assertRaises(ValueError):
            self.generator.generate_pois('invalid_category')
    
    def test_json_output(self):
        """Test JSON output functionality"""
        pois = self.generator.generate_pois('attractions')
        output_path = os.path.join(self.temp_dir, 'test_pois.json')
        
        self.generator.save_to_json(pois, output_path)
        
        # Verify file exists and contains valid JSON
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(pois))
        
        # Check first POI structure
        first_poi = data[0]
        self.assertIn('poi_id', first_poi)
        self.assertIn('category', first_poi)
        self.assertIn('name', first_poi)
        self.assertIn('lat', first_poi)
        self.assertIn('lon', first_poi)
    
    def test_csv_output(self):
        """Test CSV output functionality"""
        pois = self.generator.generate_pois('attractions')
        output_path = os.path.join(self.temp_dir, 'test_pois.csv')
        
        self.generator.save_to_csv(pois, output_path)
        
        # Verify file exists and contains valid CSV
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), len(pois))
        
        # Check CSV structure
        if rows:
            first_row = rows[0]
            self.assertIn('poi_id', first_row)
            self.assertIn('category', first_row)
            self.assertIn('name', first_row)
            self.assertIn('lat', first_row)
            self.assertIn('lon', first_row)
    
    def test_custom_config(self):
        """Test generator with custom configuration"""
        # Create temporary config file
        config_content = """
city_bounds:
  name: "Test City"
  min_lat: 0.0
  max_lat: 1.0
  min_lon: 0.0
  max_lon: 1.0

poi_categories:
  test_category:
    count: 5
    templates:
      - "Test {name}"
"""
        config_path = os.path.join(self.temp_dir, 'test_config.yaml')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Initialize generator with custom config
        custom_generator = POIGenerator(config_path)
        
        # Test coordinate generation with custom bounds
        lat, lon = custom_generator._generate_coordinates()
        self.assertGreaterEqual(lat, 0.0)
        self.assertLessEqual(lat, 1.0)
        self.assertGreaterEqual(lon, 0.0)
        self.assertLessEqual(lon, 1.0)
        
        # Test POI generation with custom category
        pois = custom_generator.generate_pois('test_category')
        self.assertEqual(len(pois), 5)
        for poi in pois:
            self.assertEqual(poi.category, 'test_category')


if __name__ == '__main__':
    unittest.main()
