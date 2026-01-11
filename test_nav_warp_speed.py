#!/usr/bin/env python3
"""Test nav command with custom warp speed."""

import sys
sys.path.insert(0, 'src')

from command_parser import CommandParser
from ship import Ship
from universe_objects import Position

def test_nav_parsing():
    """Test that the command parser correctly extracts warp speed from nav commands."""
    parser = CommandParser()
    
    print("Testing nav command parsing...")
    print("-" * 60)
    
    # Test cases
    test_cases = [
        ("nav st1234", "st1234", None),
        ("nav st1234, 5", "st1234", 5),
        ("nav st1234 5", "st1234", 5),
        ("nav st1234,7", "st1234", 7),
        ("navigate to st1234", "st1234", None),
        ("navigate to st1234, 6", "st1234", 6),
        ("navigate to st1234 6", "st1234", 6),
        ("go to st1234", "st1234", None),
        ("go to st1234, 8", "st1234", 8),
        ("go to st1234 8", "st1234", 8),
        ("nav s1 9", "s1", 9),
        ("nav s1, 4", "s1", 4),
    ]
    
    all_passed = True
    for command_text, expected_id, expected_speed in test_cases:
        result = parser.parse(command_text)
        
        if result and result.get('command') == 'nav':
            target_id = result.get('target_id')
            warp_speed = result.get('warp_speed')
            
            passed = (target_id == expected_id and warp_speed == expected_speed)
            status = "✓ PASS" if passed else "✗ FAIL"
            
            print(f"{status}: '{command_text}'")
            print(f"  Expected: target_id={expected_id}, warp_speed={expected_speed}")
            print(f"  Got:      target_id={target_id}, warp_speed={warp_speed}")
            
            if not passed:
                all_passed = False
        else:
            print(f"✗ FAIL: '{command_text}' - Failed to parse as nav command")
            all_passed = False
        
        print()
    
    print("-" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    return all_passed

def test_ship_field():
    """Test that the Ship class has the auto_nav_warp_speed field."""
    print("\nTesting Ship class field...")
    print("-" * 60)
    
    ship = Ship("test_ship", Position(5000, 5000))
    
    # Check if field exists
    if hasattr(ship, 'auto_nav_warp_speed'):
        print("✓ PASS: Ship has auto_nav_warp_speed field")
        print(f"  Initial value: {ship.auto_nav_warp_speed}")
        
        # Test setting values
        ship.auto_nav_warp_speed = 5.0
        print(f"  After setting to 5.0: {ship.auto_nav_warp_speed}")
        
        ship.auto_nav_warp_speed = None
        print(f"  After clearing: {ship.auto_nav_warp_speed}")
        
        print("-" * 60)
        return True
    else:
        print("✗ FAIL: Ship missing auto_nav_warp_speed field")
        print("-" * 60)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Nav Command Custom Warp Speed Test")
    print("=" * 60)
    print()
    
    test1_passed = test_nav_parsing()
    test2_passed = test_ship_field()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
