#!/usr/bin/env python3
"""Test script to verify starbase scan display."""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine

def test_starbase_scan():
    """Test scanning a starbase to see what statistics are displayed."""
    print("=" * 70)
    print("Testing Starbase Scan Display")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    player_ship = engine.player_ship
    
    # Find a nearby starbase
    from src.universe_objects import Starbase
    starbases = [(obj_id, obj, player_ship.position.distance_to(obj.position)) 
                 for obj_id, obj in engine.universe_objects.items() 
                 if isinstance(obj, Starbase)]
    
    if not starbases:
        print("No starbases found!")
        return
    
    # Sort by distance
    starbases.sort(key=lambda x: x[2])
    
    # Find one within sensor range
    sb_id, sb, distance = None, None, None
    for sid, s, dist in starbases[:10]:
        if dist <= player_ship.sensors.sensor_range:
            sb_id, sb, distance = sid, s, dist
            break
    
    if sb_id is None:
        # Move a starbase closer
        sb_id, sb, _ = starbases[0]
        sb.position.x = player_ship.position.x + 20.0
        sb.position.y = player_ship.position.y + 10.0
        distance = player_ship.position.distance_to(sb.position)
        print(f"Moved starbase {sb_id} closer to {distance:.1f} AU")
    
    print(f"\nStarbase to scan: {sb_id} at {distance:.1f} AU")
    print(f"Starbase properties:")
    print(f"  - Shields: {sb.shields}")
    print(f"  - Damage: {sb.damage}")
    print(f"  - Energy: {sb.energy}")
    print(f"  - Torpedos: {sb.torpedos}/{sb.max_torpedos}")
    print(f"  - Service range: {sb.service_range} AU")
    print(f"  - Defense range: {sb.defense_range} AU")
    print(f"  - Stance: {sb.stances.get(player_ship.id, 'neutral')}")
    
    print("\n" + "=" * 70)
    print(f"Scanning starbase {sb_id}...")
    print("=" * 70)
    
    engine.messages.clear()
    engine._execute_scan(player_ship, sb_id)
    
    print("\nCurrent scan output:")
    for msg in engine.messages:
        print(f"  {msg}")
    
    print("\n" + "=" * 70)
    print("ISSUE: Starbase scan only shows ID, symbol, and distance.")
    print("EXPECTED: Should also show shields, damage, energy, torpedos, stance, etc.")
    print("=" * 70)

if __name__ == '__main__':
    test_starbase_scan()
