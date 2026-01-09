#!/usr/bin/env python3
"""
Demo script showcasing the enhanced hal command with stance-based queries.

This demonstrates how the hal command now understands:
- "enemy" = hostile stance towards player
- "friendly" = friendly stance towards player
- "neutral" = neutral stance towards player

Players can now ask natural language questions like:
- "nearest enemy"
- "closest hostile ship"
- "friendly starbase nearby"
- etc.
"""

from src.game_engine import GameEngine


def demo_hal_stance_queries():
    """Demonstrate hal command stance-based query capabilities."""
    print("=" * 70)
    print(" HAL COMMAND STANCE-BASED QUERY DEMO")
    print("=" * 70)
    print()
    print("The hal command now understands stance relationships!")
    print()
    print("Keywords that work:")
    print("  • 'enemy'/'enemies'/'hostile' → objects with hostile stance")
    print("  • 'friendly'/'friend'/'allies' → objects with friendly stance")
    print("  • 'neutral' → objects with neutral stance")
    print()
    print("=" * 70)
    
    # Initialize game
    engine = GameEngine(universe_seed=12345)
    player_ship = engine.player_ship
    
    # Position player
    player_ship.position.x = 5000.0
    player_ship.position.y = 5000.0
    
    # Set up a scenario with various NPCs and starbases
    print("\n[SCENARIO SETUP]")
    print("-" * 70)
    
    # Configure NPCs
    npc_ids = list(engine.npc_ships.keys())[:6]
    npc_config = [
        (10.0, 0, 'hostile', 'Hostile Klingon patrol'),
        (25.0, 0, 'hostile', 'Hostile Romulan warbird'),
        (35.0, 0, 'neutral', 'Neutral trading vessel'),
        (50.0, 0, 'friendly', 'Friendly Federation escort'),
        (70.0, 0, 'neutral', 'Neutral freighter'),
        (90.0, 0, 'hostile', 'Hostile raider')
    ]
    
    for i, (distance, angle_offset, stance, desc) in enumerate(npc_config):
        if i < len(npc_ids):
            npc_id = npc_ids[i]
            npc = engine.npc_ships[npc_id]
            npc.position.x = 5000.0 + distance
            npc.position.y = 5000.0 + angle_offset
            npc.stances[player_ship.id] = stance
            print(f"  {npc_id:8s} @ {distance:5.1f} AU - {stance:8s} - {desc}")
    
    # Configure starbases
    sb_ids = [obj_id for obj_id in engine.universe_objects.keys() if obj_id.startswith('sb')][:4]
    sb_config = [
        (15.0, 15.0, 'friendly', 'Friendly starbase - repair hub'),
        (45.0, -20.0, 'hostile', 'Hostile enemy base'),
        (65.0, 30.0, 'neutral', 'Neutral trading post'),
        (120.0, 0, 'friendly', 'Friendly resupply depot')
    ]
    
    for i, (x_offset, y_offset, stance, desc) in enumerate(sb_config):
        if i < len(sb_ids):
            sb_id = sb_ids[i]
            sb = engine.universe_objects[sb_id]
            sb.position.x = 5000.0 + x_offset
            sb.position.y = 5000.0 + y_offset
            sb.stances[player_ship.id] = stance
            distance = player_ship.position.distance_to(sb.position)
            print(f"  {sb_id:8s} @ {distance:5.1f} AU - {stance:8s} - {desc}")
    
    # Example queries
    queries = [
        ("nearest enemy", "Find closest hostile ship"),
        ("nearest hostile starbase", "Locate enemy base"),
        ("closest friendly ship", "Find Federation ally"),
        ("nearest neutral npc", "Locate neutral vessel"),
        ("friendly base nearby", "Find repair station"),
        ("nearest npc", "Show closest ship (any stance)")
    ]
    
    print("\n" + "=" * 70)
    print(" EXAMPLE HAL QUERIES")
    print("=" * 70)
    
    for query, description in queries:
        print(f"\n[QUERY] \"{query}\"")
        print(f"Purpose: {description}")
        print("-" * 70)
        
        engine.messages.clear()
        engine._execute_hal(player_ship, query)
        
        for msg in engine.messages:
            print(f"  {msg}")
    
    # Usage tips
    print("\n" + "=" * 70)
    print(" USAGE TIPS")
    print("=" * 70)
    print()
    print("In-game, you can now use queries like:")
    print()
    print("  hal nearest enemy")
    print("    → Finds the closest hostile ship")
    print()
    print("  hal friendly starbase")
    print("    → Locates nearest friendly base for repairs")
    print()
    print("  hal closest neutral ship")
    print("    → Finds neutral vessels for potential trading")
    print()
    print("  hal nearest hostile")
    print("    → Locates closest threat")
    print()
    print("The LLM integration means you can phrase questions naturally!")
    print()
    print("=" * 70)


if __name__ == "__main__":
    demo_hal_stance_queries()
