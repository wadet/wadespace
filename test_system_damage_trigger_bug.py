#!/usr/bin/env python3
"""
Test to verify the system damage triggering bug.
Issue: System damage should trigger when damage >50% after taking hit,
but currently only triggers if damage was >50% BEFORE taking hit.
"""

import sys
sys.path.insert(0, '/home/wade/workspace/wadespace')

import random
from src.ship import Ship
from src.universe_objects import Position

def test_crossing_50_percent_threshold():
    """Test system damage when crossing the 50% threshold"""
    print("="*70)
    print("TEST: System Damage When Crossing 50% Threshold")
    print("="*70)
    
    # Set seed for reproducibility
    random.seed(12345)
    
    ship = Ship("test001", Position(5000, 5000))
    ship.is_player = True
    ship.damage = 45.0  # Below 50%
    ship.shields = 0  # No shields to simplify
    messages = []
    
    print(f"\nInitial state:")
    print(f"  Damage: {ship.damage}%")
    print(f"  Disabled systems: {ship.disabled_systems}")
    
    # Apply damage that will bring ship above 50%
    print(f"\nApplying 10% damage (will bring to 55%)...")
    ship.take_damage(10.0, bypass_shields=True, messages=messages)
    
    print(f"  New damage: {ship.damage}%")
    print(f"  Disabled systems: {ship.disabled_systems}")
    print(f"  Messages: {messages}")
    
    # Try multiple times to see if it ever triggers
    attempts = 50
    system_failures = 0
    
    print(f"\n\nTrying {attempts} more times with ship at {ship.damage}% damage...")
    for i in range(attempts):
        # Reset for each attempt
        ship.damage = 45.0
        ship.disabled_systems.clear()
        messages = []
        
        # Apply damage
        ship.take_damage(10.0, bypass_shields=True, messages=messages)
        
        if ship.disabled_systems:
            system_failures += 1
    
    print(f"  System failures triggered: {system_failures}/{attempts}")
    
    if system_failures == 0:
        print("\n✗ BUG CONFIRMED: No system failures when crossing 50% threshold")
        return False
    else:
        print(f"\n✓ System damage working: {system_failures} failures observed")
        return True


def test_already_above_50_percent():
    """Test system damage when already above 50%"""
    print("\n\n" + "="*70)
    print("TEST: System Damage When Already Above 50%")
    print("="*70)
    
    # Set seed for reproducibility
    random.seed(12345)
    
    ship = Ship("test002", Position(5000, 5000))
    ship.is_player = True
    ship.damage = 55.0  # Already above 50%
    ship.shields = 0  # No shields to simplify
    messages = []
    
    print(f"\nInitial state:")
    print(f"  Damage: {ship.damage}%")
    print(f"  Disabled systems: {ship.disabled_systems}")
    
    # Try multiple times
    attempts = 50
    system_failures = 0
    
    print(f"\nTrying {attempts} damage applications with ship at {ship.damage}% damage...")
    for i in range(attempts):
        # Reset for each attempt (but keep damage above 50%)
        ship.damage = 55.0
        ship.disabled_systems.clear()
        messages = []
        
        # Apply damage
        ship.take_damage(5.0, bypass_shields=True, messages=messages)
        
        if ship.disabled_systems:
            system_failures += 1
    
    print(f"  System failures triggered: {system_failures}/{attempts}")
    print(f"  Expected: ~{int(attempts * 0.25)} (25% chance)")
    
    if system_failures > 0:
        print(f"\n✓ System damage working when already above 50%")
        return True
    else:
        print(f"\n✗ System damage not working even when above 50%")
        return False


if __name__ == "__main__":
    test1 = test_crossing_50_percent_threshold()
    test2 = test_already_above_50_percent()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Crossing 50% threshold: {'✓ PASS' if test1 else '✗ FAIL (BUG FOUND)'}")
    print(f"Already above 50%: {'✓ PASS' if test2 else '✗ FAIL'}")
    
    if not test1:
        print("\n" + "="*70)
        print("BUG IDENTIFIED:")
        print("System damage does not trigger when ship first crosses 50% threshold.")
        print("It only triggers on subsequent hits after already being above 50%.")
        print("="*70)
