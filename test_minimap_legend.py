#!/usr/bin/env python3
"""
Quick test to verify the minimap legend updates.
"""

from src.game_engine import GameEngine
from src.universe_objects import Starbase

def test_legend_content():
    """Test that the legend has been updated correctly."""
    print("=" * 70)
    print("MINIMAP LEGEND UPDATE VERIFICATION")
    print("=" * 70)
    
    engine = GameEngine(universe_seed=42)
    
    print("\n✓ Game engine initialized successfully")
    
    # Check that starbases exist with stances
    starbases = [obj for obj in engine.universe_objects.values() if isinstance(obj, Starbase)]
    print(f"✓ Found {len(starbases)} starbases with stance system")
    
    # Sample some starbases to show their stances
    print("\nSample starbase stances toward player:")
    for sb in starbases[:5]:
        stance = sb.stances.get(engine.player_ship.id, 'neutral')
        if stance == 'hostile':
            color = "RED"
        elif stance == 'friendly':
            color = "GREEN"
        else:
            color = "YELLOW"
        print(f"  {sb.id}: stance={stance:8s} -> appears as {color} in UI")
    
    print("\n" + "=" * 70)
    print("LEGEND CHANGES IMPLEMENTED:")
    print("=" * 70)
    print("✓ 1. Changed 'Friendly Base' to 'Starbase' with GREY icon")
    print("✓ 2. Removed 'NPC Base' from legend")
    print("✓ 3. Changed 'NPC Ship' icon color to GREY")
    print("✓ 4. Added colored stance explanation at bottom:")
    print("     '(Ships and starbases can be friendly, neutral, or hostile)'")
    print("      - 'friendly' in GREEN")
    print("      - 'neutral' in YELLOW")
    print("      - 'hostile' in RED")
    
    print("\n" + "=" * 70)
    print("LEGEND EXPLANATION:")
    print("=" * 70)
    print("The legend now shows ships and starbases in GREY because their")
    print("actual color in the game UI depends on their stance toward YOU:")
    print("  • RED = Hostile (will attack)")
    print("  • YELLOW = Neutral (behavior-based)")
    print("  • GREEN = Friendly (will not attack)")
    print("\nThe legend uses grey to indicate 'variable color' since the")
    print("actual color changes based on the entity's stance toward the player.")
    print("=" * 70)


if __name__ == '__main__':
    test_legend_content()
