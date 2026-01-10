#!/usr/bin/env python3
"""Test HAL query for starbases."""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine

def test_hal_starbase_query():
    """Test HAL query for starbase information."""
    print("=" * 70)
    print("Testing HAL Starbase Query")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    player_ship = engine.player_ship
    
    # Find and setup a starbase
    from src.universe_objects import Starbase
    starbases = [(obj_id, obj) for obj_id, obj in engine.universe_objects.items() 
                 if isinstance(obj, Starbase)]
    
    if not starbases:
        print("No starbases found!")
        return
    
    sb_id, sb = starbases[0]
    sb.position.x = player_ship.position.x + 25.0
    sb.position.y = player_ship.position.y + 15.0
    sb.stances[player_ship.id] = 'hostile'
    sb.damage = 20.0
    sb.energy = 75.0
    
    print(f"\nTest starbase: {sb_id}")
    print(f"  Position: ({sb.position.x:.1f}, {sb.position.y:.1f})")
    print(f"  Stance: hostile")
    print(f"  Damage: 20.0%")
    print(f"  Energy: 75.0%")
    
    print("\n" + "=" * 70)
    print(f"HAL Query: 'what is {sb_id}'")
    print("=" * 70)
    
    engine.messages.clear()
    engine._query_object_info(f"what is {sb_id}")
    
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Verify expected fields
    hal_output = '\n'.join(engine.messages)
    checks = {
        'Object ID': sb_id in hal_output,
        'Type': 'Starbase' in hal_output,
        'Location': 'Location:' in hal_output,
        'Distance': 'Distance' in hal_output,
        'Stance': 'Stance:' in hal_output,
    }
    
    print("\n" + "-" * 70)
    print("Field verification:")
    all_passed = True
    for field, present in checks.items():
        status = "✓" if present else "✗"
        print(f"  {status} {field}")
        if not present:
            all_passed = False
    
    if all_passed:
        print("\n✓ HAL starbase query works correctly!")
    else:
        print("\n✗ HAL starbase query has issues!")
    
    print("=" * 70)

if __name__ == '__main__':
    test_hal_starbase_query()
