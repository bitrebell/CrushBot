#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test runner for CrushBot
Discovers and runs all tests
"""

import unittest
import logging

# Disable logging during tests
logging.disable(logging.CRITICAL)

if __name__ == "__main__":
    print("Running CrushBot tests...")
    
    # Discover and run all tests
    test_suite = unittest.defaultTestLoader.discover('tests')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    if result.wasSuccessful():
        print("\nAll tests passed!")
        exit(0)
    else:
        print(f"\nTests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        exit(1) 