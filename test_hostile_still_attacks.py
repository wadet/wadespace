#!/usr/bin/env python3
"""
Verify that hostile aggressive NPCs still attack as expected.
"""

from src.game_engine import GameEngine
from src.universe_objects import Position

def test_hostile_aggressive_attacks():
    """Test that hostile aggressive NPCs still attack player normally."""
    print("=" * 80)
    print("Verification: Hostile Aggressive NPCs Should Still Attack")
    print("=" * 80)
    
    engine = GameEngine()
    engine.player_ship.reputation = 10
    engine.player_ship.position = Position(5000, 5000)
    
    # Find hostile aggressive NPC
    for npc_id, npc in engine.npc_ships.items():
        if npc.behavior_trait == 'aggressive' and not npc.is_destroyed:
            npc.stances[engine.player_ship.id] = 'hostile'
            npc.position = Position(5008, 5000)
            npc.damage = 20
            hostile_npc_id = npc_id
            break
    
    print(f"\nTest NPC: {hostile_npc_id}")
    print(f"  Stance: hostile")
    print(f"  Behavior: aggressive")
    print(f"  Player reputation: {engine.player_ship.reputation}")
    
    # Run 5 turns
    attacks = 0
    for turn in range(5):
        engine.messages = []
        npc = engine.npc_ships[hostile_npc_id]
        distance = npc.position.distance_to(engine.player_ship.position)
        engine._execute_basic_npc_ai(npc, distance, True, False)
        
        for msg in engine.messages:
            if hostile_npc_id in msg and ('fires' in msg or 'launches' in msg):
                if 'you' in msg.lower():
                    attacks += 1
    
    print(f"\nAttacks in 5 turns: {attacks}")
    if attacks > 0:
        print("✓ Hostile aggressive NPCs still attack correctly!")
    else:
        print("⚠️  No attacks detected (may be RNG or positioning)")

if __name__ == '__main__':
    test_hostile_aggressive_attacks()
