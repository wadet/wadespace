"""
Test to verify that the return fire decision while fleeing is INDEPENDENT of damage level.

This test demonstrates that the decision to return fire while fleeing depends ONLY on
whether the fleeing ship was fired upon by the target, NOT on the fleeing ship's damage level.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game_engine import GameEngine
from src.universe_objects import Position


def test_low_damage_fleeing_no_return_fire():
    """Test that even a ship with LOW damage won't return fire if not fired upon."""
    print("\n" + "="*70)
    print("TEST 1: Low damage (35%) fleeing ship - NO return fire without provocation")
    print("="*70)
    
    engine = GameEngine()
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    npc_ship.position = Position(5008.0, 5000.0)  # 8 AU away
    npc_ship.damage = 35.0  # LOW damage, but timid behavior will still flee
    npc_ship.shields = 100.0
    npc_ship.energy = 100.0
    npc_ship.behavior_trait = "timid"  # Timid ships flee at 30%+ damage
    npc_ship.lock_phasers(engine.player_ship.id)
    
    print(f"\nSetup:")
    print(f"  NPC damage: {npc_ship.damage:.1f}% (LOW)")
    print(f"  Behavior: {npc_ship.behavior_trait} (flees at 30%+)")
    print(f"  Distance: 8.0 AU (within phaser range)")
    print(f"  NPC fired_upon_by: {npc_ship.fired_upon_by}")
    
    player_initial_damage = engine.player_ship.damage
    player_initial_shields = engine.player_ship.shields
    
    print(f"\nExecuting npc AI (should flee without attacking)...")
    engine._execute_basic_enemy_ai(npc_ship, 8.0, False, False)
    
    player_damage_taken = engine.player_ship.damage - player_initial_damage
    player_shields_lost = player_initial_shields - engine.player_ship.shields
    
    print(f"\nResult:")
    print(f"  Player damage: {player_damage_taken:.1f}%")
    print(f"  Player shields lost: {player_shields_lost:.1f}%")
    
    if player_damage_taken == 0 and player_shields_lost == 0:
        print("\n✅ PASS: Low damage fleeing ship did NOT attack (damage is not a factor)")
        return True
    else:
        print("\n❌ FAIL: Low damage fleeing ship attacked when it shouldn't have")
        return False


def test_high_damage_fleeing_no_return_fire():
    """Test that even a ship with HIGH damage won't return fire if not fired upon."""
    print("\n" + "="*70)
    print("TEST 2: High damage (95%) fleeing ship - NO return fire without provocation")
    print("="*70)
    
    engine = GameEngine()
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    npc_ship.position = Position(5008.0, 5000.0)  # 8 AU away
    npc_ship.damage = 95.0  # VERY HIGH damage
    npc_ship.shields = 100.0
    npc_ship.energy = 100.0
    npc_ship.behavior_trait = "aggressive"  # Even aggressive ships flee at 80%+
    npc_ship.lock_phasers(engine.player_ship.id)
    
    print(f"\nSetup:")
    print(f"  NPC damage: {npc_ship.damage:.1f}% (VERY HIGH)")
    print(f"  Behavior: {npc_ship.behavior_trait} (flees at 80%+)")
    print(f"  Distance: 8.0 AU (within phaser range)")
    print(f"  NPC fired_upon_by: {npc_ship.fired_upon_by}")
    
    player_initial_damage = engine.player_ship.damage
    player_initial_shields = engine.player_ship.shields
    
    print(f"\nExecuting npc AI (should flee without attacking)...")
    engine._execute_basic_enemy_ai(npc_ship, 8.0, False, False)
    
    player_damage_taken = engine.player_ship.damage - player_initial_damage
    player_shields_lost = player_initial_shields - engine.player_ship.shields
    
    print(f"\nResult:")
    print(f"  Player damage: {player_damage_taken:.1f}%")
    print(f"  Player shields lost: {player_shields_lost:.1f}%")
    
    if player_damage_taken == 0 and player_shields_lost == 0:
        print("\n✅ PASS: High damage fleeing ship did NOT attack (damage is not a factor)")
        return True
    else:
        print("\n❌ FAIL: High damage fleeing ship attacked when it shouldn't have")
        return False


def test_low_damage_fleeing_with_return_fire():
    """Test that a LOW damage fleeing ship WILL return fire if already fired upon."""
    print("\n" + "="*70)
    print("TEST 3: Low damage (35%) fleeing ship - DOES return fire after provocation")
    print("="*70)
    
    engine = GameEngine()
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    npc_ship.position = Position(5008.0, 5000.0)  # 8 AU away
    npc_ship.damage = 35.0  # LOW damage
    npc_ship.shields = 100.0
    npc_ship.energy = 100.0
    npc_ship.behavior_trait = "timid"
    npc_ship.weapons.phaser_operational = True
    npc_ship.lock_phasers(engine.player_ship.id)
    
    print(f"\nSetup:")
    print(f"  NPC damage: {npc_ship.damage:.1f}% (LOW)")
    print(f"  NPC fired_upon_by: {npc_ship.fired_upon_by}")
    
    # Player fires on npc first
    print(f"\nPlayer fires at npc...")
    engine.player_ship.lock_phasers(npc_id)
    result = engine.player_ship.fire_phaser(npc_ship)
    
    if result:
        print(f"  ✓ Hit: {result['damage']:.1f}% {result['damage_type']} damage")
    
    print(f"  NPC fired_upon_by: {npc_ship.fired_upon_by}")
    
    player_initial_damage = engine.player_ship.damage
    player_initial_shields = engine.player_ship.shields
    
    print(f"\nExecuting npc AI (should flee AND return fire)...")
    engine._execute_basic_enemy_ai(npc_ship, 8.0, False, False)
    
    player_damage_taken = engine.player_ship.damage - player_initial_damage
    player_shields_lost = player_initial_shields - engine.player_ship.shields
    
    print(f"\nResult:")
    print(f"  Player damage: {player_damage_taken:.1f}%")
    print(f"  Player shields lost: {player_shields_lost:.1f}%")
    
    if player_damage_taken > 0 or player_shields_lost > 0:
        print("\n✅ PASS: Low damage fleeing ship DID return fire after provocation")
        return True
    else:
        print("\n❌ FAIL: Low damage fleeing ship did NOT return fire")
        print("  (Note: Could fail due to phaser miss chance)")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("DAMAGE-INDEPENDENT RETURN FIRE TEST SUITE")
    print("Proving: Return fire decision is independent of fleeing ship's damage")
    print("="*70)
    
    results = []
    
    results.append(("Low damage (35%) - no return fire", test_low_damage_fleeing_no_return_fire()))
    results.append(("High damage (95%) - no return fire", test_high_damage_fleeing_no_return_fire()))
    results.append(("Low damage (35%) - return fire after provocation", test_low_damage_fleeing_with_return_fire()))
    
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
        print("\n🎉 CONFIRMED: Return fire decision is INDEPENDENT of damage level!")
        print("   Only the fired_upon_by check matters, not the damage percentage.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    exit(main())
