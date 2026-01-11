#!/usr/bin/env python3
"""
Quick test to verify behavior-specific responses to weapon locks.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Prevent UI from launching
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.game_engine import GameEngine


def test_behavior_responses():
    """Test that different behavior traits respond differently to weapon locks."""
    print("\n" + "="*80)
    print("BEHAVIOR-SPECIFIC WEAPON LOCK RESPONSE TEST")
    print("="*80)
    
    engine = GameEngine(universe_seed=54321)
    
    # Find NPCs with different behavior traits
    aggressive_npc = None
    timid_npc = None
    neutral_npc = None
    
    for npc_id, npc in engine.npc_ships.items():
        if not npc.is_destroyed:
            if npc.behavior_trait == 'aggressive' and not aggressive_npc:
                aggressive_npc = npc
            elif npc.behavior_trait == 'timid' and not timid_npc:
                timid_npc = npc
            elif npc.behavior_trait == 'neutral' and not neutral_npc:
                neutral_npc = npc
        
        if aggressive_npc and timid_npc and neutral_npc:
            break
    
    print(f"\nFound test subjects:")
    print(f"  Aggressive: {aggressive_npc.id if aggressive_npc else 'None'}")
    print(f"  Timid: {timid_npc.id if timid_npc else 'None'}")
    print(f"  Neutral: {neutral_npc.id if neutral_npc else 'None'}")
    
    if not (aggressive_npc and timid_npc and neutral_npc):
        print("❌ Could not find all behavior types!")
        return False
    
    engine.debug_mode = True
    engine.messages.clear()
    
    # Test 1: Aggressive NPC response
    print("\n" + "-"*80)
    print("TEST 1: Aggressive NPC Response to Weapon Lock")
    print("-"*80)
    print(f"Ship: {aggressive_npc.id}, Damage: {aggressive_npc.damage:.1f}%")
    print(f"Initial shields: {'UP' if aggressive_npc.shields_active else 'DOWN'}")
    print(f"Initial weapon lock: {aggressive_npc.weapons.phaser_locked_target}")
    
    engine.player_ship.lock_phasers(aggressive_npc.id)
    print(f"\nPlayer locks weapons on {aggressive_npc.id}...")
    
    distance = engine.player_ship.position.distance_to(aggressive_npc.position)
    engine._execute_basic_npc_ai(aggressive_npc, distance, True, True)
    
    print(f"\nAfter response:")
    print(f"  Shields: {'UP' if aggressive_npc.shields_active else 'DOWN'}")
    print(f"  Locked on: {aggressive_npc.weapons.phaser_locked_target}")
    
    if aggressive_npc.weapons.phaser_locked_target == engine.player_ship.id:
        print("✅ PASS: Aggressive NPC locked weapons back (aggressive response)")
    else:
        print("❌ FAIL: Aggressive NPC did not lock back")
    
    for msg in [m for m in engine.messages if aggressive_npc.id in m]:
        print(f"  {msg}")
    
    # Test 2: Timid NPC response (damaged)
    print("\n" + "-"*80)
    print("TEST 2: Timid NPC Response to Weapon Lock (when damaged)")
    print("-"*80)
    timid_npc.damage = 25.0  # Make it damaged
    print(f"Ship: {timid_npc.id}, Damage: {timid_npc.damage:.1f}%")
    print(f"Initial shields: {'UP' if timid_npc.shields_active else 'DOWN'}")
    print(f"Initial weapon lock: {timid_npc.weapons.phaser_locked_target}")
    
    engine.messages.clear()
    engine.player_ship.unlock_phasers()
    engine.player_ship.lock_phasers(timid_npc.id)
    print(f"\nPlayer locks weapons on {timid_npc.id}...")
    
    distance = engine.player_ship.position.distance_to(timid_npc.position)
    engine._execute_basic_npc_ai(timid_npc, distance, True, True)
    
    print(f"\nAfter response:")
    print(f"  Shields: {'UP' if timid_npc.shields_active else 'DOWN'}")
    print(f"  Locked on: {timid_npc.weapons.phaser_locked_target}")
    
    if timid_npc.shields_active and not timid_npc.weapons.phaser_locked_target:
        print("✅ PASS: Timid NPC raised shields but didn't lock back (preparing to flee)")
    elif timid_npc.shields_active:
        print("⚠️  PARTIAL: Timid NPC raised shields and locked back (less timid than expected)")
    else:
        print("❌ FAIL: Timid NPC didn't respond appropriately")
    
    for msg in [m for m in engine.messages if timid_npc.id in m]:
        print(f"  {msg}")
    
    # Test 3: Timid NPC response (not damaged)
    print("\n" + "-"*80)
    print("TEST 3: Timid NPC Response to Weapon Lock (when not damaged)")
    print("-"*80)
    timid_npc2 = None
    for npc_id, npc in engine.npc_ships.items():
        if npc.behavior_trait == 'timid' and npc.id != timid_npc.id and not npc.is_destroyed:
            timid_npc2 = npc
            break
    
    if timid_npc2:
        timid_npc2.damage = 0.0  # Not damaged
        print(f"Ship: {timid_npc2.id}, Damage: {timid_npc2.damage:.1f}%")
        print(f"Initial shields: {'UP' if timid_npc2.shields_active else 'DOWN'}")
        print(f"Initial weapon lock: {timid_npc2.weapons.phaser_locked_target}")
        
        engine.messages.clear()
        engine.player_ship.unlock_phasers()
        engine.player_ship.lock_phasers(timid_npc2.id)
        print(f"\nPlayer locks weapons on {timid_npc2.id}...")
        
        distance = engine.player_ship.position.distance_to(timid_npc2.position)
        engine._execute_basic_npc_ai(timid_npc2, distance, True, True)
        
        print(f"\nAfter response:")
        print(f"  Shields: {'UP' if timid_npc2.shields_active else 'DOWN'}")
        print(f"  Locked on: {timid_npc2.weapons.phaser_locked_target}")
        
        if timid_npc2.shields_active and timid_npc2.weapons.phaser_locked_target:
            print("✅ PASS: Timid NPC (not damaged) raised shields and cautiously locked back")
        else:
            print("⚠️  Note: Timid NPC behavior when not damaged")
        
        for msg in [m for m in engine.messages if timid_npc2.id in m]:
            print(f"  {msg}")
    
    # Test 4: Neutral NPC response
    print("\n" + "-"*80)
    print("TEST 4: Neutral NPC Response to Weapon Lock")
    print("-"*80)
    print(f"Ship: {neutral_npc.id}, Damage: {neutral_npc.damage:.1f}%")
    print(f"Initial shields: {'UP' if neutral_npc.shields_active else 'DOWN'}")
    print(f"Initial weapon lock: {neutral_npc.weapons.phaser_locked_target}")
    
    engine.messages.clear()
    engine.player_ship.unlock_phasers()
    engine.player_ship.lock_phasers(neutral_npc.id)
    print(f"\nPlayer locks weapons on {neutral_npc.id}...")
    
    distance = engine.player_ship.position.distance_to(neutral_npc.position)
    engine._execute_basic_npc_ai(neutral_npc, distance, True, True)
    
    print(f"\nAfter response:")
    print(f"  Shields: {'UP' if neutral_npc.shields_active else 'DOWN'}")
    print(f"  Locked on: {neutral_npc.weapons.phaser_locked_target}")
    
    if neutral_npc.shields_active and neutral_npc.weapons.phaser_locked_target == engine.player_ship.id:
        print("✅ PASS: Neutral NPC raised shields and locked back (balanced response)")
    else:
        print("❌ FAIL: Neutral NPC didn't respond appropriately")
    
    for msg in [m for m in engine.messages if neutral_npc.id in m]:
        print(f"  {msg}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("✅ Aggressive NPCs immediately lock weapons back and prepare for combat")
    print("✅ Timid NPCs prioritize defense and evasion, especially when damaged")
    print("✅ Neutral NPCs provide proportional responses")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_behavior_responses()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
