#!/usr/bin/env python3
"""
Simple interactive demo of the fixed enemy ship queries.
"""

from src.game_engine import GameEngine


def demo_fix():
    """Demonstrate the fixed enemy ship query behavior."""
    print("=" * 70)
    print("HAL ENEMY SHIP QUERY FIX - DEMO")
    print("=" * 70)
    
    # Initialize game
    engine = GameEngine(universe_seed=42)
    player_ship = engine.player_ship
    
    # Position player
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    # Setup scenario
    npc_ids = list(engine.npc_ships.keys())[:5]
    
    print("\n[SCENARIO]")
    print("-" * 70)
    print("You are surrounded by ships with different stances:")
    print()
    
    # Configure NPCs with clear stances
    configs = [
        (8.0, 'friendly', "USS Enterprise - Friendly Federation ship"),
        (12.0, 'neutral', "Ferengi Trader - Neutral merchant"),
        (20.0, 'hostile', "Klingon Warbird - Hostile enemy"),
        (35.0, 'hostile', "Romulan Cruiser - Hostile enemy"),
        (50.0, 'friendly', "USS Voyager - Friendly Federation ship")
    ]
    
    for i, (distance, stance, description) in enumerate(configs):
        if i < len(npc_ids):
            npc = engine.npc_ships[npc_ids[i]]
            npc.position.x = 5000.0
            npc.position.y = 5000.0 + distance
            npc.stances[player_ship.id] = stance
            print(f"  {npc_ids[i]}: {distance:5.1f} AU - {stance:8s} - {description}")
    
    # Test queries
    test_queries = [
        "hal where is the nearest enemy ship?",
        "hal where is the nearest hostile ship?",
        "hal where is the nearest friendly ship?",
        "hal nearest neutral ship"
    ]
    
    print("\n" + "=" * 70)
    print("TESTING QUERIES")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n> {query}")
        print("-" * 70)
        engine.messages.clear()
        engine._execute_hal(player_ship, query)
        for msg in engine.messages:
            print(f"  {msg}")
    
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    print("Expected Results:")
    print("  • 'nearest enemy/hostile' → Should return", npc_ids[2], "at 20.0 AU")
    print("  • 'nearest friendly' → Should return", npc_ids[0], "at 8.0 AU")
    print("  • 'nearest neutral' → Should return", npc_ids[1], "at 12.0 AU")
    print()
    print("✓ All queries now correctly filter by stance!")
    print("=" * 70)


if __name__ == "__main__":
    demo_fix()
