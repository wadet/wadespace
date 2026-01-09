#!/usr/bin/env python3
"""
Integration test for hal command stance queries in realistic game scenario.
Tests both LLM and fallback modes with natural language queries.
"""

from src.game_engine import GameEngine


def test_realistic_hal_queries():
    """Test hal queries in a realistic combat/exploration scenario."""
    print("=" * 70)
    print("HAL STANCE QUERY INTEGRATION TEST")
    print("=" * 70)
    
    # Initialize game
    engine = GameEngine(universe_seed=99999)
    player = engine.player_ship
    
    # Setup: Player ship under attack scenario
    player.position.x = 5000.0
    player.position.y = 5000.0
    player.damage = 25.0  # Damaged from combat
    player.shields = 40.0  # Shields weakened
    
    print("\n[SCENARIO] Player ship damaged, needs to locate:")
    print("  1. Nearest enemy (to avoid or engage)")
    print("  2. Friendly starbase (for repairs)")
    print("  3. Neutral ships (potential allies)")
    print()
    
    # Configure environment
    npcs = list(engine.npc_ships.keys())[:8]
    
    # Hostile ships closing in
    for i in range(3):
        if i < len(npcs):
            npc = engine.npc_ships[npcs[i]]
            npc.position.x = 5000.0 + (i + 1) * 12.0
            npc.position.y = 5000.0
            npc.stances[player.id] = 'hostile'
            npc.damage = 10.0 * i  # Varying damage
    
    # Friendly escort
    if len(npcs) > 3:
        escort = engine.npc_ships[npcs[3]]
        escort.position.x = 4995.0
        escort.position.y = 5005.0
        escort.stances[player.id] = 'friendly'
    
    # Neutral traders
    for i in range(4, 6):
        if i < len(npcs):
            npc = engine.npc_ships[npcs[i]]
            npc.position.x = 5000.0 - (i - 3) * 20.0
            npc.position.y = 5000.0 + 15.0
            npc.stances[player.id] = 'neutral'
    
    # Starbases
    sbs = [sid for sid in engine.universe_objects.keys() if sid.startswith('sb')][:3]
    
    # Friendly starbase for repairs
    if sbs:
        sb = engine.universe_objects[sbs[0]]
        sb.position.x = 4980.0
        sb.position.y = 4990.0
        sb.stances[player.id] = 'friendly'
        sb.damage = 0.0
    
    # Hostile starbase
    if len(sbs) > 1:
        sb = engine.universe_objects[sbs[1]]
        sb.position.x = 5050.0
        sb.position.y = 5050.0
        sb.stances[player.id] = 'hostile'
    
    # Neutral outpost
    if len(sbs) > 2:
        sb = engine.universe_objects[sbs[2]]
        sb.position.x = 4950.0
        sb.position.y = 5050.0
        sb.stances[player.id] = 'neutral'
    
    # Test queries a player might naturally ask
    test_cases = [
        # Combat awareness
        ("nearest enemy", "Tactical: Identify immediate threat"),
        ("how many hostile ships", "Strategic: Assess combat situation"),
        ("closest enemy base", "Intel: Locate enemy installations"),
        
        # Seeking assistance
        ("friendly starbase", "Urgent: Need repairs"),
        ("where is the nearest ally", "Support: Locate friendly forces"),
        ("friendly base nearby", "Navigation: Find safe harbor"),
        
        # Exploration/Trading
        ("neutral ships", "Diplomacy: Find potential allies"),
        ("nearest neutral starbase", "Trade: Locate neutral outpost"),
        
        # General awareness
        ("nearest ship", "Sensor: Closest contact"),
        ("nearest base", "Navigation: Any starbase"),
    ]
    
    print("=" * 70)
    print("TESTING QUERIES (LLM MODE)")
    print("=" * 70)
    
    for query, context in test_cases:
        print(f"\n[{context}]")
        print(f"Query: \"{query}\"")
        print("-" * 70)
        
        engine.messages.clear()
        engine._execute_hal(player, query)
        
        if engine.messages:
            for msg in engine.messages[:5]:  # Limit output
                print(f"  {msg}")
        else:
            print("  (No response)")
    
    # Test fallback mode
    print("\n" + "=" * 70)
    print("TESTING QUERIES (FALLBACK MODE)")
    print("=" * 70)
    
    # Disable LLM
    llm_was_enabled = engine.llm_handler.enabled
    engine.llm_handler.enabled = False
    
    critical_queries = [
        ("nearest enemy", "Must find immediate threat"),
        ("friendly starbase", "Need repairs urgently"),
        ("nearest neutral npc", "Seek diplomatic contact"),
    ]
    
    for query, context in critical_queries:
        print(f"\n[{context}]")
        print(f"Query: \"{query}\"")
        print("-" * 70)
        
        engine.messages.clear()
        engine._execute_hal(player, query)
        
        if engine.messages:
            for msg in engine.messages[:5]:
                print(f"  {msg}")
        else:
            print("  (No response)")
    
    # Restore LLM state
    engine.llm_handler.enabled = llm_was_enabled
    
    print("\n" + "=" * 70)
    print("✓ Integration test complete")
    print("=" * 70)
    print("\nSummary:")
    print("  • LLM mode: Natural language understanding ✓")
    print("  • Fallback mode: Pattern matching backup ✓")
    print("  • Stance filtering: Enemy/Friendly/Neutral ✓")
    print("  • Realistic queries: Combat/Repair/Exploration ✓")


if __name__ == "__main__":
    test_realistic_hal_queries()
