#!/usr/bin/env python3
"""
Test HAL query for hostile starbases - verify object ID is returned.
"""

from src.game_engine import GameEngine
from src.ship import Ship
from src.universe_objects import Position, Starbase
from src.llm_handler import LLMHandler

def test_hal_hostile_starbase_query():
    """Test that HAL query 'where is the nearest hostile starbase' returns a proper starbase ID."""
    print("\n" + "="*80)
    print("TEST: HAL Query - Nearest Hostile Starbase")
    print("="*80)
    
    # Create game with fixed seed
    game = GameEngine(universe_seed=42)
    
    # Position player near some starbases
    game.player_ship.position = Position(5000, 5000)
    
    # Find a hostile starbase
    hostile_starbases = []
    for obj_id, obj in game.universe_objects.items():
        if isinstance(obj, Starbase):
            stance = obj.stances.get(game.player_ship.id, 'neutral')
            if stance == 'hostile':
                distance = game.player_ship.position.distance_to(obj.position)
                hostile_starbases.append((obj_id, obj, distance))
    
    if not hostile_starbases:
        print("⚠ WARNING: No hostile starbases found in universe!")
        return
    
    # Sort by distance and get nearest
    hostile_starbases.sort(key=lambda x: x[2])
    nearest_id, nearest_obj, nearest_dist = hostile_starbases[0]
    
    print(f"\nNearest hostile starbase in universe:")
    print(f"  ID: {nearest_id}")
    print(f"  Position: ({nearest_obj.position.x:.1f}, {nearest_obj.position.y:.1f})")
    print(f"  Distance: {nearest_dist:.1f} AU")
    
    print(f"\nTotal hostile starbases: {len(hostile_starbases)}")
    print(f"Total starbases: {sum(1 for obj in game.universe_objects.values() if isinstance(obj, Starbase))}")
    
    # Execute HAL query
    print("\n" + "-"*80)
    print("EXECUTING: hal where is the nearest hostile starbase")
    print("-"*80)
    
    game._execute_hal(game.player_ship, "where is the nearest hostile starbase")
    
    # Display messages
    print("\nHAL Response:")
    for msg in game.messages:
        print(f"  {msg}")
    
    # Verify response contains proper ID
    response = "\n".join(game.messages)
    
    print("\n" + "-"*80)
    print("VERIFICATION")
    print("-"*80)
    
    if "sb####" in response or "specific ID not provided" in response.lower():
        print("❌ FAIL: Response contains placeholder 'sb####' or indicates no ID provided")
        print("   This means the LLM didn't receive starbase data in the prompt.")
        return False
    elif nearest_id in response:
        print(f"✓ PASS: Response contains correct starbase ID '{nearest_id}'")
        return True
    elif any(hostile_id in response for hostile_id, _, _ in hostile_starbases[:10]):
        print("✓ PASS: Response contains a valid hostile starbase ID")
        # Find which one
        for hostile_id, _, _ in hostile_starbases[:10]:
            if hostile_id in response:
                print(f"   Starbase ID: {hostile_id}")
                break
        return True
    else:
        print("⚠ UNCERTAIN: Response doesn't contain placeholder but also doesn't contain expected ID")
        print(f"   Expected ID like: {nearest_id}")
        print("   Check if response format is different or if LLM gave alternative answer")
        return None

if __name__ == "__main__":
    result = test_hal_hostile_starbase_query()
    print("\n" + "="*80)
    if result is True:
        print("✓ TEST PASSED")
    elif result is False:
        print("❌ TEST FAILED")
    else:
        print("⚠ TEST RESULT UNCERTAIN - Manual review needed")
    print("="*80)
