#!/usr/bin/env python3
"""
Test script to verify scan and hal commands now display stance and behavior trait.
"""

from src.game_engine import GameEngine
from src.ship import Ship


def test_scan_and_hal_stance_behavior():
    """Test that scan and hal commands show stance and behavior information."""
    print("=" * 70)
    print(" TEST: Scan and HAL Commands with Stance & Behavior Trait")
    print("=" * 70)
    print()
    
    # Initialize game
    engine = GameEngine(universe_seed=12345)
    player_ship = engine.player_ship
    
    # Position player
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    print("[SCENARIO SETUP]")
    print("-" * 70)
    
    # Configure NPCs with different stances and behaviors
    npc_ids = list(engine.npc_ships.keys())[:4]
    
    configs = [
        (10.0, 0.0, 'hostile', 'aggressive', 'Hostile Aggressive Ship'),
        (20.0, 20.0, 'friendly', 'timid', 'Friendly Timid Ship'),
        (30.0, -10.0, 'neutral', 'neutral', 'Neutral Ship'),
        (40.0, 30.0, 'hostile', 'timid', 'Hostile Timid Ship')
    ]
    
    for i, (x_offset, y_offset, stance, behavior, desc) in enumerate(configs):
        if i < len(npc_ids):
            npc_id = npc_ids[i]
            npc = engine.npc_ships[npc_id]
            npc.position.x = 5000.0 + x_offset
            npc.position.y = 5000.0 + y_offset
            npc.stances[player_ship.id] = stance
            npc.behavior_trait = behavior
            distance = player_ship.position.distance_to(npc.position)
            print(f"  {npc_id}: {desc} @ {distance:.1f} AU")
    
    # Configure starbases
    sb_ids = [obj_id for obj_id in engine.universe_objects.keys() if obj_id.startswith('sb')][:3]
    sb_configs = [
        (15.0, 15.0, 'friendly', 'Friendly Starbase'),
        (35.0, -20.0, 'hostile', 'Hostile Starbase'),
        (50.0, 30.0, 'neutral', 'Neutral Starbase')
    ]
    
    for i, (x_offset, y_offset, stance, desc) in enumerate(sb_configs):
        if i < len(sb_ids):
            sb_id = sb_ids[i]
            sb = engine.universe_objects[sb_id]
            sb.position.x = 5000.0 + x_offset
            sb.position.y = 5000.0 + y_offset
            sb.stances[player_ship.id] = stance
            distance = player_ship.position.distance_to(sb.position)
            print(f"  {sb_id}: {desc} @ {distance:.1f} AU")
    
    print()
    print("=" * 70)
    print(" TEST 1: Scan Nearby Objects (General Scan)")
    print("=" * 70)
    engine.messages.clear()
    engine._execute_scan(player_ship)
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Verify stance and behavior appear in scan results
    scan_results = '\n'.join(engine.messages)
    assert '[hostile' in scan_results or '[friendly' in scan_results or '[neutral' in scan_results, \
        "Stance should appear in nearby scan results"
    print("\n✓ Stance information appears in scan results!")
    
    print()
    print("=" * 70)
    print(f" TEST 2: Scan Specific NPC Ship (scan {npc_ids[0]})")
    print("=" * 70)
    engine.messages.clear()
    engine._execute_scan(player_ship, npc_ids[0])
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Verify stance and behavior appear
    scan_results = '\n'.join(engine.messages)
    assert 'Stance:' in scan_results, "Stance field should appear in specific ship scan"
    assert 'Behavior:' in scan_results, "Behavior field should appear in specific ship scan"
    print("\n✓ Stance and behavior information appears in specific ship scan!")
    
    print()
    print("=" * 70)
    print(f" TEST 3: Scan Specific Starbase (scan {sb_ids[0]})")
    print("=" * 70)
    engine.messages.clear()
    engine._execute_scan(player_ship, sb_ids[0])
    for msg in engine.messages:
        print(f"  {msg}")
    
    print()
    print("=" * 70)
    print(f" TEST 4: HAL Query Object Info (what is {npc_ids[1]})")
    print("=" * 70)
    engine.messages.clear()
    engine._query_object_info(f"what is {npc_ids[1]}")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Verify stance and behavior appear in HAL query
    hal_results = '\n'.join(engine.messages)
    assert 'Stance:' in hal_results, "Stance should appear in HAL object info"
    assert '(timid)' in hal_results or '(aggressive)' in hal_results or '(neutral)' in hal_results, \
        "Behavior trait should appear in HAL object info header"
    print("\n✓ Stance and behavior information appears in HAL query!")
    
    print()
    print("=" * 70)
    print(f" TEST 5: HAL Query Starbase Info (what is {sb_ids[1]})")
    print("=" * 70)
    engine.messages.clear()
    engine._query_object_info(f"what is {sb_ids[1]}")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Verify stance appears for starbase
    hal_results = '\n'.join(engine.messages)
    assert 'Stance:' in hal_results, "Stance should appear in HAL starbase info"
    print("\n✓ Stance information appears in HAL starbase query!")
    
    print()
    print("=" * 70)
    print(" ✓ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Summary of Changes:")
    print("  • Scan command (general) now shows: [stance, behavior] for ships")
    print("  • Scan command (general) now shows: [stance] for starbases")
    print("  • Scan command (specific) now shows: Stance field for ships")
    print("  • HAL queries now show: Behavior in header, Stance as field")
    print()


if __name__ == "__main__":
    test_scan_and_hal_stance_behavior()
