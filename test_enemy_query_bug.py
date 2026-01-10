#!/usr/bin/env python3
"""
Test to reproduce the bug where "hal where is the nearest enemy ship?" 
returns incorrect results.
"""

from src.game_engine import GameEngine
from src.ship import Ship


def test_enemy_query():
    """Test that enemy ship queries return correct results based on stance."""
    print("=" * 60)
    print("Testing Enemy Ship Query Bug")
    print("=" * 60)
    
    # Initialize game
    engine = GameEngine(universe_seed=54321)
    player_ship = engine.player_ship
    
    # Position player at origin
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    # Get some NPCs and position them at known distances
    npc_ids = list(engine.npc_ships.keys())[:5]
    
    if len(npc_ids) >= 5:
        print("\n[SETUP] Positioning NPCs with specific stances:")
        print("-" * 60)
        
        # NPC 1: Closest, but FRIENDLY (should NOT be returned as enemy)
        npc1 = engine.npc_ships[npc_ids[0]]
        npc1.position.x = 5000.0
        npc1.position.y = 5010.0  # 10 AU away
        npc1.stances[player_ship.id] = 'friendly'
        print(f"NPC {npc_ids[0]}: 10.0 AU - FRIENDLY (should NOT be enemy)")
        
        # NPC 2: Second closest, NEUTRAL (should NOT be returned as enemy)
        npc2 = engine.npc_ships[npc_ids[1]]
        npc2.position.x = 5000.0
        npc2.position.y = 5020.0  # 20 AU away
        npc2.stances[player_ship.id] = 'neutral'
        print(f"NPC {npc_ids[1]}: 20.0 AU - NEUTRAL (should NOT be enemy)")
        
        # NPC 3: Third closest, HOSTILE (should be returned as nearest enemy)
        npc3 = engine.npc_ships[npc_ids[2]]
        npc3.position.x = 5000.0
        npc3.position.y = 5030.0  # 30 AU away
        npc3.stances[player_ship.id] = 'hostile'
        print(f"NPC {npc_ids[2]}: 30.0 AU - HOSTILE (SHOULD be nearest enemy)")
        
        # NPC 4: Far away, HOSTILE
        npc4 = engine.npc_ships[npc_ids[3]]
        npc4.position.x = 5000.0
        npc4.position.y = 5050.0  # 50 AU away
        npc4.stances[player_ship.id] = 'hostile'
        print(f"NPC {npc_ids[3]}: 50.0 AU - HOSTILE (farther enemy)")
        
        # NPC 5: Very far, FRIENDLY
        npc5 = engine.npc_ships[npc_ids[4]]
        npc5.position.x = 5000.0
        npc5.position.y = 5100.0  # 100 AU away
        npc5.stances[player_ship.id] = 'friendly'
        print(f"NPC {npc_ids[4]}: 100.0 AU - FRIENDLY (should NOT be enemy)")
    
    # Test queries
    print("\n" + "=" * 60)
    print("TESTING QUERIES")
    print("=" * 60)
    
    # Test 1: "nearest enemy"
    print("\n[TEST 1] Query: 'hal where is the nearest enemy ship?'")
    print("-" * 60)
    print("EXPECTED: Should return", npc_ids[2], "at 30.0 AU (closest HOSTILE)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "where is the nearest enemy ship?")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_npc = any(npc_ids[2] in msg for msg in engine.messages)
    has_correct_distance = any('30.0' in msg for msg in engine.messages)
    has_wrong_npc = any(npc_ids[0] in msg or npc_ids[1] in msg for msg in engine.messages)
    
    print()
    if has_correct_npc and has_correct_distance:
        print("✓ TEST PASSED: Returned correct hostile NPC")
    else:
        print("✗ TEST FAILED: Did not return correct hostile NPC")
        if has_wrong_npc:
            print("  ERROR: Returned a non-hostile NPC!")
    
    # Test 2: "nearest hostile ship"
    print("\n[TEST 2] Query: 'hal nearest hostile ship'")
    print("-" * 60)
    print("EXPECTED: Should return", npc_ids[2], "at 30.0 AU (closest HOSTILE)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest hostile ship")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_npc = any(npc_ids[2] in msg for msg in engine.messages)
    has_correct_distance = any('30.0' in msg for msg in engine.messages)
    has_wrong_npc = any(npc_ids[0] in msg or npc_ids[1] in msg for msg in engine.messages)
    
    print()
    if has_correct_npc and has_correct_distance:
        print("✓ TEST PASSED: Returned correct hostile NPC")
    else:
        print("✗ TEST FAILED: Did not return correct hostile NPC")
        if has_wrong_npc:
            print("  ERROR: Returned a non-hostile NPC!")
    
    # Test 3: "nearest friendly ship"  
    print("\n[TEST 3] Query: 'hal nearest friendly ship'")
    print("-" * 60)
    print("EXPECTED: Should return", npc_ids[0], "at 10.0 AU (closest FRIENDLY)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest friendly ship")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_npc = any(npc_ids[0] in msg for msg in engine.messages)
    has_correct_distance = any('10.0' in msg for msg in engine.messages)
    
    print()
    if has_correct_npc and has_correct_distance:
        print("✓ TEST PASSED: Returned correct friendly NPC")
    else:
        print("✗ TEST FAILED: Did not return correct friendly NPC")
    
    # Test 4: Debug - check actual stances
    print("\n" + "=" * 60)
    print("DEBUG: Verifying Actual Stances")
    print("=" * 60)
    for i in range(5):
        npc_id = npc_ids[i]
        npc = engine.npc_ships[npc_id]
        stance = npc.stances.get(player_ship.id, 'neutral')
        distance = player_ship.position.distance_to(npc.position)
        print(f"{npc_id}: {distance:.1f} AU - stance toward player: {stance}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_enemy_query()
