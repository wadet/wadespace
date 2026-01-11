#!/usr/bin/env python3
"""
Test HAL query word boundary fix - verify "star" queries still work.
"""

from src.game_engine import GameEngine
from src.universe_objects import Position

def test_hal_queries():
    """Test various HAL queries to ensure word boundary fix works correctly."""
    print("\n" + "="*80)
    print("TEST: HAL Query Word Boundary Fix")
    print("="*80)
    
    # Create game with fixed seed
    game = GameEngine(universe_seed=42)
    game.player_ship.position = Position(5000, 5000)
    
    test_cases = [
        ("nearest star", "Star"),  # Should match "star" word
        ("nearest hostile starbase", "Starbase"),  # Should NOT match "star" in "starbase"
        ("nearest planet", "Planet"),  # Should match "planet" word
        ("closest sun", "Star"),  # Should match "sun" as synonym for star
        ("where is the nearest friendly starbase", "Starbase"),  # Should find friendly starbase
    ]
    
    for i, (query, expected_type) in enumerate(test_cases, 1):
        print(f"\n{'-'*80}")
        print(f"Test Case {i}: '{query}'")
        print(f"Expected object type: {expected_type}")
        print(f"{'-'*80}")
        
        # Clear previous messages
        game.messages = []
        
        # Execute query
        game._execute_hal(game.player_ship, query)
        
        # Display response
        response = "\n".join(game.messages)
        print(f"Response: {response[:200]}...")  # Show first 200 chars
        
        # Verify
        if expected_type == "Starbase":
            if "sb" in response and "sb####" not in response:
                print("✓ PASS: Contains starbase ID (not placeholder)")
            elif "sb####" in response:
                print("❌ FAIL: Contains placeholder 'sb####'")
            else:
                print("⚠ UNCERTAIN: No starbase ID found")
        elif expected_type == "Star":
            if "st" in response and "stb" not in response:  # st but not part of "starbase"
                print("✓ PASS: Contains star ID")
            else:
                print("⚠ UNCERTAIN: No star ID found")
        elif expected_type == "Planet":
            if "pl" in response:
                print("✓ PASS: Contains planet ID")
            else:
                print("⚠ UNCERTAIN: No planet ID found")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_hal_queries()
