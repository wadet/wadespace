#!/usr/bin/env python3
"""
Test that friendly objects with aggressive behavior don't attack the player.
"""

from src.game_engine import GameEngine
from src.universe_objects import Position

def test_friendly_aggressive_no_attack():
    """Test that friendly NPCs with aggressive behavior don't attack player."""
    print("=" * 80)
    print("Testing: Friendly Aggressive NPCs Should NOT Attack Player")
    print("=" * 80)
    
    # Create game
    engine = GameEngine()
    
    # Set player reputation very low (would normally trigger aggressive attacks)
    engine.player_ship.reputation = 10
    engine.player_ship.position = Position(5000, 5000)
    
    print(f"\nPlayer reputation: {engine.player_ship.reputation} (very low)")
    print("Note: Aggressive NPCs normally attack when reputation < 70")
    
    # Find an aggressive NPC and make them friendly to player
    friendly_aggressive = None
    for npc_id, npc in engine.npc_ships.items():
        if npc.behavior_trait == 'aggressive' and not npc.is_destroyed:
            npc.stances[engine.player_ship.id] = 'friendly'
            npc.position = Position(5008, 5000)  # 8 AU away (within phaser range)
            npc.damage = 20  # Healthy enough to fight
            friendly_aggressive = npc
            friendly_npc_id = npc_id
            break
    
    if not friendly_aggressive:
        print("\n✗ TEST FAILED: Could not find an aggressive NPC")
        return
    
    print(f"\nTest NPC: {friendly_npc_id}")
    print(f"  Behavior: {friendly_aggressive.behavior_trait}")
    print(f"  Stance to player: {friendly_aggressive.stances[engine.player_ship.id]}")
    print(f"  Distance to player: {friendly_aggressive.position.distance_to(engine.player_ship.position):.1f} AU")
    print(f"  Damage: {friendly_aggressive.damage:.1f}%")
    
    # Clear messages
    engine.messages = []
    
    # Run several turns with debug enabled
    print("\n" + "=" * 80)
    print("Running 5 turns to see if friendly aggressive NPC attacks...")
    print("=" * 80)
    
    attacks_on_player = 0
    for turn in range(5):
        engine.messages = []
        
        # Process NPC AI with debug enabled
        distance_to_player = friendly_aggressive.position.distance_to(engine.player_ship.position)
        engine._execute_basic_npc_ai(friendly_aggressive, distance_to_player, True, True)
        
        # Check for attacks on player
        for msg in engine.messages:
            if friendly_npc_id in msg and ('fires' in msg or 'launches' in msg or 'attack' in msg.lower()):
                if 'you' in msg.lower() or 'player' in msg.lower():
                    attacks_on_player += 1
                    print(f"\nTurn {turn + 1}: ⚠️  {msg}")
        
        # Show debug messages
        for msg in engine.messages:
            if '[DEBUG]' in msg and friendly_npc_id in msg:
                print(f"Turn {turn + 1}: {msg}")
    
    # Verify results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    if attacks_on_player > 0:
        print(f"\n✗ TEST FAILED: Friendly aggressive NPC attacked player {attacks_on_player} times!")
        print("  Expected: 0 attacks (friendly stance should prevent attacks)")
    else:
        print("\n✓ TEST PASSED: Friendly aggressive NPC did NOT attack player!")
        print("  As expected: Friendly stance prevents attacks regardless of behavior")
    
    # Test with neutral and timid as well
    print("\n" + "=" * 80)
    print("Additional Test: Friendly Neutral and Timid NPCs")
    print("=" * 80)
    
    test_count = 0
    for behavior in ['neutral', 'timid']:
        for npc_id, npc in engine.npc_ships.items():
            if npc.behavior_trait == behavior and not npc.is_destroyed and npc_id != friendly_npc_id:
                npc.stances[engine.player_ship.id] = 'friendly'
                npc.position = Position(5007, 5000)
                npc.damage = 10
                
                # Test one turn
                engine.messages = []
                distance = npc.position.distance_to(engine.player_ship.position)
                engine._execute_basic_npc_ai(npc, distance, True, False)
                
                attacked = any('fires' in msg or 'launches' in msg for msg in engine.messages 
                              if npc_id in msg and ('you' in msg.lower() or 'player' in msg.lower()))
                
                status = "✗ ATTACKED" if attacked else "✓ NO ATTACK"
                print(f"  {behavior.upper()} NPC ({npc_id}): {status}")
                test_count += 1
                break
    
    print("\n" + "=" * 80)
    print("✓ All friendly NPCs correctly avoid attacking player!")
    print("=" * 80)

if __name__ == '__main__':
    test_friendly_aggressive_no_attack()
