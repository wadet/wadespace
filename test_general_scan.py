#!/usr/bin/env python3
"""Test general scan command to ensure it still works."""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine

def test_general_scan():
    """Test general scan command."""
    print("=" * 70)
    print("Testing General Scan Command")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    player_ship = engine.player_ship
    
    # Move some objects close
    from src.universe_objects import Starbase
    
    objects = list(engine.universe_objects.items())[:3]
    for i, (obj_id, obj) in enumerate(objects):
        obj.position.x = player_ship.position.x + 10.0 + (i * 5)
        obj.position.y = player_ship.position.y + 5.0
        if isinstance(obj, Starbase):
            obj.stances[player_ship.id] = ['friendly', 'hostile', 'neutral'][i % 3]
    
    # Move some NPC ships close
    npc_list = list(engine.npc_ships.items())[:2]
    for i, (npc_id, npc) in enumerate(npc_list):
        npc.position.x = player_ship.position.x + 20.0 + (i * 10)
        npc.position.y = player_ship.position.y - 5.0
        npc.stances[player_ship.id] = ['friendly', 'hostile'][i % 2]
        npc.behavior_trait = ['aggressive', 'timid'][i % 2]
    
    print("\nExecuting general scan command...")
    print("-" * 70)
    
    engine.messages.clear()
    engine._execute_scan(player_ship)
    
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Verify output format
    scan_output = '\n'.join(engine.messages)
    has_objects = "Scan results" in scan_output
    has_distances = "AU" in scan_output
    has_stance_info = "[" in scan_output and "]" in scan_output
    
    print("\n" + "-" * 70)
    print("Verification:")
    print(f"  {'✓' if has_objects else '✗'} Scan results header present")
    print(f"  {'✓' if has_distances else '✗'} Distance information present")
    print(f"  {'✓' if has_stance_info else '✗'} Stance/behavior info present")
    
    if has_objects and has_distances and has_stance_info:
        print("\n✓ General scan command works correctly!")
    else:
        print("\n✗ General scan command has issues!")
    
    print("=" * 70)

if __name__ == '__main__':
    test_general_scan()
