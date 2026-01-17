#!/usr/bin/env python3
"""
Comprehensive test demonstrating the system damage fix.
Shows that system damage now correctly triggers when crossing 50% threshold.
"""

import sys
sys.path.insert(0, '/home/wade/workspace/wadespace')

import random
from src.ship import Ship
from src.universe_objects import Position

def main():
    print("="*70)
    print("System Damage Comprehensive Test - Demonstrating the Fix")
    print("="*70)
    
    # Set seed for reproducibility
    random.seed(99999)
    
    ship = Ship("USS Test", Position(5000, 5000))
    ship.is_player = True
    ship.shields = 0  # Disable shields for simplicity
    
    print("\nScenario: Ship gradually takes damage and crosses 50% threshold\n")
    
    # Start at 30% damage
    ship.damage = 30.0
    print(f"Initial damage: {ship.damage}%")
    print(f"Disabled systems: {ship.disabled_systems or 'None'}\n")
    
    # Take damage to 40%
    print("Taking 10% damage...")
    messages = []
    ship.take_damage(10.0, bypass_shields=True, messages=messages)
    print(f"  Damage: {ship.damage}%")
    print(f"  Disabled systems: {ship.disabled_systems or 'None'}")
    print(f"  Messages: {messages or 'None'}\n")
    
    # Take damage to 50% exactly
    print("Taking 10% damage...")
    messages = []
    ship.take_damage(10.0, bypass_shields=True, messages=messages)
    print(f"  Damage: {ship.damage}%")
    print(f"  Disabled systems: {ship.disabled_systems or 'None'}")
    print(f"  Messages: {messages or 'None'}\n")
    
    # Cross the threshold to 60%
    print("Taking 10% damage (CROSSING 50% THRESHOLD)...")
    messages = []
    ship.take_damage(10.0, bypass_shields=True, messages=messages)
    print(f"  Damage: {ship.damage}%")
    print(f"  Disabled systems: {ship.disabled_systems or 'None'}")
    print(f"  Messages: {messages or 'None'}")
    
    if ship.disabled_systems:
        print(f"\n✓ SUCCESS: System damage triggered when crossing 50% threshold!")
        print(f"  System failed: {list(ship.disabled_systems)[0]}")
    else:
        print(f"\n  No system failure this time (25% chance)")
    
    # Continue taking damage
    print(f"\n\nContinuing to take damage while above 50%...")
    for i in range(5):
        messages = []
        ship.take_damage(5.0, bypass_shields=True, messages=messages)
        print(f"\n  Hit {i+1}: Damage now {ship.damage}%")
        if messages:
            for msg in messages:
                if 'CRITICAL' in msg:
                    print(f"    → {msg}")
        print(f"    Disabled systems: {ship.disabled_systems or 'None'}")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
    print(f"\nFinal state:")
    print(f"  Total damage: {ship.damage}%")
    print(f"  Disabled systems: {len(ship.disabled_systems)}")
    for system in sorted(ship.disabled_systems):
        print(f"    - {system}")
    
    if ship.disabled_systems:
        print(f"\n✓ System damage mechanic is working correctly!")
    else:
        print(f"\n  No systems disabled (rare but possible with 25% chance)")

if __name__ == "__main__":
    main()
