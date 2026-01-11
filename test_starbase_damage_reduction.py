#!/usr/bin/env python3
"""
Test script to verify that starbases take 25% of ship damage from weapons.

Expected Results:
- Phasers: 1.25% damage (25% of 5%)
- Torpedoes: 5% shield damage (25% of 20%), 2.5% hull damage (25% of 10%)
"""

import sys

from src.game_engine import GameEngine
from src.ship import Ship, Position
from src.universe_objects import Starbase

def test_phaser_vs_starbase_shields():
    """Test phaser damage against starbase with shields up."""
    print("\n" + "="*70)
    print("TEST 1: Phaser vs Starbase with Shields Up")
    print("="*70)
    print("Expected: 1.25% shield damage (25% of ship's 5% damage)")
    
    game = GameEngine()
    game.player_ship.position = Position(100.0, 100.0)
    
    # Create a hostile starbase
    starbase = Starbase("sb1", Position(105.0, 100.0))
    starbase.shields = 100.0
    starbase.shields_active = True
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    game.universe_objects["sb1"] = starbase
    
    # Lock and fire phasers
    game.player_ship.weapons.phaser_locked_target = "sb1"
    
    print(f"\nBefore firing:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Execute phaser fire
    game._execute_fire(game.player_ship)
    
    print(f"\nAfter firing:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Shield damage taken: {100.0 - starbase.shields:.2f}%")
    
    expected_damage = 5.0 * 0.25
    actual_damage = 100.0 - starbase.shields
    
    if abs(actual_damage - expected_damage) < 0.01:
        print(f"\n✓ PASS: Phaser did {actual_damage:.2f}% damage (expected {expected_damage:.2f}%)")
    else:
        print(f"\n✗ FAIL: Expected {expected_damage:.2f}% but got {actual_damage:.2f}%")
    
    return abs(actual_damage - expected_damage) < 0.01


def test_phaser_vs_starbase_no_shields():
    """Test phaser damage against starbase with shields down."""
    print("\n" + "="*70)
    print("TEST 2: Phaser vs Starbase with Shields Down")
    print("="*70)
    print("Expected: 1.25% hull damage (25% of ship's 5% damage)")
    
    game = GameEngine()
    game.player_ship.position = Position(100.0, 100.0)
    
    # Create a hostile starbase with shields down
    starbase = Starbase("sb1", Position(105.0, 100.0))
    starbase.shields = 0.0
    starbase.shields_active = False
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    game.universe_objects["sb1"] = starbase
    
    # Lock and fire phasers
    game.player_ship.weapons.phaser_locked_target = "sb1"
    
    print(f"\nBefore firing:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Execute phaser fire
    game._execute_fire(game.player_ship)
    
    print(f"\nAfter firing:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Hull damage taken: {starbase.damage:.2f}%")
    
    expected_damage = 5.0 * 0.25
    actual_damage = starbase.damage
    
    if abs(actual_damage - expected_damage) < 0.01:
        print(f"\n✓ PASS: Phaser did {actual_damage:.2f}% damage (expected {expected_damage:.2f}%)")
    else:
        print(f"\n✗ FAIL: Expected {expected_damage:.2f}% but got {actual_damage:.2f}%")
    
    return abs(actual_damage - expected_damage) < 0.01


def test_torpedo_vs_starbase_full_shields():
    """Test torpedo damage against starbase with full shields."""
    print("\n" + "="*70)
    print("TEST 3: Torpedo vs Starbase with Full Shields")
    print("="*70)
    print("Expected: 5% shield damage (25% of ship's 20% damage)")
    
    game = GameEngine()
    game.player_ship.position = Position(100.0, 100.0)
    game.player_ship.torpedos = 50
    
    # Create a hostile starbase
    starbase = Starbase("sb1", Position(102.0, 100.0))
    starbase.shields = 100.0
    starbase.shields_active = True
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    game.universe_objects["sb1"] = starbase
    
    print(f"\nBefore torpedo:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Fire torpedo and move it to hit immediately
    game._execute_torpedo(game.player_ship, "sb1")
    
    # Find the torpedo and move it to the starbase
    if game.player_ship.weapons.active_torpedos:
        torpedo = game.player_ship.weapons.active_torpedos[0]
        torpedo['current_pos'] = Position(starbase.position.x - 1.5, starbase.position.y)
        
        # Process torpedo movement
        game._update_torpedos()
    
    print(f"\nAfter torpedo hit:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Shield damage taken: {100.0 - starbase.shields:.2f}%")
    
    expected_shield_damage = 20.0 * 0.25
    actual_shield_damage = 100.0 - starbase.shields
    
    if abs(actual_shield_damage - expected_shield_damage) < 0.01 and starbase.damage == 0.0:
        print(f"\n✓ PASS: Torpedo did {actual_shield_damage:.2f}% shield damage (expected {expected_shield_damage:.2f}%)")
        print(f"         No hull damage (shields absorbed all damage)")
    else:
        print(f"\n✗ FAIL: Expected {expected_shield_damage:.2f}% shield damage but got {actual_shield_damage:.2f}%")
        print(f"         Expected 0% hull damage but got {starbase.damage:.2f}%")
    
    return abs(actual_shield_damage - expected_shield_damage) < 0.01 and starbase.damage == 0.0


def test_torpedo_vs_starbase_no_shields():
    """Test torpedo damage against starbase with no shields."""
    print("\n" + "="*70)
    print("TEST 4: Torpedo vs Starbase with No Shields")
    print("="*70)
    print("Expected: 2.5% hull damage (25% of ship's 10% damage)")
    
    game = GameEngine()
    game.player_ship.position = Position(100.0, 100.0)
    game.player_ship.torpedos = 50
    
    # Create a hostile starbase with no shields
    starbase = Starbase("sb1", Position(102.0, 100.0))
    starbase.shields = 0.0
    starbase.shields_active = False
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    game.universe_objects["sb1"] = starbase
    
    print(f"\nBefore torpedo:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Fire torpedo and move it to hit immediately
    game._execute_torpedo(game.player_ship, "sb1")
    
    # Find the torpedo and move it to the starbase
    if game.player_ship.weapons.active_torpedos:
        torpedo = game.player_ship.weapons.active_torpedos[0]
        torpedo['current_pos'] = Position(starbase.position.x - 1.5, starbase.position.y)
        
        # Process torpedo movement
        game._update_torpedos()
    
    print(f"\nAfter torpedo hit:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Hull damage taken: {starbase.damage:.2f}%")
    
    expected_hull_damage = 10.0 * 0.25
    actual_hull_damage = starbase.damage
    
    if abs(actual_hull_damage - expected_hull_damage) < 0.01:
        print(f"\n✓ PASS: Torpedo did {actual_hull_damage:.2f}% hull damage (expected {expected_hull_damage:.2f}%)")
    else:
        print(f"\n✗ FAIL: Expected {expected_hull_damage:.2f}% but got {actual_hull_damage:.2f}%")
    
    return abs(actual_hull_damage - expected_hull_damage) < 0.01


def test_torpedo_vs_starbase_partial_shields():
    """Test torpedo damage against starbase with partial shields."""
    print("\n" + "="*70)
    print("TEST 5: Torpedo vs Starbase with Partial Shields (3%)")
    print("="*70)
    print("Expected: 3% shield damage, remaining damage to hull")
    print("         Shield absorbs 3%, leaving 2% worth of shield damage")
    print("         2% shield damage converts to ~1% hull damage")
    
    game = GameEngine()
    game.player_ship.position = Position(100.0, 100.0)
    game.player_ship.torpedos = 50
    
    # Create a hostile starbase with low shields
    starbase = Starbase("sb1", Position(102.0, 100.0))
    starbase.shields = 3.0
    starbase.shields_active = True
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    game.universe_objects["sb1"] = starbase
    
    print(f"\nBefore torpedo:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Fire torpedo and move it to hit immediately
    game._execute_torpedo(game.player_ship, "sb1")
    
    # Find the torpedo and move it to the starbase
    if game.player_ship.weapons.active_torpedos:
        torpedo = game.player_ship.weapons.active_torpedos[0]
        torpedo['current_pos'] = Position(starbase.position.x - 1.5, starbase.position.y)
        
        # Process torpedo movement
        game._update_torpedos()
    
    print(f"\nAfter torpedo hit:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Shield damage taken: {3.0 - starbase.shields:.2f}%")
    print(f"  Hull damage taken: {starbase.damage:.2f}%")
    
    # Shields should be depleted (3% absorbed)
    # Remaining: 5% - 3% = 2% shield damage worth
    # This converts to hull damage: min(2.5%, 2% * 0.5) = min(2.5%, 1%) = 1%
    expected_hull_damage = 1.0
    
    if starbase.shields == 0.0 and abs(starbase.damage - expected_hull_damage) < 0.01:
        print(f"\n✓ PASS: Shields depleted and {starbase.damage:.2f}% hull damage (expected ~{expected_hull_damage:.2f}%)")
    else:
        print(f"\n✗ FAIL: Expected shields at 0% and ~{expected_hull_damage:.2f}% hull damage")
        print(f"         Got shields at {starbase.shields:.2f}% and {starbase.damage:.2f}% hull damage")
    
    return starbase.shields == 0.0 and abs(starbase.damage - expected_hull_damage) < 0.01


def test_multiple_hits():
    """Test multiple phaser and torpedo hits on starbase."""
    print("\n" + "="*70)
    print("TEST 6: Multiple Hits on Starbase")
    print("="*70)
    print("Testing 4 phasers (4 × 1.25% = 5%) + 2 torpedoes (2 × 5% = 10%)")
    print("Expected total: 15% shield damage")
    
    game = GameEngine()
    game.player_ship.position = Position(100.0, 100.0)
    game.player_ship.torpedos = 50
    
    # Create a hostile starbase
    starbase = Starbase("sb1", Position(105.0, 100.0))
    starbase.shields = 100.0
    starbase.shields_active = True
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'  # Make it hostile to player
    game.universe_objects["sb1"] = starbase
    
    print(f"\nInitial state:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Fire 4 phasers
    game.player_ship.weapons.phaser_locked_target = "sb1"
    for i in range(4):
        game._execute_fire(game.player_ship)
        print(f"  After phaser {i+1}: Shields = {starbase.shields:.2f}%")
    
    # Fire 2 torpedoes
    for i in range(2):
        game._execute_torpedo(game.player_ship, "sb1")
        if game.player_ship.weapons.active_torpedos:
            torpedo = game.player_ship.weapons.active_torpedos[-1]
            torpedo['current_pos'] = Position(starbase.position.x - 1.5, starbase.position.y)
            game._update_torpedos()
        print(f"  After torpedo {i+1}: Shields = {starbase.shields:.2f}%")
    
    print(f"\nFinal state:")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Total shield damage: {100.0 - starbase.shields:.2f}%")
    
    expected_total = (4 * 1.25) + (2 * 5.0)  # 5% + 10% = 15%
    actual_total = 100.0 - starbase.shields
    
    if abs(actual_total - expected_total) < 0.1:
        print(f"\n✓ PASS: Total damage {actual_total:.2f}% (expected {expected_total:.2f}%)")
    else:
        print(f"\n✗ FAIL: Expected {expected_total:.2f}% but got {actual_total:.2f}%")
    
    return abs(actual_total - expected_total) < 0.1


def main():
    print("\n" + "="*70)
    print("STARBASE DAMAGE REDUCTION TEST SUITE")
    print("="*70)
    print("Verifying that starbases take 25% of ship damage from weapons")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Phaser vs Shields", test_phaser_vs_starbase_shields()))
    results.append(("Phaser vs No Shields", test_phaser_vs_starbase_no_shields()))
    results.append(("Torpedo vs Full Shields", test_torpedo_vs_starbase_full_shields()))
    results.append(("Torpedo vs No Shields", test_torpedo_vs_starbase_no_shields()))
    results.append(("Torpedo vs Partial Shields", test_torpedo_vs_starbase_partial_shields()))
    results.append(("Multiple Hits", test_multiple_hits()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Starbases correctly take 25% of ship damage.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
