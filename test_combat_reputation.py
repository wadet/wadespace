#!/usr/bin/env python3
"""
Integration test to verify reputation changes work in actual combat.
Tests both phaser and torpedo destruction scenarios.
"""

from src.game_engine import GameEngine
from src.universe import Position
from src.command_parser import CommandParser


def test_combat_reputation():
    """Test reputation changes during actual combat."""
    print("=" * 80)
    print("Testing Reputation Changes in Combat")
    print("=" * 80)
    
    # Create game
    game = GameEngine()
    parser = CommandParser()
    game.player_ship.position = Position(5000, 5000)
    
    print(f"\nInitial player reputation: {game.player_ship.reputation}")
    
    # Test 1: Destroy with phasers
    print("\n" + "=" * 80)
    print("Test 1: Destroy npc with PHASERS")
    print("=" * 80)
    
    # Find an aggressive npc (should increase reputation)
    aggressive_id = None
    for npc_id, npc in game.npc_ships.items():
        if npc.behavior_trait == 'aggressive':
            aggressive_id = npc_id
            break
    
    if not aggressive_id:
        aggressive_id = list(game.npc_ships.keys())[0]
        game.npc_ships[aggressive_id].behavior_trait = 'aggressive'
    
    npc = game.npc_ships[aggressive_id]
    npc.position = Position(5005, 5000)  # 5 AU away (within phaser range)
    npc.shields = 0  # Disable shields for faster kill
    npc.shields_active = False
    npc.damage = 96  # Almost destroyed
    
    print(f"Target: {aggressive_id}")
    print(f"  Behavior: {npc.behavior_trait}")
    print(f"  Reputation: {npc.reputation}")
    print(f"  Damage: {npc.damage}%")
    print(f"  Distance: {game.player_ship.position.distance_to(npc.position):.1f} AU")
    
    # Lock and fire phasers
    game.player_ship.weapons.phaser_locked_target = aggressive_id
    
    before_rep = game.player_ship.reputation
    print(f"\nPlayer reputation before: {before_rep}")
    
    # Execute phaser fire
    game._execute_fire(game.player_ship)
    
    # Process turn to update state
    game.turn_count += 1
    
    after_rep = game.player_ship.reputation
    print(f"Player reputation after: {after_rep}")
    print(f"NPC destroyed: {npc.is_destroyed}")
    
    if npc.is_destroyed and after_rep > before_rep:
        print("✓ PASSED: NPC destroyed by phasers and reputation increased")
    elif npc.is_destroyed:
        print(f"✓ NPC destroyed but reputation change unexpected: {after_rep - before_rep}")
    else:
        print("⚠ NPC not destroyed, finishing off...")
        # Fire again if needed
        while not npc.is_destroyed and npc.damage < 100:
            game._execute_fire(game.player_ship)
            if npc.is_destroyed:
                after_rep = game.player_ship.reputation
                print(f"Player reputation after: {after_rep}")
                print(f"Change: {after_rep - before_rep}")
                break
    
    # Test 2: Destroy with torpedoes
    print("\n" + "=" * 80)
    print("Test 2: Destroy npc with TORPEDOES")
    print("=" * 80)
    
    # Find a timid npc (should decrease reputation)
    timid_id = None
    for npc_id, npc in game.npc_ships.items():
        if npc.behavior_trait == 'timid' and not npc.is_destroyed:
            timid_id = npc_id
            break
    
    if not timid_id:
        # Find any available npc
        for npc_id, npc in game.npc_ships.items():
            if not npc.is_destroyed:
                timid_id = npc_id
                game.npc_ships[timid_id].behavior_trait = 'timid'
                break
    
    enemy2 = game.npc_ships[timid_id]
    enemy2.position = Position(5020, 5000)  # 20 AU away
    enemy2.damage = 76  # Torpedo does 25% damage, so this will destroy it
    
    print(f"Target: {timid_id}")
    print(f"  Behavior: {enemy2.behavior_trait}")
    print(f"  Reputation: {enemy2.reputation}")
    print(f"  Damage: {enemy2.damage}%")
    print(f"  Distance: {game.player_ship.position.distance_to(enemy2.position):.1f} AU")
    
    before_rep = game.player_ship.reputation
    print(f"\nPlayer reputation before: {before_rep}")
    
    # Fire torpedo
    game._execute_torpedo(game.player_ship, timid_id)
    
    # Process torpedo movement for several turns
    print("\nProcessing torpedo flight...")
    for i in range(5):
        game._update_torpedos()
        if enemy2.is_destroyed:
            print(f"Torpedo hit on turn {i+1}")
            break
    
    after_rep = game.player_ship.reputation
    print(f"Player reputation after: {after_rep}")
    print(f"NPC destroyed: {enemy2.is_destroyed}")
    
    if enemy2.is_destroyed and after_rep < before_rep:
        print("✓ PASSED: NPC destroyed by torpedo and reputation decreased")
    elif enemy2.is_destroyed:
        print(f"✓ NPC destroyed but reputation change unexpected: {after_rep - before_rep}")
    else:
        print("⚠ NPC not destroyed by torpedo")
    
    print("\n" + "=" * 80)
    print("Combat integration tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_combat_reputation()
