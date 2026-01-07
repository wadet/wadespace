"""
Test script to verify fleeing ships only return fire if already fired upon.

This test verifies the rule: Ships that are fleeing must not attack the ship 
they are fleeing from unless the fleeing ship has already been fired upon.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game_engine import GameEngine
from src.universe_objects import Position
from src.ship import Ship


def test_fleeing_without_being_fired_upon():
    """Test that fleeing ships do NOT attack before being fired upon."""
    print("\n" + "="*70)
    print("TEST 1: Fleeing ship should NOT attack before being fired upon")
    print("="*70)
    
    # Create game engine
    engine = GameEngine()
    
    # Position player and enemy close together
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    # Create enemy ship close by with high damage to trigger fleeing
    enemy_id = list(engine.enemy_ships.keys())[0]
    enemy_ship = engine.enemy_ships[enemy_id]
    enemy_ship.position = Position(5008.0, 5000.0)  # 8 AU away (in phaser range)
    enemy_ship.damage = 85.0  # High damage - should flee
    enemy_ship.shields = 100.0
    enemy_ship.energy = 100.0
    enemy_ship.behavior_trait = "aggressive"  # Even aggressive ships flee at 80%+ damage
    
    # Lock enemy on player
    enemy_ship.lock_phasers(engine.player_ship.id)
    
    # Record initial state
    player_initial_damage = engine.player_ship.damage
    player_initial_shields = engine.player_ship.shields
    
    print(f"\nInitial State:")
    print(f"  Player: damage={player_initial_damage:.1f}%, shields={player_initial_shields:.1f}%")
    print(f"  Enemy {enemy_id}: damage={enemy_ship.damage:.1f}%, shields={enemy_ship.shields:.1f}%")
    print(f"  Distance: 8.0 AU (within phaser range)")
    print(f"  Enemy fired_upon_by set: {enemy_ship.fired_upon_by}")
    
    # Execute enemy AI - should flee but NOT attack
    print(f"\nExecuting enemy AI (should flee without attacking)...")
    engine._execute_basic_enemy_ai(enemy_ship, 8.0, False, False)
    
    # Check if player took any damage
    player_damage_taken = engine.player_ship.damage - player_initial_damage
    player_shields_lost = player_initial_shields - engine.player_ship.shields
    
    print(f"\nAfter enemy turn:")
    print(f"  Player damage change: {player_damage_taken:.1f}%")
    print(f"  Player shields change: {player_shields_lost:.1f}%")
    print(f"  Enemy heading: {enemy_ship.propulsion.current_heading:.0f}°")
    print(f"  Enemy speed: {enemy_ship.propulsion.current_speed:.1f} AU/turn")
    
    # Verify enemy did NOT attack
    if player_damage_taken == 0 and player_shields_lost == 0:
        print("\n✅ PASS: Fleeing enemy did NOT attack before being fired upon")
        return True
    else:
        print("\n❌ FAIL: Fleeing enemy attacked when it shouldn't have")
        return False


def test_fleeing_after_being_fired_upon():
    """Test that fleeing ships DO return fire after being fired upon."""
    print("\n" + "="*70)
    print("TEST 2: Fleeing ship SHOULD return fire after being fired upon")
    print("="*70)
    
    # Create game engine
    engine = GameEngine()
    
    # Position player and enemy close together
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    # Create enemy ship close by with high damage to trigger fleeing
    enemy_id = list(engine.enemy_ships.keys())[0]
    enemy_ship = engine.enemy_ships[enemy_id]
    enemy_ship.position = Position(5008.0, 5000.0)  # 8 AU away (in phaser range)
    enemy_ship.damage = 85.0  # High damage - should flee
    enemy_ship.shields = 100.0
    enemy_ship.energy = 100.0
    enemy_ship.behavior_trait = "aggressive"
    enemy_ship.weapons.phaser_operational = True
    
    # Lock enemy on player
    enemy_ship.lock_phasers(engine.player_ship.id)
    
    print(f"\nInitial State:")
    print(f"  Enemy {enemy_id}: damage={enemy_ship.damage:.1f}%, shields={enemy_ship.shields:.1f}%")
    print(f"  Enemy fired_upon_by set: {enemy_ship.fired_upon_by}")
    
    # Player fires on enemy first
    print(f"\nPlayer fires phaser at enemy...")
    engine.player_ship.lock_phasers(enemy_id)
    result = engine.player_ship.fire_phaser(enemy_ship)
    
    if result:
        print(f"  ✓ Player hit enemy: {result['damage']:.1f}% {result['damage_type']} damage")
    
    print(f"  Enemy fired_upon_by set after being hit: {enemy_ship.fired_upon_by}")
    print(f"  Player ID in fired_upon_by: {engine.player_ship.id in enemy_ship.fired_upon_by}")
    
    # Record player state before enemy turn
    player_initial_damage = engine.player_ship.damage
    player_initial_shields = engine.player_ship.shields
    
    # Execute enemy AI - should flee AND return fire
    print(f"\nExecuting enemy AI (should flee and return fire)...")
    engine._execute_basic_enemy_ai(enemy_ship, 8.0, False, False)
    
    # Check if player took any damage (return fire)
    player_damage_taken = engine.player_ship.damage - player_initial_damage
    player_shields_lost = player_initial_shields - engine.player_ship.shields
    
    print(f"\nAfter enemy turn:")
    print(f"  Player damage change: {player_damage_taken:.1f}%")
    print(f"  Player shields change: {player_shields_lost:.1f}%")
    
    # Verify enemy DID return fire
    if player_damage_taken > 0 or player_shields_lost > 0:
        print("\n✅ PASS: Fleeing enemy returned fire after being fired upon")
        return True
    else:
        print("\n❌ FAIL: Fleeing enemy did NOT return fire after being fired upon")
        print("  (Note: This could also fail due to phaser miss chance)")
        return False


def test_torpedo_tracking():
    """Test that torpedo hits are tracked in fired_upon_by set."""
    print("\n" + "="*70)
    print("TEST 3: Torpedo hits should add attacker to fired_upon_by set")
    print("="*70)
    
    # Create game engine
    engine = GameEngine()
    
    # Position player and enemy
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    enemy_id = list(engine.enemy_ships.keys())[0]
    enemy_ship = engine.enemy_ships[enemy_id]
    enemy_ship.position = Position(5001.0, 5000.0)  # 1 AU away
    
    print(f"\nInitial State:")
    print(f"  Enemy {enemy_id} fired_upon_by: {enemy_ship.fired_upon_by}")
    
    # Player fires torpedo at enemy
    print(f"\nPlayer fires torpedo at enemy...")
    torpedo = engine.player_ship.fire_torpedo(enemy_ship.position, enemy_ship)
    
    if torpedo:
        print(f"  ✓ Torpedo fired: {len(engine.player_ship.weapons.active_torpedos)} active")
        
        # Move torpedo close to target to trigger hit detection
        if engine.player_ship.weapons.active_torpedos:
            torp = engine.player_ship.weapons.active_torpedos[0]
            # Set current_pos close to enemy, and target_pos AT enemy
            # This ensures distance > 0 so hit detection triggers
            torp['current_pos'] = Position(5000.5, 5000.0)  # 0.5 AU from enemy
            torp['target_pos'] = Position(5001.0, 5000.0)   # At enemy
            torp['distance_traveled'] = 0.5
            
            print(f"  Torpedo positioned 0.5 AU from enemy")
            print(f"  Torpedo current_pos: ({torp['current_pos'].x}, {torp['current_pos'].y})")
            print(f"  Torpedo target_pos: ({torp['target_pos'].x}, {torp['target_pos'].y})")
            print(f"  Enemy position: ({enemy_ship.position.x}, {enemy_ship.position.y})")
            
            # Check distance before update
            import math
            dx = torp['target_pos'].x - torp['current_pos'].x
            dy = torp['target_pos'].y - torp['current_pos'].y
            dist = math.sqrt(dx*dx + dy*dy)
            print(f"  Distance to target: {dist:.2f} AU (should be > 0 and will move to < 2.0)")
            
            # Update torpedoes to trigger hit detection
            print(f"\n  Calling _update_torpedos_for_ship...")
            engine._update_torpedos_for_ship(engine.player_ship, is_player=True)
            print(f"  Torpedoes remaining: {len(engine.player_ship.weapons.active_torpedos)}")
            
            print(f"\nAfter torpedo hit:")
            print(f"  Enemy damage: {enemy_ship.damage:.1f}%")
            print(f"  Enemy fired_upon_by: {enemy_ship.fired_upon_by}")
            print(f"  Player ID in set: {engine.player_ship.id in enemy_ship.fired_upon_by}")
            
            if engine.player_ship.id in enemy_ship.fired_upon_by:
                print("\n✅ PASS: Torpedo hit added player to enemy's fired_upon_by set")
                return True
            else:
                print("\n❌ FAIL: Torpedo hit did NOT add player to fired_upon_by set")
                return False
    
    print("\n❌ FAIL: Could not fire torpedo")
    return False


def test_enemy_vs_enemy_fleeing():
    """Test that fleeing logic works between enemy ships."""
    print("\n" + "="*70)
    print("TEST 4: Enemy ships fleeing from other enemies")
    print("="*70)
    
    # Create game engine
    engine = GameEngine()
    
    # Position player far away
    engine.player_ship.position = Position(1000.0, 1000.0)
    
    # Get two enemy ships
    enemy_ids = list(engine.enemy_ships.keys())[:2]
    enemy1 = engine.enemy_ships[enemy_ids[0]]
    enemy2 = engine.enemy_ships[enemy_ids[1]]
    
    # Position them close together
    enemy1.position = Position(5000.0, 5000.0)
    enemy2.position = Position(5008.0, 5000.0)  # 8 AU away
    
    # Make enemy1 damaged (should flee)
    enemy1.damage = 85.0
    enemy1.behavior_trait = "aggressive"
    enemy1.shields = 50.0
    
    # Enemy2 is healthy
    enemy2.damage = 0.0
    enemy2.shields = 100.0
    
    print(f"\nInitial State:")
    print(f"  {enemy_ids[0]}: damage={enemy1.damage:.1f}%, should flee")
    print(f"  {enemy_ids[1]}: damage={enemy2.damage:.1f}%, healthy")
    print(f"  {enemy_ids[0]} fired_upon_by: {enemy1.fired_upon_by}")
    
    # Enemy2 fires on Enemy1
    print(f"\n{enemy_ids[1]} fires on {enemy_ids[0]}...")
    enemy2.lock_phasers(enemy_ids[0])
    result = enemy2.fire_phaser(enemy1)
    
    if result:
        print(f"  ✓ Hit: {result['damage']:.1f}% {result['damage_type']} damage")
        print(f"  {enemy_ids[0]} fired_upon_by: {enemy1.fired_upon_by}")
        
        if enemy_ids[1] in enemy1.fired_upon_by:
            print(f"\n✅ PASS: Enemy-to-enemy fire tracking works correctly")
            return True
        else:
            print(f"\n❌ FAIL: Enemy-to-enemy fire NOT tracked")
            return False
    else:
        print(f"  Miss or could not fire")
        print(f"\n⚠️  INCONCLUSIVE: Phaser missed")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("FLEEING RETURN FIRE TEST SUITE")
    print("Testing: Ships fleeing must not attack unless fired upon first")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("No return fire before being fired upon", test_fleeing_without_being_fired_upon()))
    results.append(("Return fire after being fired upon", test_fleeing_after_being_fired_upon()))
    results.append(("Torpedo hits tracked", test_torpedo_tracking()))
    results.append(("Enemy vs enemy fleeing", test_enemy_vs_enemy_fleeing()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED! Fleeing return fire logic is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review implementation.")
        return 1


if __name__ == "__main__":
    exit(main())
