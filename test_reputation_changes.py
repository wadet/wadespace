#!/usr/bin/env python3
"""
Test script to verify reputation changes when destroying npc ships.
Tests that reputation decreases for timid/high-rep npcs and increases for aggressive/low-rep npcs.
"""

from src.game_engine import GameEngine
from src.universe import Position


def test_reputation_changes():
    """Test reputation changes on ship destruction."""
    print("=" * 80)
    print("Testing Reputation Changes on Ship Destruction")
    print("=" * 80)
    
    # Create game
    game = GameEngine()
    game.player_ship.position = Position(5000, 5000)
    
    # Get initial player reputation
    initial_rep = game.player_ship.reputation
    print(f"\nInitial player reputation: {initial_rep}")
    
    # Test 1: Destroy a timid npc (should decrease reputation)
    print("\n" + "=" * 80)
    print("Test 1: Destroying a TIMID npc (reputation should decrease by 10)")
    print("=" * 80)
    
    # Find or set up a timid npc
    timid_npc_id = None
    for npc_id, npc in game.npc_ships.items():
        if npc.behavior_trait == 'timid':
            timid_npc_id = npc_id
            break
    
    # If no timid npc found, create one
    if not timid_npc_id:
        timid_npc_id = list(game.npc_ships.keys())[0]
        game.npc_ships[timid_npc_id].behavior_trait = 'timid'
    
    timid_enemy = game.npc_ships[timid_npc_id]
    timid_enemy.position = Position(5010, 5000)  # Close to player
    timid_enemy.reputation = 50  # Mid-range reputation
    
    print(f"Target: {timid_npc_id}")
    print(f"  Behavior: {timid_enemy.behavior_trait}")
    print(f"  Reputation: {timid_enemy.reputation}")
    print(f"  Position: ({timid_enemy.position.x:.0f}, {timid_enemy.position.y:.0f})")
    
    # Destroy the timid npc
    before_rep = game.player_ship.reputation
    timid_enemy.damage = 100.0
    timid_enemy.is_destroyed = True
    game._handle_ship_destruction(game.player_ship, timid_enemy, timid_npc_id)
    after_rep = game.player_ship.reputation
    
    print(f"\nReputation before: {before_rep}")
    print(f"Reputation after: {after_rep}")
    print(f"Change: {after_rep - before_rep}")
    
    if after_rep == before_rep - 10:
        print("✓ PASSED: Reputation decreased by 10")
    else:
        print(f"✗ FAILED: Expected decrease of 10, got {after_rep - before_rep}")
    
    # Test 2: Destroy an aggressive npc (should increase reputation)
    print("\n" + "=" * 80)
    print("Test 2: Destroying an AGGRESSIVE npc (reputation should increase by 10)")
    print("=" * 80)
    
    # Find or set up an aggressive npc
    aggressive_npc_id = None
    for npc_id, npc in game.npc_ships.items():
        if npc.behavior_trait == 'aggressive' and not npc.is_destroyed:
            aggressive_npc_id = npc_id
            break
    
    # If no aggressive npc found, create one
    if not aggressive_npc_id:
        for npc_id, npc in game.npc_ships.items():
            if not npc.is_destroyed:
                aggressive_npc_id = npc_id
                game.npc_ships[aggressive_npc_id].behavior_trait = 'aggressive'
                break
    
    aggressive_enemy = game.npc_ships[aggressive_npc_id]
    aggressive_enemy.position = Position(5010, 5000)
    aggressive_enemy.reputation = 50  # Mid-range reputation
    
    print(f"Target: {aggressive_npc_id}")
    print(f"  Behavior: {aggressive_enemy.behavior_trait}")
    print(f"  Reputation: {aggressive_enemy.reputation}")
    print(f"  Position: ({aggressive_enemy.position.x:.0f}, {aggressive_enemy.position.y:.0f})")
    
    # Destroy the aggressive npc
    before_rep = game.player_ship.reputation
    aggressive_enemy.damage = 100.0
    aggressive_enemy.is_destroyed = True
    game._handle_ship_destruction(game.player_ship, aggressive_enemy, aggressive_npc_id)
    after_rep = game.player_ship.reputation
    
    print(f"\nReputation before: {before_rep}")
    print(f"Reputation after: {after_rep}")
    print(f"Change: {after_rep - before_rep}")
    
    if after_rep == before_rep + 10:
        print("✓ PASSED: Reputation increased by 10")
    else:
        print(f"✗ FAILED: Expected increase of 10, got {after_rep - before_rep}")
    
    # Test 3: Destroy npc with reputation > 70 (should decrease reputation)
    print("\n" + "=" * 80)
    print("Test 3: Destroying npc with reputation > 70 (should decrease by 10)")
    print("=" * 80)
    
    high_rep_npc_id = None
    for npc_id, npc in game.npc_ships.items():
        if not npc.is_destroyed:
            high_rep_npc_id = npc_id
            break
    
    high_rep_enemy = game.npc_ships[high_rep_npc_id]
    high_rep_enemy.position = Position(5010, 5000)
    high_rep_enemy.reputation = 85  # High reputation
    high_rep_enemy.behavior_trait = 'neutral'  # Not timid or aggressive
    
    print(f"Target: {high_rep_npc_id}")
    print(f"  Behavior: {high_rep_enemy.behavior_trait}")
    print(f"  Reputation: {high_rep_enemy.reputation}")
    
    before_rep = game.player_ship.reputation
    high_rep_enemy.damage = 100.0
    high_rep_enemy.is_destroyed = True
    game._handle_ship_destruction(game.player_ship, high_rep_enemy, high_rep_npc_id)
    after_rep = game.player_ship.reputation
    
    print(f"\nReputation before: {before_rep}")
    print(f"Reputation after: {after_rep}")
    print(f"Change: {after_rep - before_rep}")
    
    if after_rep == before_rep - 10:
        print("✓ PASSED: Reputation decreased by 10")
    else:
        print(f"✗ FAILED: Expected decrease of 10, got {after_rep - before_rep}")
    
    # Test 4: Destroy npc with reputation < 30 (should increase reputation)
    print("\n" + "=" * 80)
    print("Test 4: Destroying npc with reputation < 30 (should increase by 10)")
    print("=" * 80)
    
    low_rep_npc_id = None
    for npc_id, npc in game.npc_ships.items():
        if not npc.is_destroyed:
            low_rep_npc_id = npc_id
            break
    
    low_rep_enemy = game.npc_ships[low_rep_npc_id]
    low_rep_enemy.position = Position(5010, 5000)
    low_rep_enemy.reputation = 20  # Low reputation
    low_rep_enemy.behavior_trait = 'neutral'  # Not timid or aggressive
    
    print(f"Target: {low_rep_npc_id}")
    print(f"  Behavior: {low_rep_enemy.behavior_trait}")
    print(f"  Reputation: {low_rep_enemy.reputation}")
    
    before_rep = game.player_ship.reputation
    low_rep_enemy.damage = 100.0
    low_rep_enemy.is_destroyed = True
    game._handle_ship_destruction(game.player_ship, low_rep_enemy, low_rep_npc_id)
    after_rep = game.player_ship.reputation
    
    print(f"\nReputation before: {before_rep}")
    print(f"Reputation after: {after_rep}")
    print(f"Change: {after_rep - before_rep}")
    
    if after_rep == before_rep + 10:
        print("✓ PASSED: Reputation increased by 10")
    else:
        print(f"✗ FAILED: Expected increase of 10, got {after_rep - before_rep}")
    
    # Test 5: Reputation cap at 100
    print("\n" + "=" * 80)
    print("Test 5: Reputation should cap at 100")
    print("=" * 80)
    
    game.player_ship.reputation = 95  # Near max
    
    neutral_npc_id = None
    for npc_id, npc in game.npc_ships.items():
        if not npc.is_destroyed:
            neutral_npc_id = npc_id
            break
    
    neutral_enemy = game.npc_ships[neutral_npc_id]
    neutral_enemy.reputation = 20  # Low rep, should trigger increase
    neutral_enemy.behavior_trait = 'neutral'
    
    print(f"Player reputation set to: {game.player_ship.reputation}")
    print(f"Destroying npc with reputation {neutral_enemy.reputation} (should increase)")
    
    before_rep = game.player_ship.reputation
    neutral_enemy.damage = 100.0
    neutral_enemy.is_destroyed = True
    game._handle_ship_destruction(game.player_ship, neutral_enemy, neutral_npc_id)
    after_rep = game.player_ship.reputation
    
    print(f"\nReputation before: {before_rep}")
    print(f"Reputation after: {after_rep}")
    print(f"Change: {after_rep - before_rep}")
    
    if after_rep == 100:
        print("✓ PASSED: Reputation capped at 100")
    else:
        print(f"✗ FAILED: Expected 100, got {after_rep}")
    
    # Test 6: Reputation floor at 0
    print("\n" + "=" * 80)
    print("Test 6: Reputation should floor at 0")
    print("=" * 80)
    
    game.player_ship.reputation = 5  # Near min
    
    timid_enemy2_id = None
    for npc_id, npc in game.npc_ships.items():
        if not npc.is_destroyed:
            timid_enemy2_id = npc_id
            break
    
    timid_enemy2 = game.npc_ships[timid_enemy2_id]
    timid_enemy2.reputation = 50
    timid_enemy2.behavior_trait = 'timid'  # Should trigger decrease
    
    print(f"Player reputation set to: {game.player_ship.reputation}")
    print(f"Destroying TIMID npc (should decrease)")
    
    before_rep = game.player_ship.reputation
    timid_enemy2.damage = 100.0
    timid_enemy2.is_destroyed = True
    game._handle_ship_destruction(game.player_ship, timid_enemy2, timid_enemy2_id)
    after_rep = game.player_ship.reputation
    
    print(f"\nReputation before: {before_rep}")
    print(f"Reputation after: {after_rep}")
    print(f"Change: {after_rep - before_rep}")
    
    if after_rep == 0:
        print("✓ PASSED: Reputation floored at 0")
    else:
        print(f"✗ FAILED: Expected 0, got {after_rep}")
    
    print("\n" + "=" * 80)
    print("All tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_reputation_changes()
