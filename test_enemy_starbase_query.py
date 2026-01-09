#!/usr/bin/env python3
"""
Test to verify that HAL queries for nearest enemy starbase work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game_engine import GameEngine
from ship import Ship, Position

def test_nearest_enemy_starbase():
    """Test that 'hal where is the nearest enemy starbase' returns the actual nearest enemy starbase."""
    print("=" * 80)
    print("Testing: HAL query for nearest enemy starbase")
    print("=" * 80)
    
    # Create a game engine with a fixed seed for reproducibility
    engine = GameEngine(universe_seed=12345)
    
    # Get player's position
    player_pos = engine.player_ship.position
    print(f"\nPlayer position: ({player_pos.x:.1f}, {player_pos.y:.1f})")
    
    # Count all starbases
    from universe_objects import Starbase
    all_starbases = [obj for obj in engine.universe_objects.values() if isinstance(obj, Starbase)]
    friendly_count = sum(1 for sb in all_starbases if sb.friendly_to_player)
    enemy_count = sum(1 for sb in all_starbases if not sb.friendly_to_player)
    
    print(f"\nTotal starbases in universe: {len(all_starbases)}")
    print(f"  Friendly: {friendly_count}")
    print(f"  Enemy: {enemy_count}")
    
    # Find all enemy (hostile) starbases manually
    enemy_starbases = []
    for obj_id, obj in engine.universe_objects.items():
        if obj_id.startswith('sb'):
            if isinstance(obj, Starbase) and not obj.friendly_to_player:
                distance = player_pos.distance_to(obj.position)
                enemy_starbases.append((obj_id, obj, distance))
    
    # Sort by distance
    enemy_starbases.sort(key=lambda x: x[2])
    
    print(f"\nTotal enemy starbases in universe: {len(enemy_starbases)}")
    print("\nNearest 5 enemy starbases (manual calculation):")
    for i, (sb_id, sb, dist) in enumerate(enemy_starbases[:5]):
        print(f"  {i+1}. {sb_id}: {dist:.1f} AU at ({sb.position.x:.1f}, {sb.position.y:.1f})")
    
    if not enemy_starbases:
        print("\nNo enemy starbases found in universe!")
        return False
    
    expected_nearest_id, expected_nearest_obj, expected_distance = enemy_starbases[0]
    print(f"\nExpected nearest enemy starbase: {expected_nearest_id} at {expected_distance:.1f} AU")
    
    # Clear messages
    engine.messages = []
    
    # Test the HAL query using the fallback pattern matching
    print("\n" + "=" * 80)
    print("Testing fallback pattern matching: 'hal where is the nearest enemy starbase'")
    print("=" * 80)
    
    engine._execute_hal(engine.player_ship, "where is the nearest enemy starbase")
    
    print("\nHAL response (fallback):")
    for msg in engine.messages:
        print(f"  {msg}")
    
    # Check if the response contains the expected starbase ID
    response_text = ' '.join(engine.messages)
    
    if expected_nearest_id in response_text:
        print(f"\n✓ SUCCESS: Found expected starbase {expected_nearest_id} in response")
        
        # Verify distance is approximately correct
        if f"{expected_distance:.1f}" in response_text:
            print(f"✓ SUCCESS: Distance {expected_distance:.1f} AU matches")
        else:
            print(f"⚠ WARNING: Distance might not match exactly")
        
        result = True
    else:
        print(f"\n✗ FAILURE: Expected {expected_nearest_id} but got different result")
        print(f"Expected starbase: {expected_nearest_id} at {expected_distance:.1f} AU")
        result = False
    
    # Also test with LLM if available
    if engine.llm_handler.enabled:
        print("\n" + "=" * 80)
        print("Testing with LLM: 'hal where is the nearest enemy starbase'")
        print("=" * 80)
        
        engine.messages = []
        engine._execute_hal(engine.player_ship, "where is the nearest enemy starbase")
        
        print("\nHAL response (LLM):")
        for msg in engine.messages:
            print(f"  {msg}")
        
        llm_response_text = ' '.join(engine.messages)
        if expected_nearest_id in llm_response_text:
            print(f"\n✓ SUCCESS: LLM found expected starbase {expected_nearest_id}")
        else:
            print(f"\n⚠ WARNING: LLM response may not contain exact starbase ID")
            print(f"Expected: {expected_nearest_id}")
    else:
        print("\n⚠ LLM not available for testing")
    
    print("\n" + "=" * 80)
    return result


if __name__ == "__main__":
    success = test_nearest_enemy_starbase()
    sys.exit(0 if success else 1)
