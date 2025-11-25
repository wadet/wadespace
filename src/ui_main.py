"""
Wade Space Game - UI Entry Point

Launches the Pygame graphical interface.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui import launch_ui

if __name__ == '__main__':
    launch_ui()
