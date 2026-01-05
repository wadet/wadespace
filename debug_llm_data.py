#!/usr/bin/env python3
"""
Debug script to see what data the LLM is receiving.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine

def debug_llm_data():
    """Debug what data is being sent to the LLM."""
    print("=" * 60)
    print("Debugging LLM Data")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Get universe data with full search
    print("\n[1] Getting universe data with full search...")
    universe_data = engine._get_universe_data_for_llm(engine.player_ship, search_entire_universe=True)
    
    print(f"\nPlayer position: {universe_data['player_position']}")
    print(f"Search entire universe: {universe_data['search_entire_universe']}")
    print(f"Total objects found: {len(universe_data['nearby_objects'])}")
    
    # Count by type
    type_counts = {}
    for obj_id, obj_data in universe_data['nearby_objects']:
        obj_type = obj_data['type']
        type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
    
    print("\nObject counts by type:")
    for obj_type, count in sorted(type_counts.items()):
        print(f"  {obj_type}: {count}")
    
    # Find starbases
    print("\n[2] Looking for starbases...")
    starbases = [(obj_id, obj_data) for obj_id, obj_data in universe_data['nearby_objects'] 
                 if obj_data['type'] == 'Starbase']
    
    print(f"Found {len(starbases)} starbases")
    
    # Show first few
    print("\nFirst 5 starbases:")
    for obj_id, obj_data in starbases[:5]:
        friendly = obj_data.get('friendly', True)
        status = 'FRIENDLY' if friendly else 'HOSTILE'
        print(f"  {obj_id} ({status}): Distance {obj_data['distance']:.1f} AU")
    
    # Find nearest enemy starbase
    enemy_starbases = [(obj_id, obj_data) for obj_id, obj_data in starbases 
                       if not obj_data.get('friendly', True)]
    
    if enemy_starbases:
        nearest_enemy = min(enemy_starbases, key=lambda x: x[1]['distance'])
        print(f"\nNearest ENEMY starbase:")
        print(f"  {nearest_enemy[0]}: Distance {nearest_enemy[1]['distance']:.1f} AU")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_llm_data()
