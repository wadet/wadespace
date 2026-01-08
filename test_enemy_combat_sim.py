#!/usr/bin/env python3
"""
Comprehensive test showing npc-on-npc combat with actual weapon fire.
This simulates several turns to show npcs attacking each other.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game_engine import GameEngine
from universe import Position
import random

def test_enemy_combat_simulation():
    """Simulate several turns of npc-on-npc combat."""
    print("=" * 70)
    print("NPC-on-NPC Combat Simulation")
    print("=" * 70)
    
    # Create game engine
    engine = GameEngine()
    
    # Set up scenario
    print("\n[SETUP] Creating combat scenario...")
    
    # Move player very far away
    engine.player_ship.position = Position(9000, 9000)
    engine.player_ship.reputation = 95  # Very high reputation (not attractive target)
    
    # Get 5 npc ships
    npc_ids = list(engine.npc_ships.keys())[:5]
    
    # Position them in a cluster
    print(f"\n[SETUP] Positioning {len(npc_ids)} npc ships in combat zone...")
    for i, npc_id in enumerate(npc_ids):
        npc = engine.npc_ships[npc_id]
        # Position in a cluster around (1000, 1000)
        npc.position = Position(1000 + random.randint(-20, 20), 
                                 1000 + random.randint(-20, 20))
        # Give some random damage
        npc.damage = random.uniform(20, 70)
        # Mix behaviors
        npc.behavior_trait = random.choice(['aggressive', 'aggressive', 'neutral'])
        
        print(f"  {npc_id}: pos({npc.position.x:.0f}, {npc.position.y:.0f}), "
              f"damage: {npc.damage:.1f}%, behavior: {npc.behavior_trait}")
    
    print(f"\n[INFO] Player ship at ({engine.player_ship.position.x:.0f}, "
          f"{engine.player_ship.position.y:.0f}), reputation: {engine.player_ship.reputation}")
    
    # Simulate 10 turns
    print("\n" + "=" * 70)
    print("SIMULATING 10 TURNS")
    print("=" * 70)
    
    enemy_attacks = 0
    player_attacks = 0
    
    for turn in range(1, 11):
        print(f"\n--- TURN {turn} ---")
        engine.messages.clear()
        
        # Execute npc AI for each ship
        for npc_id in list(engine.npc_ships.keys()):
            if npc_id not in engine.npc_ships:  # Ship might have been destroyed
                continue
                
            npc = engine.npc_ships[npc_id]
            if npc.is_destroyed or npc.is_disabled:
                continue
            
            distance_to_player = npc.position.distance_to(engine.player_ship.position)
            player_in_range = distance_to_player <= 50
            
            # Use basic AI with debug on
            engine._execute_basic_enemy_ai(npc, distance_to_player, player_in_range, True)
        
        # Analyze messages
        for msg in engine.messages:
            if 'fires phasers' in msg or 'launches a torpedo' in msg:
                # Check if it's attacking player or another npc
                if 'at you' in msg or 'at PLAYER' in msg:
                    player_attacks += 1
                else:
                    # Extract target ID - should be npc ship ID format
                    if ' at s' in msg and 's606' not in msg:  # Exclude "ship at station" type messages
                        enemy_attacks += 1
            
            print(f"  {msg}")
        
        # If no messages, print status
        if not engine.messages:
            print("  [No significant actions this turn]")
    
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  NPC-on-NPC attacks: {enemy_attacks}")
    print(f"  Attacks on Player: {player_attacks}")
    print(f"  Total attacks: {enemy_attacks + player_attacks}")
    
    if enemy_attacks > 0:
        print(f"\n✓ SUCCESS: NPC ships ARE attacking each other!")
        print(f"  {enemy_attacks} npc-on-npc attacks detected in 10 turns")
        
        if player_attacks > 0:
            print(f"  Note: {player_attacks} attacks on player (expected since player might enter range)")
        
        return True
    else:
        print(f"\n⚠ WARNING: No npc-on-npc attacks detected")
        print(f"  This might be due to:")
        print(f"    - Ships not meeting attack criteria")
        print(f"    - Random chance (attacks have probability)")
        print(f"    - Ships choosing movement over combat")
        
        if player_attacks > 0:
            print(f"\n  However, {player_attacks} attacks on player were detected,")
            print(f"  suggesting combat system is working.")
        
        return False

if __name__ == '__main__':
    success = test_enemy_combat_simulation()
    sys.exit(0 if success else 1)
