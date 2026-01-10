#!/usr/bin/env python3
"""
Test that friendly NPCs with aggressive behavior don't attack via LLM path.
"""

from src.game_engine import GameEngine
from src.universe_objects import Position

def test_friendly_aggressive_llm():
    """Test that friendly NPCs don't attack via LLM decision path."""
    print("=" * 80)
    print("Testing: Friendly Aggressive NPCs (LLM Path)")
    print("=" * 80)
    
    # Create game with LLM enabled
    engine = GameEngine()
    
    # Enable LLM
    if not engine.llm_handler.enabled:
        print("\n⚠️  LLM is not enabled. Test will use basic AI fallback.")
    
    # Set player reputation very low (would trigger aggressive attacks)
    engine.player_ship.reputation = 10
    engine.player_ship.position = Position(5000, 5000)
    
    print(f"\nPlayer reputation: {engine.player_ship.reputation} (very low)")
    print(f"LLM enabled: {engine.llm_handler.enabled}")
    
    # Find an aggressive NPC and make them friendly
    friendly_aggressive = None
    for npc_id, npc in engine.npc_ships.items():
        if npc.behavior_trait == 'aggressive' and not npc.is_destroyed:
            npc.stances[engine.player_ship.id] = 'friendly'
            npc.position = Position(5008, 5000)  # Within sensor range
            npc.damage = 20
            friendly_aggressive = npc
            friendly_npc_id = npc_id
            break
    
    if not friendly_aggressive:
        print("\n✗ TEST FAILED: Could not find an aggressive NPC")
        return
    
    print(f"\nTest NPC: {friendly_npc_id}")
    print(f"  Behavior: {friendly_aggressive.behavior_trait}")
    print(f"  Stance to player: {friendly_aggressive.stances[engine.player_ship.id]}")
    print(f"  Distance: {friendly_aggressive.position.distance_to(engine.player_ship.position):.1f} AU")
    
    # Test with _execute_npc_command (LLM path)
    print("\n" + "=" * 80)
    print("Running 5 turns with LLM decision path...")
    print("=" * 80)
    
    attacks_on_player = 0
    for turn in range(5):
        engine.messages = []
        
        # Use the full NPC command execution (will use LLM if enabled)
        engine._execute_npc_command(friendly_aggressive, show_debug=True)
        
        # Check for attacks
        for msg in engine.messages:
            if friendly_npc_id in msg:
                if 'fires' in msg or 'launches' in msg:
                    if 'you' in msg.lower() or 'player' in msg.lower():
                        attacks_on_player += 1
                        print(f"\nTurn {turn + 1}: ⚠️  ATTACK DETECTED: {msg}")
                print(f"Turn {turn + 1}: {msg}")
    
    # Results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    if attacks_on_player > 0:
        print(f"\n✗ TEST FAILED: Friendly NPC attacked {attacks_on_player} times via LLM!")
        print("  Expected: 0 attacks (friendly stance should prevent attacks)")
    else:
        print("\n✓ TEST PASSED: Friendly NPC did NOT attack via LLM path!")
        print("  Friendly stance correctly prevents attacks in LLM decisions")

if __name__ == '__main__':
    test_friendly_aggressive_llm()
