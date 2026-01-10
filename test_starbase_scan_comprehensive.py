#!/usr/bin/env python3
"""Comprehensive test for starbase scan display."""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine

def test_starbase_scan_comprehensive():
    """Test scanning starbases with different conditions."""
    print("=" * 70)
    print("Comprehensive Starbase Scan Test")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    player_ship = engine.player_ship
    
    # Find starbases
    from src.universe_objects import Starbase
    starbases = [(obj_id, obj) for obj_id, obj in engine.universe_objects.items() 
                 if isinstance(obj, Starbase)]
    
    if len(starbases) < 3:
        print("Not enough starbases for test!")
        return
    
    # Setup 3 test starbases with different conditions
    test_cases = [
        ("Friendly, Full Health", 'friendly', 0.0, 100.0, 500),
        ("Hostile, Damaged", 'hostile', 45.0, 60.0, 250),
        ("Neutral, Low Energy", 'neutral', 10.0, 30.0, 450),
    ]
    
    for i, (desc, stance, damage, energy, torpedos) in enumerate(test_cases):
        sb_id, sb = starbases[i]
        
        # Position near player
        sb.position.x = player_ship.position.x + 20.0 + (i * 5)
        sb.position.y = player_ship.position.y + 10.0 + (i * 5)
        
        # Set conditions
        sb.stances[player_ship.id] = stance
        sb.damage = damage
        sb.energy = energy
        sb.torpedos = torpedos
        sb.shields = 100.0 - damage  # Shields correlate with damage
        
        distance = player_ship.position.distance_to(sb.position)
        
        print(f"\nTest Case {i+1}: {desc}")
        print(f"  Starbase ID: {sb_id}")
        print(f"  Distance: {distance:.1f} AU")
        print("-" * 70)
        
        engine.messages.clear()
        engine._execute_scan(player_ship, sb_id)
        
        for msg in engine.messages:
            print(f"  {msg}")
        
        # Verify all expected fields are present
        scan_output = '\n'.join(engine.messages)
        checks = {
            'Distance': 'AU' in scan_output,
            'Status': 'Status:' in scan_output,
            'Damage': 'Damage:' in scan_output,
            'Energy': 'Energy:' in scan_output,
            'Shields': 'Shields:' in scan_output,
            'Torpedos': 'Torpedos:' in scan_output,
            'Service range': 'Service range:' in scan_output,
            'Defense range': 'Defense range:' in scan_output,
            'Stance': 'Stance:' in scan_output,
        }
        
        print("\n  Field verification:")
        all_passed = True
        for field, present in checks.items():
            status = "✓" if present else "✗"
            print(f"    {status} {field}")
            if not present:
                all_passed = False
        
        if all_passed:
            print(f"  ✓ Test case {i+1} PASSED")
        else:
            print(f"  ✗ Test case {i+1} FAILED")
    
    print("\n" + "=" * 70)
    print("✓ Comprehensive starbase scan test complete!")
    print("=" * 70)

if __name__ == '__main__':
    test_starbase_scan_comprehensive()
