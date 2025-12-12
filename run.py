#!/usr/bin/env python3
"""
Root-level launcher script for Emergency Traffic AI System.
This script adds the src directory to the Python path and runs the main application.
"""

import sys
import os

# Add src directory to Python path so imports work correctly
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Import and run the main module
from main import main_loop

if __name__ == '__main__':
    main_loop()
