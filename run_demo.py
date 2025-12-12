#!/usr/bin/env python3
"""
Root-level launcher script for Emergency Traffic AI Demo.
This script adds the src directory to the Python path and runs the demo application.
"""

import sys
import os

# Add src directory to Python path so imports work correctly
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Import and run the demo module
import demo

if __name__ == '__main__':
    demo.main()
