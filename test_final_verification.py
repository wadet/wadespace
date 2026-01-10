#!/usr/bin/env python3
"""Final verification that friendly NPCs don't attack player in real game."""

from src.game_engine import GameEngine
from src.universe_objects import Position

def test_final_verification():
    """Final test simulating real gameplay scenario."""
    print("=" * 80)
    print("FINAL VERIFICATION: Real Gameplay Scenario")
    print("=" * 80)
    
    engine = GameEngine()
    engine.player_ship.reputation = 5  # Extremely low
    engine.player_ship.position = Position(5000, 5000)
    
    # Set up 3 aggressive NPCs at different stances
    test_npcs = []
    for npc_id, npc in engine.npc_ships.items():
        if npc.behavior_trait == 'aggressive' and not npc.is_destroyed and len(test_npcs) < 3:
            npc.position = Position(5008, 5000)  # All at same distance
            npc.damage = 15
            test_npcs.append((npc_id, npc))
    
    if len(test_npcs) < 3:
        print("Not enough NPCs for test")
        return
    
    # Set stances
    test_npcs[0][1].stances[engine.player_ship.id] = 'friendly'
    test_npcs[1][1].stances[engine.player_ship.id] = 'neutral'
    test_npcs[2][1].stances[engine.player_ship.id] = 'hostile'
    
    print(f"\nPlayer reputation: {engine.player_ship.reputation}")
    print(f"\nSetup: 3 aggressive NPCs at 8 AU:")
    print(f"  {test_npcs[0][0]}: FRIENDLY stance")
    print(f"  {test_npcs[1][0]}: NEUTRAL stance")
    print(f"  {test_npcs[2][0]}: HOSTILE stance")
    
    print("\nRunning 10 turns...")
    
    attacks_by_npc = {npc_id: 0 for npc_id, _ in test_npcs}
    
    for turn in range(10):
        for npc_id, npc in test_npcs:
            engine.messages = []
            dist = npc.position.distance_to(engine.player_ship.position)
            engine._execute_basic_npc_ai(npc, dist, True, False)
            
            for msg in engine.messages:
                if npc_id in msg and ('fires' in msg or 'launches' in msg):
                    if 'you' in msg.lower():
                        attacks_by_npc[npc_id] += 1
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\n{test_npcs[0][0]} (friendly):  {attacks_by_npc[test_npcs[0][0]]} attacks")
    print(f"{test_npcs[1][0]} (neutral):   {attacks_by_npc[test_npcs[1][0]]} attacks")
    print(f"{test_npcs[2][0]} (hostile):   {attacks_by_npc[test_npcs[2][0]]} attacks")
    
    friendly_attacks = attacks_by_npc[test_npcs[0][0]]
    
    if friendly_attacks > 0:
        print(f"\n✗✗✗ FAILED: Friendly NPC attacked {friendly_attacks} times! ✗✗✗")
    else:
        print("\n✓✓✓ SUCCESS: Friendly NPC did not attack player! ✓✓✓")
        print("Fix is working correctly!")

if __name__ == '__main__':
    test_final_verification()
