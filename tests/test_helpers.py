"""
Test helper functions for CrushBot
"""

import unittest
from utils.helpers import parse_duration, get_readable_time

class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions."""
    
    def test_parse_duration(self):
        """Test parse_duration function."""
        # Test valid duration strings
        self.assertEqual(parse_duration('1m'), 60)
        self.assertEqual(parse_duration('2h'), 7200)
        self.assertEqual(parse_duration('1d'), 86400)
        self.assertEqual(parse_duration('1w'), 604800)
        
        # Test invalid duration strings
        self.assertIsNone(parse_duration(''))
        self.assertIsNone(parse_duration('invalid'))
        self.assertIsNone(parse_duration('1x'))
        
    def test_get_readable_time(self):
        """Test get_readable_time function."""
        # Test various durations
        self.assertEqual(get_readable_time(60), "1 minute")
        self.assertEqual(get_readable_time(120), "2 minutes")
        self.assertEqual(get_readable_time(3600), "1 hour")
        self.assertEqual(get_readable_time(3661), "1 hour, 1 minute, 1 second")
        self.assertEqual(get_readable_time(86400), "1 day")
        self.assertEqual(get_readable_time(604800), "1 week")
        self.assertEqual(get_readable_time(694861), "1 week, 1 day, 1 hour, 1 minute, 1 second")
        
        # Test edge cases
        self.assertEqual(get_readable_time(0), "0 seconds")
        self.assertEqual(get_readable_time(-1), "0 seconds")

if __name__ == '__main__':
    unittest.main() 