#!/usr/bin/env python3
"""
Test script to verify NPC ships can attack starbases.
This tests:
1. NPC ships identify hostile starbases as targets
2. NPC ships attack hostile starbases with phasers and torpedoes
3. NPC ships prioritize hostile ships over starbases
4. NPC ships coordinate attacks on starbases with friendly NPCs
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game_engine import GameEngine
from src.ship import Ship
from src.universe_objects import Position, Starbase

def test_npc_identifies_hostile_starbase():
    """Test that NPC ships identify hostile starbases as targets."""
    print("\n" + "=" * 70)
    print("TEST 1: NPC Identifies Hostile Starbase as Target")
    print("=" * 70)
    
    engine = GameEngine()
    
    # Get an NPC ship
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    
    # Position NPC ship
    npc_ship.position = Position(500.0, 500.0)
    npc_ship.damage = 10.0
    npc_ship.behavior_trait = 'aggressive'
    
    # Create a hostile starbase nearby
    hostile_sb = Starbase("sb_test1", Position(510.0, 505.0))
    hostile_sb.shields = 100.0
    hostile_sb.damage = 0.0
    hostile_sb.stances[npc_id] = 'neutral'
    npc_ship.stances[hostile_sb.id] = 'hostile'
    engine.universe_objects[hostile_sb.id] = hostile_sb
    
    distance = npc_ship.position.distance_to(hostile_sb.position)
    print(f"NPC Ship: {npc_id} at (500, 500)")
    print(f"Hostile Starbase: {hostile_sb.id} at (510, 505)")
    print(f"Distance: {distance:.1f} AU")
    print(f"NPC stance toward starbase: {npc_ship.stances.get(hostile_sb.id, 'neutral')}")
    
    # Move player far away so NPC focuses on starbase
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    # Debug: Print all stances
    print(f"\nDebug - NPC {npc_id} stances: {npc_ship.stances}")
    print(f"Debug - Checking if starbase {hostile_sb.id} is in universe_objects: {hostile_sb.id in engine.universe_objects}")
    print(f"Debug - Type of starbase object: {type(hostile_sb)}")
    print(f"Debug - Starbase in universe_objects type: {type(engine.universe_objects.get(hostile_sb.id, 'NOT FOUND'))}")
    
    # Run AI decision
    distance_to_player = npc_ship.position.distance_to(engine.player_ship.position)
    engine._execute_basic_npc_ai(npc_ship, distance_to_player, False, True)
    
    # Check messages for starbase targeting
    print(f"\nDebug - All messages: {engine.messages}")
    recent_messages = [msg for msg in engine.messages[-10:] if hostile_sb.id in msg]
    
    if recent_messages:
        print(f"\n✓ SUCCESS: NPC is targeting hostile starbase!")
        for msg in recent_messages:
            print(f"  {msg}")
        return True
    else:
        print(f"\n✗ FAILED: NPC did not target hostile starbase")
        print(f"Recent messages: {engine.messages[-5:]}")
        return False


def test_npc_attacks_starbase_with_weapons():
    """Test that NPC ships attack starbases with phasers and torpedoes."""
    print("\n" + "=" * 70)
    print("TEST 2: NPC Attacks Starbase with Weapons")
    print("=" * 70)
    
    engine = GameEngine()
    
    # Get an NPC ship
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    
    # Position NPC ship close to starbase (within phaser range)
    npc_ship.position = Position(500.0, 500.0)
    npc_ship.damage = 10.0
    npc_ship.behavior_trait = 'aggressive'
    npc_ship.energy = 100.0
    
    # Create a hostile starbase nearby
    hostile_sb = Starbase("sb_test2", Position(505.0, 500.0))
    hostile_sb.shields = 100.0
    hostile_sb.shields_active = True
    hostile_sb.damage = 0.0
    npc_ship.stances[hostile_sb.id] = 'hostile'
    engine.universe_objects[hostile_sb.id] = hostile_sb
    
    initial_shields = hostile_sb.shields
    initial_damage = hostile_sb.damage
    
    print(f"Initial starbase state:")
    print(f"  Shields: {initial_shields}%")
    print(f"  Damage: {initial_damage}%")
    
    # Move player far away
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    # Run multiple turns to allow NPC to attack
    attacks_observed = 0
    for turn in range(20):
        distance_to_player = npc_ship.position.distance_to(engine.player_ship.position)
        engine._execute_basic_npc_ai(npc_ship, distance_to_player, False, False)
        
        # Check if starbase took damage
        if hostile_sb.shields < initial_shields or hostile_sb.damage > initial_damage:
            attacks_observed += 1
            print(f"\nTurn {turn + 1}: Attack detected!")
            print(f"  Starbase shields: {hostile_sb.shields:.2f}%")
            print(f"  Starbase damage: {hostile_sb.damage:.2f}%")
            initial_shields = hostile_sb.shields
            initial_damage = hostile_sb.damage
    
    if attacks_observed > 0:
        print(f"\n✓ SUCCESS: NPC attacked starbase {attacks_observed} times!")
        return True
    else:
        print(f"\n✗ FAILED: NPC did not attack starbase")
        return False


def test_npc_prioritizes_hostile_ships():
    """Test that NPC ships prioritize hostile ships over starbases."""
    print("\n" + "=" * 70)
    print("TEST 3: NPC Prioritizes Hostile Ships Over Starbases")
    print("=" * 70)
    
    engine = GameEngine()
    
    # Get two NPC ships
    npc_ids = list(engine.npc_ships.keys())[:2]
    attacker = engine.npc_ships[npc_ids[0]]
    hostile_npc = engine.npc_ships[npc_ids[1]]
    
    # Position attacker
    attacker.position = Position(500.0, 500.0)
    attacker.damage = 10.0
    attacker.behavior_trait = 'aggressive'
    
    # Position hostile NPC ship nearby
    hostile_npc.position = Position(515.0, 505.0)
    hostile_npc.damage = 40.0
    attacker.stances[hostile_npc.id] = 'hostile'
    
    # Create hostile starbase even closer
    hostile_sb = Starbase("sb_test3", Position(508.0, 502.0))
    hostile_sb.shields = 100.0
    hostile_sb.damage = 0.0
    attacker.stances[hostile_sb.id] = 'hostile'
    engine.universe_objects[hostile_sb.id] = hostile_sb
    
    dist_to_ship = attacker.position.distance_to(hostile_npc.position)
    dist_to_sb = attacker.position.distance_to(hostile_sb.position)
    
    print(f"Attacker: {npc_ids[0]} at (500, 500)")
    print(f"Hostile Ship: {npc_ids[1]} at (515, 505) - {dist_to_ship:.1f} AU away, {hostile_npc.damage}% damage")
    print(f"Hostile Starbase: {hostile_sb.id} at (508, 502) - {dist_to_sb:.1f} AU away (CLOSER)")
    print(f"\nExpected: Attacker should target the hostile ship, not the starbase")
    
    # Move player far away
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    # Run AI decision for multiple turns to give it a chance to attack
    # (torpedo firing has 20% random chance per turn)
    ship_attacked = False
    starbase_attacked = False
    for _ in range(10):
        distance_to_player = attacker.position.distance_to(engine.player_ship.position)
        engine._execute_basic_npc_ai(attacker, distance_to_player, False, True)
        
        # Check messages for ship vs starbase targeting
        recent_messages = engine.messages[-10:]
        # Look for actual attack messages (not just debug target selection)
        attack_messages = [msg for msg in recent_messages if 'fires' in msg or 'launches' in msg]
        
        if any(npc_ids[1] in msg for msg in attack_messages):
            ship_attacked = True
            break
        if any(hostile_sb.id in msg for msg in attack_messages):
            starbase_attacked = True
            break
    
    if ship_attacked and not starbase_attacked:
        print(f"\n✓ SUCCESS: NPC correctly prioritized hostile ship over starbase!")
        recent_messages = engine.messages[-10:]
        attack_messages = [msg for msg in recent_messages if 'fires' in msg or 'launches' in msg]
        for msg in attack_messages:
            print(f"  {msg}")
        return True
    elif starbase_attacked:
        print(f"\n✗ FAILED: NPC targeted starbase instead of hostile ship")
        recent_messages = engine.messages[-15:]
        for msg in recent_messages:
            print(f"  {msg}")
        return False
    else:
        print(f"\n⚠ WARNING: No attack observed in 10 turns")
        recent_messages = engine.messages[-15:]
        for msg in recent_messages:
            print(f"  {msg}")
        return False


def test_npc_disengages_starbase_when_hostile_ship_appears():
    """Test that NPC disengages from starbase attack when hostile ship appears."""
    print("\n" + "=" * 70)
    print("TEST 4: NPC Disengages Starbase When Hostile Ship Appears")
    print("=" * 70)
    
    engine = GameEngine()
    
    # Get two NPC ships
    npc_ids = list(engine.npc_ships.keys())[:2]
    attacker = engine.npc_ships[npc_ids[0]]
    hostile_npc = engine.npc_ships[npc_ids[1]]
    
    # Position attacker near starbase
    attacker.position = Position(500.0, 500.0)
    attacker.damage = 10.0
    attacker.behavior_trait = 'aggressive'
    
    # Create hostile starbase nearby
    hostile_sb = Starbase("sb_test4", Position(505.0, 500.0))
    hostile_sb.shields = 100.0
    hostile_sb.damage = 0.0
    attacker.stances[hostile_sb.id] = 'hostile'
    engine.universe_objects[hostile_sb.id] = hostile_sb
    
    # Position hostile ship far away initially
    hostile_npc.position = Position(1000.0, 1000.0)
    attacker.stances[hostile_npc.id] = 'hostile'
    
    # Move player far away
    engine.player_ship.position = Position(5000.0, 5000.0)
    
    print(f"Phase 1: NPC attacks starbase (hostile ship far away)")
    print(f"  Attacker: {npc_ids[0]} at (500, 500)")
    print(f"  Hostile Starbase: {hostile_sb.id} at (505, 500)")
    print(f"  Hostile Ship: {npc_ids[1]} at (1000, 1000) - far away")
    
    # Run a few turns - should attack starbase
    for turn in range(5):
        distance_to_player = attacker.position.distance_to(engine.player_ship.position)
        engine._execute_basic_npc_ai(attacker, distance_to_player, False, False)
    
    starbase_attacked = hostile_sb.damage > 0 or hostile_sb.shields < 100
    print(f"\n  Starbase attacked: {starbase_attacked}")
    print(f"  Starbase state: Shields={hostile_sb.shields:.1f}%, Damage={hostile_sb.damage:.1f}%")
    
    # Now move hostile ship nearby
    hostile_npc.position = Position(510.0, 505.0)
    hostile_npc.damage = 30.0
    
    print(f"\nPhase 2: Hostile ship appears nearby")
    print(f"  Hostile Ship moved to: (510, 505) - {attacker.position.distance_to(hostile_npc.position):.1f} AU")
    
    # Run AI decision
    distance_to_player = attacker.position.distance_to(engine.player_ship.position)
    engine._execute_basic_npc_ai(attacker, distance_to_player, False, True)
    
    # Check if NPC switched targets
    recent_messages = engine.messages[-10:]
    ship_targeted = any(npc_ids[1] in msg for msg in recent_messages)
    disengage_message = any("Disengaging starbase" in msg or "hostile ship" in msg for msg in recent_messages)
    
    if ship_targeted or disengage_message:
        print(f"\n✓ SUCCESS: NPC disengaged from starbase to engage hostile ship!")
        for msg in recent_messages:
            if npc_ids[1] in msg or "Disengaging" in msg:
                print(f"  {msg}")
        return True
    else:
        print(f"\n✗ FAILED: NPC did not disengage from starbase")
        print(f"Recent messages: {recent_messages}")
        return False


def main():
    print("\n" + "=" * 70)
    print("NPC STARBASE ATTACK TEST SUITE")
    print("=" * 70)
    print("Testing NPC ability to attack starbases and prioritize targets")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("Identify Hostile Starbase", test_npc_identifies_hostile_starbase()))
    results.append(("Attack Starbase with Weapons", test_npc_attacks_starbase_with_weapons()))
    results.append(("Prioritize Hostile Ships", test_npc_prioritizes_hostile_ships()))
    results.append(("Disengage When Ship Appears", test_npc_disengages_starbase_when_hostile_ship_appears()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
