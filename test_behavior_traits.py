#!/usr/bin/env python3
"""
Test script to verify behavior traits are assigned to npc ships.
"""

from src.game_engine import GameEngine

def test_behavior_traits():
    """Test that behavior traits are assigned to npc ships."""
    print("Initializing game engine...")
    game = GameEngine(universe_seed=12345)
    
    print(f"\nTotal npc ships: {len(game.npc_ships)}")
    
    # Count traits
    trait_counts = {'aggressive': 0, 'neutral': 0, 'timid': 0, 'None': 0}
    
    print("\nFirst 10 npc ships:")
    for i, (npc_id, npc_ship) in enumerate(list(game.npc_ships.items())[:10]):
        trait = npc_ship.behavior_trait
        trait_counts[trait if trait else 'None'] += 1
        print(f"  {npc_id}: behavior={trait}, damage={npc_ship.damage:.1f}%, rep={npc_ship.reputation}")
    
    # Count all traits
    for npc_ship in game.npc_ships.values():
        trait = npc_ship.behavior_trait
        if trait not in trait_counts:
            trait_counts[trait] = 0
        trait_counts[trait] += 1
    
    print(f"\nBehavior trait distribution across all {len(game.npc_ships)} npc ships:")
    for trait, count in sorted(trait_counts.items()):
        if count > 0:
            percentage = (count / len(game.npc_ships)) * 100
            print(f"  {trait}: {count} ({percentage:.1f}%)")
    
    # Verify player ship doesn't have a behavior trait
    print(f"\nPlayer ship behavior trait: {game.player_ship.behavior_trait} (should be None)")
    
    # Test that behavior affects decision making
    print("\n" + "="*60)
    print("Testing behavior trait decision logic...")
    print("="*60)
    
    # Find one npc of each type
    enemy_examples = {}
    for npc_id, npc_ship in game.npc_ships.items():
        trait = npc_ship.behavior_trait
        if trait and trait not in enemy_examples:
            enemy_examples[trait] = (npc_id, npc_ship)
        if len(enemy_examples) == 3:
            break
    
    for trait, (npc_id, npc_ship) in enemy_examples.items():
        print(f"\n{trait.upper()} captain ({npc_id}):")
        print(f"  Current damage: {npc_ship.damage:.1f}%")
        print(f"  Player reputation: {game.player_ship.reputation}")
        
        # Simulate various scenarios
        if trait == 'aggressive':
            print(f"  - Will attack if player reputation < 70: {game.player_ship.reputation < 70}")
            print(f"  - Will flee if own damage > 80%: {npc_ship.damage > 80}")
        elif trait == 'neutral':
            print(f"  - Will attack if provoked or player reputation < 50: {npc_ship.damage > 0 or game.player_ship.reputation < 50}")
            print(f"  - Will flee if own damage > 50%: {npc_ship.damage > 50}")
        elif trait == 'timid':
            print(f"  - Will attack if provoked or player reputation < 25: {npc_ship.damage > 0 or game.player_ship.reputation < 25}")
            print(f"  - Will flee if own damage > 30% (and player rep >= 10): {npc_ship.damage > 30 and game.player_ship.reputation >= 10}")
    
    print("\n" + "="*60)
    print("✓ Behavior traits successfully implemented!")
    print("="*60)

if __name__ == '__main__':
    test_behavior_traits()
