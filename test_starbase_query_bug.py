#!/usr/bin/env python3
"""
Test to check if starbase queries correctly filter by stance.
"""

from src.game_engine import GameEngine


def test_starbase_query():
    """Test that starbase queries return correct results based on stance."""
    print("=" * 60)
    print("Testing Starbase Query with Stance Filtering")
    print("=" * 60)
    
    # Initialize game
    engine = GameEngine(universe_seed=88888)
    player_ship = engine.player_ship
    
    # Position player at origin
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    # Get some starbases and position them at known distances
    starbase_ids = [obj_id for obj_id in engine.universe_objects.keys() if obj_id.startswith('sb')][:5]
    
    if len(starbase_ids) >= 5:
        print("\n[SETUP] Positioning Starbases with specific stances:")
        print("-" * 60)
        
        # SB 1: Closest, but FRIENDLY (should NOT be returned as enemy)
        sb1 = engine.universe_objects[starbase_ids[0]]
        sb1.position.x = 5000.0
        sb1.position.y = 5010.0  # 10 AU away
        sb1.stances[player_ship.id] = 'friendly'
        print(f"Starbase {starbase_ids[0]}: 10.0 AU - FRIENDLY (should NOT be enemy)")
        
        # SB 2: Second closest, NEUTRAL (should NOT be returned as enemy)
        sb2 = engine.universe_objects[starbase_ids[1]]
        sb2.position.x = 5000.0
        sb2.position.y = 5020.0  # 20 AU away
        sb2.stances[player_ship.id] = 'neutral'
        print(f"Starbase {starbase_ids[1]}: 20.0 AU - NEUTRAL (should NOT be enemy)")
        
        # SB 3: Third closest, HOSTILE (should be returned as nearest enemy)
        sb3 = engine.universe_objects[starbase_ids[2]]
        sb3.position.x = 5000.0
        sb3.position.y = 5030.0  # 30 AU away
        sb3.stances[player_ship.id] = 'hostile'
        print(f"Starbase {starbase_ids[2]}: 30.0 AU - HOSTILE (SHOULD be nearest enemy)")
        
        # SB 4: Far away, HOSTILE
        sb4 = engine.universe_objects[starbase_ids[3]]
        sb4.position.x = 5000.0
        sb4.position.y = 5050.0  # 50 AU away
        sb4.stances[player_ship.id] = 'hostile'
        print(f"Starbase {starbase_ids[3]}: 50.0 AU - HOSTILE (farther enemy)")
        
        # SB 5: Very far, FRIENDLY
        sb5 = engine.universe_objects[starbase_ids[4]]
        sb5.position.x = 5000.0
        sb5.position.y = 5100.0  # 100 AU away
        sb5.stances[player_ship.id] = 'friendly'
        print(f"Starbase {starbase_ids[4]}: 100.0 AU - FRIENDLY (should NOT be enemy)")
    
    # Test queries
    print("\n" + "=" * 60)
    print("TESTING QUERIES")
    print("=" * 60)
    
    # Test 1: "nearest enemy starbase"
    print("\n[TEST 1] Query: 'hal where is the nearest enemy starbase?'")
    print("-" * 60)
    print("EXPECTED: Should return", starbase_ids[2], "at 30.0 AU (closest HOSTILE)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "where is the nearest enemy starbase?")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_sb = any(starbase_ids[2] in msg for msg in engine.messages)
    has_correct_distance = any('30.0' in msg for msg in engine.messages)
    has_wrong_sb = any(starbase_ids[0] in msg or starbase_ids[1] in msg for msg in engine.messages)
    
    print()
    if has_correct_sb and has_correct_distance:
        print("✓ TEST PASSED: Returned correct hostile starbase")
    else:
        print("✗ TEST FAILED: Did not return correct hostile starbase")
        if has_wrong_sb:
            print("  ERROR: Returned a non-hostile starbase!")
    
    # Test 2: "nearest hostile starbase"
    print("\n[TEST 2] Query: 'hal nearest hostile starbase'")
    print("-" * 60)
    print("EXPECTED: Should return", starbase_ids[2], "at 30.0 AU (closest HOSTILE)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest hostile starbase")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_sb = any(starbase_ids[2] in msg for msg in engine.messages)
    has_correct_distance = any('30.0' in msg for msg in engine.messages)
    has_wrong_sb = any(starbase_ids[0] in msg or starbase_ids[1] in msg for msg in engine.messages)
    
    print()
    if has_correct_sb and has_correct_distance:
        print("✓ TEST PASSED: Returned correct hostile starbase")
    else:
        print("✗ TEST FAILED: Did not return correct hostile starbase")
        if has_wrong_sb:
            print("  ERROR: Returned a non-hostile starbase!")
    
    # Test 3: "nearest friendly starbase"  
    print("\n[TEST 3] Query: 'hal nearest friendly starbase'")
    print("-" * 60)
    print("EXPECTED: Should return", starbase_ids[0], "at 10.0 AU (closest FRIENDLY)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest friendly starbase")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_sb = any(starbase_ids[0] in msg for msg in engine.messages)
    has_correct_distance = any('10.0' in msg for msg in engine.messages)
    
    print()
    if has_correct_sb and has_correct_distance:
        print("✓ TEST PASSED: Returned correct friendly starbase")
    else:
        print("✗ TEST FAILED: Did not return correct friendly starbase")
    
    # Test 4: "nearest neutral starbase"  
    print("\n[TEST 4] Query: 'hal nearest neutral starbase'")
    print("-" * 60)
    print("EXPECTED: Should return", starbase_ids[1], "at 20.0 AU (closest NEUTRAL)")
    print("-" * 60)
    engine.messages.clear()
    engine._execute_hal(player_ship, "nearest neutral starbase")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check result
    has_correct_sb = any(starbase_ids[1] in msg for msg in engine.messages)
    has_correct_distance = any('20.0' in msg for msg in engine.messages)
    
    print()
    if has_correct_sb and has_correct_distance:
        print("✓ TEST PASSED: Returned correct neutral starbase")
    else:
        print("✗ TEST FAILED: Did not return correct neutral starbase")
    
    # Test 5: Debug - check actual stances
    print("\n" + "=" * 60)
    print("DEBUG: Verifying Actual Stances")
    print("=" * 60)
    for i in range(5):
        sb_id = starbase_ids[i]
        sb = engine.universe_objects[sb_id]
        stance = sb.stances.get(player_ship.id, 'neutral')
        distance = player_ship.position.distance_to(sb.position)
        print(f"{sb_id}: {distance:.1f} AU - stance toward player: {stance}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_starbase_query()
