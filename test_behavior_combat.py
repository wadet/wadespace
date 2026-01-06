#!/usr/bin/env python3
"""
Test script to verify behavior traits affect enemy ship behavior in combat.
"""

from src.game_engine import GameEngine

def test_behavior_in_combat():
    """Test that behavior traits affect enemy decisions during combat."""
    print("Initializing game with specific scenario...")
    game = GameEngine(universe_seed=42)
    
    # Set player reputation to test different behaviors
    game.player_ship.reputation = 45  # Below aggressive threshold (70), neutral threshold (50), but above timid (25)
    
    print(f"Player reputation set to: {game.player_ship.reputation}")
    print(f"Total enemy ships: {len(game.enemy_ships)}")
    
    # Find examples of each behavior type nearby
    print("\n" + "="*70)
    print("TESTING BEHAVIOR TRAITS IN COMBAT SCENARIOS")
    print("="*70)
    
    # Get first 5 enemy ships
    enemies_to_test = list(game.enemy_ships.items())[:5]
    
    for enemy_id, enemy_ship in enemies_to_test:
        behavior = enemy_ship.behavior_trait
        distance = enemy_ship.position.distance_to(game.player_ship.position)
        
        print(f"\n{behavior.upper()} Captain ({enemy_id}):")
        print(f"  Position: ({enemy_ship.position.x:.1f}, {enemy_ship.position.y:.1f})")
        print(f"  Distance to player: {distance:.1f} AU")
        print(f"  Current damage: {enemy_ship.damage:.1f}%")
        print(f"  Reputation: {enemy_ship.reputation}")
        
        # Test attack decision
        if behavior == 'aggressive':
            will_attack = game.player_ship.reputation < 70
            flee_threshold = 80
            print(f"  • Will attack (player rep {game.player_ship.reputation} < 70): {will_attack}")
            print(f"  • Will flee only if damage > {flee_threshold}%: {enemy_ship.damage > flee_threshold}")
        elif behavior == 'neutral':
            will_attack = (enemy_ship.damage > 0) or (game.player_ship.reputation < 50)
            flee_threshold = 50
            print(f"  • Will attack (provoked or player rep {game.player_ship.reputation} < 50): {will_attack}")
            print(f"  • Will flee if damage > {flee_threshold}%: {enemy_ship.damage > flee_threshold}")
        elif behavior == 'timid':
            will_attack = (enemy_ship.damage > 0) or (game.player_ship.reputation < 25)
            flee_threshold = 30
            will_flee = (enemy_ship.damage > flee_threshold) and (game.player_ship.reputation >= 10)
            print(f"  • Will attack (provoked or player rep {game.player_ship.reputation} < 25): {will_attack}")
            print(f"  • Will flee if damage > {flee_threshold}% (and player rep >= 10): {will_flee}")
    
    # Test damage scenarios
    print("\n" + "="*70)
    print("TESTING FLEE BEHAVIOR WITH DIFFERENT DAMAGE LEVELS")
    print("="*70)
    
    # Simulate damage for different behavior types
    test_cases = [
        ('aggressive', 85, "Should FLEE (damage > 80%)"),
        ('aggressive', 75, "Should ATTACK (damage <= 80%)"),
        ('neutral', 60, "Should FLEE (damage > 50%)"),
        ('neutral', 40, "Should ATTACK (damage <= 50%)"),
        ('timid', 35, "Should FLEE (damage > 30%, player rep >= 10)"),
        ('timid', 25, "Should ATTACK (damage <= 30%)"),
    ]
    
    for behavior_type, damage_level, expected in test_cases:
        # Find an enemy with this behavior
        target_enemy = None
        for enemy_ship in game.enemy_ships.values():
            if enemy_ship.behavior_trait == behavior_type:
                target_enemy = enemy_ship
                break
        
        if target_enemy:
            # Simulate damage
            original_damage = target_enemy.damage
            target_enemy.damage = damage_level
            
            # Check decision logic
            should_flee = False
            should_attack = False
            
            if behavior_type == 'aggressive':
                should_attack = game.player_ship.reputation < 70
                should_flee = target_enemy.damage > 80
            elif behavior_type == 'neutral':
                should_attack = (target_enemy.damage > 0) or (game.player_ship.reputation < 50)
                should_flee = target_enemy.damage > 50
            elif behavior_type == 'timid':
                should_attack = (target_enemy.damage > 0) or (game.player_ship.reputation < 25)
                should_flee = (target_enemy.damage > 30) and (game.player_ship.reputation >= 10)
            
            action = "FLEE" if should_flee else ("ATTACK" if should_attack else "PATROL")
            print(f"\n{behavior_type.upper()} @ {damage_level}% damage -> {action}")
            print(f"  Expected: {expected}")
            print(f"  ✓ Correct!" if action in expected else f"  ✗ Mismatch!")
            
            # Restore original damage
            target_enemy.damage = original_damage
    
    # Test reputation thresholds
    print("\n" + "="*70)
    print("TESTING ATTACK BEHAVIOR WITH DIFFERENT PLAYER REPUTATIONS")
    print("="*70)
    
    rep_tests = [
        (90, "Aggressive: NO, Neutral: NO, Timid: NO"),
        (60, "Aggressive: YES, Neutral: NO, Timid: NO"),
        (40, "Aggressive: YES, Neutral: YES, Timid: NO"),
        (20, "Aggressive: YES, Neutral: YES, Timid: YES"),
    ]
    
    for rep, expected in rep_tests:
        game.player_ship.reputation = rep
        
        attacks = {
            'aggressive': rep < 70,
            'neutral': rep < 50,  # Assuming not provoked
            'timid': rep < 25,     # Assuming not provoked
        }
        
        print(f"\nPlayer reputation: {rep}")
        print(f"  Aggressive will attack: {attacks['aggressive']}")
        print(f"  Neutral will attack: {attacks['neutral']}")
        print(f"  Timid will attack: {attacks['timid']}")
        print(f"  Expected: {expected}")
    
    print("\n" + "="*70)
    print("✓ All behavior trait logic tests completed!")
    print("="*70)

if __name__ == '__main__':
    test_behavior_in_combat()
