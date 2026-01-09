#!/usr/bin/env python3
"""
Test script to verify hal command stance-based queries using fallback pattern matching.
This tests the queries without LLM to ensure the API changes work correctly.
"""

from src.game_engine import GameEngine
from src.ship import Ship


def test_hal_stance_fallback():
    """Test hal command fallback pattern matching with stance-based keywords."""
    print("=" * 60)
    print("Testing HAL Command Stance Fallback (Pattern Matching)")
    print("=" * 60)
    
    # Initialize game with fixed seed for reproducibility
    engine = GameEngine(universe_seed=42)
    
    # Disable LLM to force fallback pattern matching
    engine.llm_handler.enabled = False
    print("[INFO] LLM disabled - using fallback pattern matching\n")
    
    player_ship = engine.player_ship
    
    # Position player near several NPCs
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    # Position NPCs at known distances with different stances
    npc_ids = list(engine.npc_ships.keys())[:5]
    
    if len(npc_ids) >= 5:
        # Set up test NPCs with specific stances
        for i, npc_id in enumerate(npc_ids):
            npc = engine.npc_ships[npc_id]
            npc.position.x = 5000.0 + (i + 1) * 5.0  # 5, 10, 15, 20, 25 AU away
            npc.position.y = 5000.0
            
            # Assign different stances
            if i == 0:
                npc.stances[player_ship.id] = 'hostile'
                print(f"NPC {npc_id} at {(i+1)*5.0} AU - HOSTILE")
            elif i == 1:
                npc.stances[player_ship.id] = 'friendly'
                print(f"NPC {npc_id} at {(i+1)*5.0} AU - FRIENDLY")
            elif i == 2:
                npc.stances[player_ship.id] = 'neutral'
                print(f"NPC {npc_id} at {(i+1)*5.0} AU - NEUTRAL")
            elif i == 3:
                npc.stances[player_ship.id] = 'hostile'
                print(f"NPC {npc_id} at {(i+1)*5.0} AU - HOSTILE")
            elif i == 4:
                npc.stances[player_ship.id] = 'neutral'
                print(f"NPC {npc_id} at {(i+1)*5.0} AU - NEUTRAL")
    
    # Position starbases with different stances
    starbase_ids = [obj_id for obj_id in engine.universe_objects.keys() if obj_id.startswith('sb')][:3]
    
    if len(starbase_ids) >= 3:
        for i, sb_id in enumerate(starbase_ids):
            sb = engine.universe_objects[sb_id]
            sb.position.x = 5000.0
            sb.position.y = 5000.0 + (i + 1) * 8.0  # 8, 16, 24 AU away
            
            if i == 0:
                sb.stances[player_ship.id] = 'hostile'
                print(f"Starbase {sb_id} at {(i+1)*8.0} AU - HOSTILE")
            elif i == 1:
                sb.stances[player_ship.id] = 'friendly'
                print(f"Starbase {sb_id} at {(i+1)*8.0} AU - FRIENDLY")
            elif i == 2:
                sb.stances[player_ship.id] = 'neutral'
                print(f"Starbase {sb_id} at {(i+1)*8.0} AU - NEUTRAL")
    
    print("\n" + "=" * 60)
    print("Testing HAL Fallback Queries")
    print("=" * 60)
    
    # Test 1: Query nearest enemy (should find hostile NPC at 5 AU)
    print("\n[TEST 1] Query: 'nearest enemy'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest enemy")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('s9635' in msg for msg in engine.messages), "Expected to find hostile NPC s9635"
    assert any('5.0' in msg for msg in engine.messages), "Expected distance of 5.0 AU"
    assert any('hostile' in msg.lower() for msg in engine.messages), "Expected stance label"
    
    # Test 2: Query nearest hostile ship (should find hostile NPC at 5 AU)
    print("\n[TEST 2] Query: 'nearest hostile ship'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest hostile ship")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('s9635' in msg for msg in engine.messages), "Expected to find hostile NPC s9635"
    
    # Test 3: Query nearest friendly ship (should find friendly NPC at 10 AU)
    print("\n[TEST 3] Query: 'nearest friendly ship'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest friendly ship")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('s9445' in msg for msg in engine.messages), "Expected to find friendly NPC s9445"
    assert any('10.0' in msg for msg in engine.messages), "Expected distance of 10.0 AU"
    
    # Test 4: Query nearest neutral npc (should find neutral NPC at 15 AU)
    print("\n[TEST 4] Query: 'nearest neutral npc'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest neutral npc")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('s4158' in msg for msg in engine.messages), "Expected to find neutral NPC s4158"
    assert any('15.0' in msg for msg in engine.messages), "Expected distance of 15.0 AU"
    
    # Test 5: Query nearest enemy starbase (should find hostile starbase at 8 AU)
    print("\n[TEST 5] Query: 'nearest enemy starbase'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest enemy starbase")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('sb6434' in msg for msg in engine.messages), "Expected to find hostile starbase sb6434"
    assert any('8.0' in msg for msg in engine.messages), "Expected distance of 8.0 AU"
    
    # Test 6: Query nearest friendly base (should find friendly starbase at 16 AU)
    print("\n[TEST 6] Query: 'nearest friendly base'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest friendly base")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('sb2903' in msg for msg in engine.messages), "Expected to find friendly starbase sb2903"
    assert any('16.0' in msg for msg in engine.messages), "Expected distance of 16.0 AU"
    
    # Test 7: Query nearest neutral starbase (should find neutral starbase at 24 AU)
    print("\n[TEST 7] Query: 'nearest neutral starbase'")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest neutral starbase")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('sb2018' in msg for msg in engine.messages), "Expected to find neutral starbase sb2018"
    assert any('24.0' in msg for msg in engine.messages), "Expected distance of 24.0 AU"
    
    # Test 8: Query without stance filter (should show nearest NPC regardless of stance)
    print("\n[TEST 8] Query: 'nearest npc' (no stance filter)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest npc")
    for msg in engine.messages:
        print(f"  {msg}")
    assert any('s9635' in msg for msg in engine.messages), "Expected to find nearest NPC s9635"
    assert any('Stance: hostile' in msg for msg in engine.messages), "Expected stance label when no filter"
    
    print("\n" + "=" * 60)
    print("✓ All HAL Fallback Stance Query Tests Passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_hal_stance_fallback()
