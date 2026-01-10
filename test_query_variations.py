#!/usr/bin/env python3
"""
Comprehensive test for various enemy/hostile/friendly ship query phrasings.
"""

from src.game_engine import GameEngine


def test_query_variations():
    """Test that various query phrasings work correctly."""
    print("=" * 70)
    print("Testing Various Query Phrasings")
    print("=" * 70)
    
    # Initialize game
    engine = GameEngine(universe_seed=99999)
    player_ship = engine.player_ship
    
    # Position player
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    # Get some NPCs and position them
    npc_ids = list(engine.npc_ships.keys())[:4]
    
    if len(npc_ids) >= 4:
        print("\n[SETUP]")
        print("-" * 70)
        
        # Setup: 1 hostile, 1 friendly, 1 neutral, 1 far hostile
        npc1 = engine.npc_ships[npc_ids[0]]
        npc1.position.x = 5000.0
        npc1.position.y = 5015.0  # 15 AU
        npc1.stances[player_ship.id] = 'hostile'
        print(f"NPC {npc_ids[0]}: 15.0 AU - HOSTILE (closest hostile)")
        
        npc2 = engine.npc_ships[npc_ids[1]]
        npc2.position.x = 5000.0
        npc2.position.y = 5010.0  # 10 AU
        npc2.stances[player_ship.id] = 'friendly'
        print(f"NPC {npc_ids[1]}: 10.0 AU - FRIENDLY (closest friendly)")
        
        npc3 = engine.npc_ships[npc_ids[2]]
        npc3.position.x = 5000.0
        npc3.position.y = 5012.0  # 12 AU
        npc3.stances[player_ship.id] = 'neutral'
        print(f"NPC {npc_ids[2]}: 12.0 AU - NEUTRAL (closest neutral)")
        
        npc4 = engine.npc_ships[npc_ids[3]]
        npc4.position.x = 5000.0
        npc4.position.y = 5050.0  # 50 AU
        npc4.stances[player_ship.id] = 'hostile'
        print(f"NPC {npc_ids[3]}: 50.0 AU - HOSTILE (far hostile)")
    
    # Test different query phrasings
    queries = [
        ("hal where is the nearest enemy ship?", npc_ids[0], "15.0"),
        ("hal where is the nearest hostile ship?", npc_ids[0], "15.0"),
        ("hal nearest enemy", npc_ids[0], "15.0"),
        ("hal closest hostile", npc_ids[0], "15.0"),
        ("hal find nearest enemy ship", npc_ids[0], "15.0"),
        ("hal show me the nearest enemy ship", npc_ids[0], "15.0"),
        ("hal where is the nearest friendly ship?", npc_ids[1], "10.0"),
        ("hal nearest friendly", npc_ids[1], "10.0"),
        ("hal closest friendly ship", npc_ids[1], "10.0"),
    ]
    
    print("\n" + "=" * 70)
    print("TESTING QUERY VARIATIONS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for query, expected_npc, expected_distance in queries:
        print(f"\nQuery: '{query}'")
        print(f"Expected: {expected_npc} at {expected_distance} AU")
        print("-" * 70)
        
        engine.messages.clear()
        engine._execute_hal(player_ship, query)
        
        # Check if expected NPC and distance are in the response
        response = " ".join(engine.messages)
        has_correct_npc = expected_npc in response
        has_correct_distance = expected_distance in response
        
        if has_correct_npc and has_correct_distance:
            print("✓ PASS")
            passed += 1
        else:
            print("✗ FAIL")
            print(f"Response: {response[:200]}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All query variations work correctly!")
    else:
        print(f"\n✗ {failed} query variation(s) failed")


if __name__ == "__main__":
    test_query_variations()
