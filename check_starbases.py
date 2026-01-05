#!/usr/bin/env python3
"""
Test script to check starbase distribution in the universe.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Prevent UI from launching

from src.game_engine import GameEngine
from src.universe_objects import Starbase

def check_starbases():
    """Check starbase locations and types."""
    print("=" * 60)
    print("Checking Starbase Distribution")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    player_pos = engine.player_ship.position
    
    print(f"\nPlayer position: ({player_pos.x:.1f}, {player_pos.y:.1f})")
    
    # Find all starbases
    starbases = [(obj_id, obj) for obj_id, obj in engine.universe_objects.items() 
                 if isinstance(obj, Starbase)]
    
    print(f"\nTotal starbases in universe: {len(starbases)}")
    
    # Separate by type
    friendly = []
    hostile = []
    
    for sb_id, sb in starbases:
        distance = player_pos.distance_to(sb.position)
        if sb.friendly_to_player:
            friendly.append((sb_id, sb, distance))
        else:
            hostile.append((sb_id, sb, distance))
    
    print(f"  Friendly: {len(friendly)}")
    print(f"  Hostile:  {len(hostile)}")
    
    # Find nearest of each type
    if friendly:
        friendly.sort(key=lambda x: x[2])
        nearest_friendly = friendly[0]
        print(f"\nNearest FRIENDLY starbase:")
        print(f"  ID: {nearest_friendly[0]}")
        print(f"  Position: ({nearest_friendly[1].position.x:.1f}, {nearest_friendly[1].position.y:.1f})")
        print(f"  Distance: {nearest_friendly[2]:.1f} AU")
    
    if hostile:
        hostile.sort(key=lambda x: x[2])
        nearest_hostile = hostile[0]
        print(f"\nNearest HOSTILE/ENEMY starbase:")
        print(f"  ID: {nearest_hostile[0]}")
        print(f"  Position: ({nearest_hostile[1].position.x:.1f}, {nearest_hostile[1].position.y:.1f})")
        print(f"  Distance: {nearest_hostile[2]:.1f} AU")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_starbases()
