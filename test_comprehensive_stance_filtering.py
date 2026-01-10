#!/usr/bin/env python3
"""
Comprehensive test to verify both ship and starbase stance filtering works correctly.
"""

from src.game_engine import GameEngine


def test_comprehensive_stance_filtering():
    """Test that both ship and starbase queries correctly filter by stance."""
    print("=" * 70)
    print("COMPREHENSIVE STANCE FILTERING TEST")
    print("=" * 70)
    
    # Initialize game
    engine = GameEngine(universe_seed=77777)
    player_ship = engine.player_ship
    
    # Position player at origin
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    print("\n[SETUP]")
    print("-" * 70)
    
    # Setup NPCs
    npc_ids = list(engine.npc_ships.keys())[:4]
    if len(npc_ids) >= 4:
        npc1 = engine.npc_ships[npc_ids[0]]
        npc1.position.x = 5000.0
        npc1.position.y = 5015.0
        npc1.stances[player_ship.id] = 'hostile'
        print(f"NPC {npc_ids[0]}: 15.0 AU - HOSTILE")
        
        npc2 = engine.npc_ships[npc_ids[1]]
        npc2.position.x = 5000.0
        npc2.position.y = 5008.0
        npc2.stances[player_ship.id] = 'friendly'
        print(f"NPC {npc_ids[1]}: 8.0 AU - FRIENDLY")
        
        npc3 = engine.npc_ships[npc_ids[2]]
        npc3.position.x = 5000.0
        npc3.position.y = 5012.0
        npc3.stances[player_ship.id] = 'neutral'
        print(f"NPC {npc_ids[2]}: 12.0 AU - NEUTRAL")
        
        npc4 = engine.npc_ships[npc_ids[3]]
        npc4.position.x = 5000.0
        npc4.position.y = 5040.0
        npc4.stances[player_ship.id] = 'hostile'
        print(f"NPC {npc_ids[3]}: 40.0 AU - HOSTILE")
    
    # Setup Starbases
    starbase_ids = [obj_id for obj_id in engine.universe_objects.keys() if obj_id.startswith('sb')][:4]
    if len(starbase_ids) >= 4:
        sb1 = engine.universe_objects[starbase_ids[0]]
        sb1.position.x = 5000.0
        sb1.position.y = 5025.0
        sb1.stances[player_ship.id] = 'hostile'
        print(f"SB {starbase_ids[0]}: 25.0 AU - HOSTILE")
        
        sb2 = engine.universe_objects[starbase_ids[1]]
        sb2.position.x = 5000.0
        sb2.position.y = 5010.0
        sb2.stances[player_ship.id] = 'friendly'
        print(f"SB {starbase_ids[1]}: 10.0 AU - FRIENDLY")
        
        sb3 = engine.universe_objects[starbase_ids[2]]
        sb3.position.x = 5000.0
        sb3.position.y = 5018.0
        sb3.stances[player_ship.id] = 'neutral'
        print(f"SB {starbase_ids[2]}: 18.0 AU - NEUTRAL")
        
        sb4 = engine.universe_objects[starbase_ids[3]]
        sb4.position.x = 5000.0
        sb4.position.y = 5050.0
        sb4.stances[player_ship.id] = 'hostile'
        print(f"SB {starbase_ids[3]}: 50.0 AU - HOSTILE")
    
    # Test queries
    tests = [
        ("hal nearest enemy ship", npc_ids[0], "15.0", "hostile NPC ship"),
        ("hal nearest hostile ship", npc_ids[0], "15.0", "hostile NPC ship"),
        ("hal nearest friendly ship", npc_ids[1], "8.0", "friendly NPC ship"),
        ("hal nearest neutral ship", npc_ids[2], "12.0", "neutral NPC ship"),
        ("hal nearest enemy starbase", starbase_ids[0], "25.0", "hostile starbase"),
        ("hal nearest hostile starbase", starbase_ids[0], "25.0", "hostile starbase"),
        ("hal nearest friendly starbase", starbase_ids[1], "10.0", "friendly starbase"),
        ("hal nearest neutral starbase", starbase_ids[2], "18.0", "neutral starbase"),
    ]
    
    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for query, expected_id, expected_dist, description in tests:
        print(f"\nTest: '{query}'")
        print(f"Expected: {expected_id} at {expected_dist} AU ({description})")
        
        engine.messages.clear()
        engine._execute_hal(player_ship, query)
        response = " ".join(engine.messages)
        
        has_correct_id = expected_id in response
        has_correct_dist = expected_dist in response
        
        if has_correct_id and has_correct_dist:
            print("✓ PASS")
            passed += 1
        else:
            print("✗ FAIL")
            print(f"Response: {response[:150]}...")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("Both ship and starbase stance filtering works correctly!")
    else:
        print(f"\n✗ {failed} test(s) failed")


if __name__ == "__main__":
    test_comprehensive_stance_filtering()
