#!/usr/bin/env python3
"""
Test script to verify that weapon locks are treated as hostile actions by NPCs and starbases.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.game_engine import GameEngine
from src.universe_objects import Position


def test_npc_responds_to_weapon_lock():
    """Test that NPC ships respond to weapon locks as hostile actions."""
    print("\n" + "="*80)
    print("TEST 1: NPC Ship Response to Weapon Lock")
    print("="*80)
    
    # Initialize game
    engine = GameEngine(universe_seed=12345)
    
    # Find nearest NPC ship
    nearest_npc = None
    min_distance = float('inf')
    
    for npc_id, npc_ship in engine.npc_ships.items():
        if not npc_ship.is_destroyed:
            dist = engine.player_ship.position.distance_to(npc_ship.position)
            if dist < min_distance:
                min_distance = dist
                nearest_npc = npc_ship
    
    if not nearest_npc:
        print("❌ No NPC ships found!")
        return False
    
    print(f"\nFound NPC ship: {nearest_npc.id}")
    print(f"Distance: {min_distance:.1f} AU")
    print(f"Initial shields status: {'UP' if nearest_npc.shields_active else 'DOWN'}")
    print(f"Initial stance toward player: {nearest_npc.stances.get(engine.player_ship.id, 'neutral')}")
    
    # Lock weapons on the NPC
    print(f"\n🎯 Player locking weapons on {nearest_npc.id}...")
    engine.player_ship.lock_phasers(nearest_npc.id)
    print(f"Player locked target: {engine.player_ship.weapons.phaser_locked_target}")
    
    # Process one turn to let NPC AI respond
    print("\n⏱️  Processing turn to allow NPC to respond...")
    engine.debug_mode = True  # Enable debug to see NPC thinking
    
    # Manually trigger NPC AI for the specific ship
    distance = engine.player_ship.position.distance_to(nearest_npc.position)
    engine._execute_basic_npc_ai(nearest_npc, distance, True, True)
    
    # Check if NPC responded
    print(f"\nAfter weapon lock:")
    print(f"NPC shields status: {'UP' if nearest_npc.shields_active else 'DOWN'}")
    print(f"NPC locked target: {nearest_npc.weapons.phaser_locked_target}")
    
    # Verify the response
    success = True
    if not nearest_npc.shields_active:
        print("⚠️  WARNING: NPC did not raise shields in response to weapon lock!")
        success = False
    else:
        print("✅ NPC raised shields in response to weapon lock")
    
    if nearest_npc.weapons.phaser_locked_target != engine.player_ship.id:
        print("⚠️  WARNING: NPC did not lock weapons back on player!")
        success = False
    else:
        print("✅ NPC locked weapons back on player")
    
    # Print any messages
    if engine.messages:
        print("\nGame messages:")
        for msg in engine.messages[-5:]:
            print(f"  {msg}")
    
    return success


def test_starbase_responds_to_weapon_lock():
    """Test that starbases respond to weapon locks as hostile actions."""
    print("\n" + "="*80)
    print("TEST 2: Starbase Response to Weapon Lock")
    print("="*80)
    
    # Initialize game
    engine = GameEngine(universe_seed=12346)
    
    # Find nearest starbase
    from src.universe_objects import Starbase
    nearest_starbase = None
    min_distance = float('inf')
    
    for obj_id, obj in engine.universe_objects.items():
        if isinstance(obj, Starbase):
            dist = engine.player_ship.position.distance_to(obj.position)
            if dist < min_distance:
                min_distance = dist
                nearest_starbase = obj
    
    if not nearest_starbase:
        print("❌ No starbases found!")
        return False
    
    print(f"\nFound starbase: {nearest_starbase.id}")
    print(f"Distance: {min_distance:.1f} AU")
    print(f"Initial shields status: {'UP' if nearest_starbase.shields_active else 'DOWN'}")
    print(f"Stance toward player: {nearest_starbase.stances.get(engine.player_ship.id, 'neutral')}")
    print(f"Fired upon by: {list(nearest_starbase.fired_upon_by)}")
    
    # Lock weapons on the starbase
    print(f"\n🎯 Player locking weapons on {nearest_starbase.id}...")
    engine.player_ship.lock_phasers(nearest_starbase.id)
    print(f"Player locked target: {engine.player_ship.weapons.phaser_locked_target}")
    
    # Process starbase actions to let it respond
    print("\n⏱️  Processing starbase actions to allow response...")
    engine.messages.clear()
    engine._process_starbase_actions()
    
    # Check if starbase responded
    print(f"\nAfter weapon lock:")
    print(f"Starbase shields status: {'UP' if nearest_starbase.shields_active else 'DOWN'}")
    print(f"Fired upon by: {list(nearest_starbase.fired_upon_by)}")
    
    # Verify the response
    success = True
    if engine.player_ship.id not in nearest_starbase.fired_upon_by:
        print("⚠️  WARNING: Starbase did not register player as aggressor!")
        success = False
    else:
        print("✅ Starbase registered player as aggressor")
    
    if not nearest_starbase.shields_active and nearest_starbase.energy > 10.0:
        print("⚠️  WARNING: Starbase did not raise shields in response to weapon lock!")
        success = False
    else:
        print("✅ Starbase raised shields (or had insufficient energy)")
    
    # Print any messages
    if engine.messages:
        print("\nGame messages:")
        for msg in engine.messages:
            print(f"  {msg}")
    
    return success


def test_npc_to_npc_weapon_lock():
    """Test that NPCs respond to weapon locks from other NPCs."""
    print("\n" + "="*80)
    print("TEST 3: NPC-to-NPC Weapon Lock Response")
    print("="*80)
    
    # Initialize game
    engine = GameEngine(universe_seed=12347)
    
    # Find two NPCs
    npc_list = [npc for npc in engine.npc_ships.values() if not npc.is_destroyed]
    
    if len(npc_list) < 2:
        print("❌ Need at least 2 NPC ships!")
        return False
    
    aggressor = npc_list[0]
    target = npc_list[1]
    
    print(f"\nAggressor NPC: {aggressor.id}")
    print(f"Target NPC: {target.id}")
    print(f"Target initial shields: {'UP' if target.shields_active else 'DOWN'}")
    print(f"Target locked: {target.weapons.phaser_locked_target}")
    
    # Have aggressor lock weapons on target
    print(f"\n🎯 {aggressor.id} locking weapons on {target.id}...")
    aggressor.lock_phasers(target.id)
    print(f"Aggressor locked target: {aggressor.weapons.phaser_locked_target}")
    
    # Process target's AI response
    print("\n⏱️  Processing target NPC AI to allow response...")
    engine.debug_mode = True
    distance = aggressor.position.distance_to(target.position)
    engine._execute_basic_npc_ai(target, distance, False, True)
    
    # Check response
    print(f"\nAfter weapon lock:")
    print(f"Target shields: {'UP' if target.shields_active else 'DOWN'}")
    print(f"Target locked: {target.weapons.phaser_locked_target}")
    
    success = True
    if not target.shields_active:
        print("⚠️  WARNING: Target NPC did not raise shields!")
        success = False
    else:
        print("✅ Target NPC raised shields")
    
    if target.weapons.phaser_locked_target != aggressor.id:
        print("⚠️  WARNING: Target NPC did not lock back on aggressor!")
        success = False
    else:
        print("✅ Target NPC locked weapons back on aggressor")
    
    # Print messages
    if engine.messages:
        print("\nGame messages:")
        for msg in engine.messages[-5:]:
            print(f"  {msg}")
    
    return success


def main():
    """Run all weapon lock hostility tests."""
    print("\n" + "#"*80)
    print("# WEAPON LOCK HOSTILITY TESTS")
    print("#"*80)
    
    results = []
    
    # Test 1: NPC response to player weapon lock
    try:
        result1 = test_npc_responds_to_weapon_lock()
        results.append(("NPC response to player lock", result1))
    except Exception as e:
        print(f"❌ Test 1 failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("NPC response to player lock", False))
    
    # Test 2: Starbase response to player weapon lock
    try:
        result2 = test_starbase_responds_to_weapon_lock()
        results.append(("Starbase response to player lock", result2))
    except Exception as e:
        print(f"❌ Test 2 failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Starbase response to player lock", False))
    
    # Test 3: NPC-to-NPC weapon lock response
    try:
        result3 = test_npc_to_npc_weapon_lock()
        results.append(("NPC-to-NPC weapon lock response", result3))
    except Exception as e:
        print(f"❌ Test 3 failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("NPC-to-NPC weapon lock response", False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "#"*80)
    if all_passed:
        print("# ALL TESTS PASSED! ✅")
    else:
        print("# SOME TESTS FAILED! ❌")
    print("#"*80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
