#!/usr/bin/env python3
"""
Quick verification script for Wade Space UI
Tests that all imports work and basic UI initialization succeeds
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import pygame
        print(f"✓ pygame {pygame.__version__}")
    except ImportError as e:
        print(f"✗ pygame import failed: {e}")
        return False
    
    try:
        from src.game_engine import GameEngine
        print("✓ GameEngine")
    except ImportError as e:
        print(f"✗ GameEngine import failed: {e}")
        return False
    
    try:
        from src.command_parser import CommandParser
        print("✓ CommandParser")
    except ImportError as e:
        print(f"✗ CommandParser import failed: {e}")
        return False
    
    try:
        from src.ui import GameUI
        print("✓ GameUI")
    except ImportError as e:
        print(f"✗ GameUI import failed: {e}")
        return False
    
    try:
        from src.effects import EffectManager
        print("✓ EffectManager")
    except ImportError as e:
        print(f"✗ EffectManager import failed: {e}")
        return False
    
    return True

def test_ui_initialization():
    """Test UI initialization without creating window"""
    print("\nTesting UI initialization...")
    
    try:
        from src.game_engine import GameEngine
        from src.ui import GameUI
        import os
        
        # Check if display available
        if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            print("⚠ No display detected - skipping window creation test")
            print("  (UI requires X11 or Wayland)")
            return True
        
        print("✓ Initializing game engine...")
        engine = GameEngine()
        
        print("✓ Creating UI (may open window)...")
        # This will open a window if display available
        ui = GameUI(engine)
        print("✓ UI created successfully")
        
        # Clean up
        import pygame
        pygame.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ UI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Wade Space UI Verification")
    print("=" * 40)
    
    if not test_imports():
        print("\n✗ Import test failed")
        return 1
    
    if not test_ui_initialization():
        print("\n✗ Initialization test failed")
        return 1
    
    print("\n" + "=" * 40)
    print("✓ All tests passed!")
    print("\nYou can now run: python -m src.ui_main")
    return 0

if __name__ == "__main__":
    sys.exit(main())
