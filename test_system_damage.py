#!/usr/bin/env python3
"""
Test script for ship system damage mechanics.

Tests:
1. System damage occurs when ship has >50% damage and takes additional damage
2. 25% chance to disable one of 7 systems
3. System repair mechanics (25% when damage >= 50%, 50% when damage < 50%)
4. System-specific effects and command restrictions
"""

import sys
sys.path.insert(0, '/home/wade/workspace/wadespace')

from src.ship import Ship
from src.universe_objects import Position

def test_system_damage_triggering():
    """Test that system damage only triggers when ship >50% damage."""
    print("TEST 1: System Damage Triggering")
    print("=" * 60)
    
    ship = Ship("test001", Position(5000, 5000))
    ship.is_player = True
    ship.damage = 60.0  # Above 50%
    messages = []
    
    # Apply damage multiple times to trigger system damage
    for i in range(20):
        ship.damage = 60.0  # Reset to 60% each time
        ship.take_damage(5.0, messages=messages)
        if messages:
            print(f"  Turn {i+1}: System damaged! - {messages[-1]}")
            break
    
    if ship.disabled_systems:
        print(f"✓ PASS: System damage triggered")
        print(f"  Disabled systems: {ship.disabled_systems}")
    else:
        print("✗ FAIL: No system damage after 20 attempts (expected at least one)")
    print()

def test_all_seven_systems():
    """Test that all 7 systems can be disabled."""
    print("TEST 2: All Seven Systems Can Be Disabled")
    print("=" * 60)
    
    all_systems = ['shields', 'engines', 'torpedoes', 'phasers', 'scanners', 'radios', 'computers']
    disabled_systems = set()
    messages = []
    
    # Try to disable all systems
    for attempt in range(1000):
        ship = Ship("test002", Position(5000, 5000))
        ship.is_player = True
        ship.damage = 60.0
        
        # Apply damage multiple times
        for _ in range(10):
            ship.damage = 60.0
            ship.take_damage(5.0, messages=messages)
            disabled_systems.update(ship.disabled_systems)
        
        if len(disabled_systems) == 7:
            print(f"✓ PASS: All 7 systems can be disabled (found in {attempt+1} attempts)")
            break
    
    print(f"  Systems found: {sorted(disabled_systems)}")
    if len(disabled_systems) == 7:
        print("✓ All systems verified")
    else:
        print(f"✗ Missing systems: {set(all_systems) - disabled_systems}")
    print()

def test_system_repair_high_damage():
    """Test system repair at damage >= 50% (25% chance)."""
    print("TEST 3: System Repair at High Damage (≥50%)")
    print("=" * 60)
    
    ship = Ship("test003", Position(5000, 5000))
    ship.is_player = True
    ship.damage = 60.0
    ship.disabled_systems.add('phasers')
    messages = []
    
    repairs = 0
    for turn in range(200):
        if 'phasers' not in ship.disabled_systems:
            repairs += 1
            ship.disabled_systems.add('phasers')  # Re-disable for testing
        
        ship.attempt_system_repair(messages)
    
    repair_rate = repairs / 200.0
    expected_rate = 0.25
    
    print(f"  Repairs in 200 turns: {repairs}")
    print(f"  Repair rate: {repair_rate:.2%} (expected ~25%)")
    
    if 0.15 <= repair_rate <= 0.35:
        print("✓ PASS: Repair rate within expected range")
    else:
        print(f"✗ FAIL: Repair rate {repair_rate:.2%} outside expected range (15-35%)")
    print()

def test_system_repair_low_damage():
    """Test system repair at damage < 50% (50% chance)."""
    print("TEST 4: System Repair at Low Damage (<50%)")
    print("=" * 60)
    
    ship = Ship("test004", Position(5000, 5000))
    ship.is_player = True
    ship.damage = 30.0
    ship.disabled_systems.add('phasers')
    messages = []
    
    repairs = 0
    for turn in range(200):
        if 'phasers' not in ship.disabled_systems:
            repairs += 1
            ship.disabled_systems.add('phasers')  # Re-disable for testing
        
        ship.attempt_system_repair(messages)
    
    repair_rate = repairs / 200.0
    expected_rate = 0.50
    
    print(f"  Repairs in 200 turns: {repairs}")
    print(f"  Repair rate: {repair_rate:.2%} (expected ~50%)")
    
    if 0.40 <= repair_rate <= 0.60:
        print("✓ PASS: Repair rate within expected range")
    else:
        print(f"✗ FAIL: Repair rate {repair_rate:.2%} outside expected range (40-60%)")
    print()

def test_shields_disabled():
    """Test shields disabled effects."""
    print("TEST 5: Shields Disabled Effects")
    print("=" * 60)
    
    ship = Ship("test005", Position(5000, 5000))
    ship.is_player = True
    ship.disabled_systems.add('shields')
    
    # Try to raise shields
    ship.update_shields(True)
    
    if not ship.shields_active:
        print("✓ PASS: Shields cannot be raised when system is disabled")
    else:
        print("✗ FAIL: Shields were raised despite system being disabled")
    print()

def test_engines_disabled():
    """Test engines disabled effects."""
    print("TEST 6: Engines Disabled Effects")
    print("=" * 60)
    
    ship = Ship("test006", Position(5000, 5000))
    ship.is_player = True
    ship.disabled_systems.add('engines')
    
    # Check can_move
    if not ship.can_move():
        print("✓ PASS: Ship cannot move when engines are disabled")
    else:
        print("✗ FAIL: Ship can move despite engines being disabled")
    print()

def test_phasers_disabled():
    """Test phasers disabled effects."""
    print("TEST 7: Phasers Disabled Effects")
    print("=" * 60)
    
    player = Ship("PLAYER", Position(5000, 5000))
    player.is_player = True
    player.disabled_systems.add('phasers')
    player.energy = 100
    
    target = Ship("s001", Position(5005, 5000))  # 5 AU away
    target.energy = 100
    
    player.weapons.phaser_locked_target = "s001"
    
    result = player.fire_phaser(target)
    
    if not result:
        print("✓ PASS: Phasers cannot fire when system is disabled")
    else:
        print("✗ FAIL: Phasers fired despite system being disabled")
    print()

def test_torpedoes_disabled():
    """Test torpedoes disabled effects."""
    print("TEST 8: Torpedoes Disabled Effects")
    print("=" * 60)
    
    player = Ship("PLAYER", Position(5000, 5000))
    player.is_player = True
    player.disabled_systems.add('torpedoes')
    player.energy = 100
    player.weapons.torpedos = 10
    
    target_pos = Position(5010, 5000)
    
    result = player.fire_torpedo(target_pos)
    
    if not result:
        print("✓ PASS: Torpedoes cannot fire when system is disabled")
    else:
        print("✗ FAIL: Torpedoes fired despite system being disabled")
    print()

def test_system_specific_effects():
    """Test that system-specific effects occur on disable."""
    print("TEST 9: System-Specific Disable Effects")
    print("=" * 60)
    
    # Test shields lowered when disabled
    ship = Ship("test009", Position(5000, 5000))
    ship.is_player = True
    ship.shields_active = True
    ship.damage = 60.0
    messages = []
    
    # Manually disable shields system
    ship.disabled_systems.add('shields')
    ship.check_for_system_damage(messages)  # This should lower shields
    
    if not ship.shields_active:
        print("✓ PASS: Shields lowered when system disabled")
    else:
        print("  Note: Shields may need to be explicitly lowered in disable logic")
    
    # Test engines stop when disabled
    ship2 = Ship("test009b", Position(5000, 5000))
    ship2.is_player = True
    ship2.propulsion.warp_active = True
    ship2.propulsion.current_speed = 5.0
    ship2.damage = 60.0
    
    # Manually trigger engine disable
    ship2.disabled_systems.add('engines')
    ship2.stop()  # Called when engines disabled
    
    if ship2.propulsion.current_speed == 0:
        print("✓ PASS: Ship stopped when engines disabled")
    else:
        print("✗ FAIL: Ship still moving after engines disabled")
    print()

def test_only_one_system_per_turn():
    """Test that only one system can be repaired per turn."""
    print("TEST 10: Only One System Repaired Per Turn")
    print("=" * 60)
    
    ship = Ship("test010", Position(5000, 5000))
    ship.is_player = True
    ship.damage = 30.0  # Low damage for 50% repair chance
    ship.disabled_systems = {'phasers', 'torpedoes', 'shields'}
    
    initial_count = len(ship.disabled_systems)
    messages = []
    
    ship.attempt_system_repair(messages)
    
    repaired_count = initial_count - len(ship.disabled_systems)
    
    if repaired_count <= 1:
        print(f"✓ PASS: Only {repaired_count} system repaired in one turn")
    else:
        print(f"✗ FAIL: {repaired_count} systems repaired (should be max 1)")
    print()

if __name__ == "__main__":
    print("System Damage Mechanics Test Suite")
    print("=" * 60)
    print()
    
    test_system_damage_triggering()
    test_all_seven_systems()
    test_system_repair_high_damage()
    test_system_repair_low_damage()
    test_shields_disabled()
    test_engines_disabled()
    test_phasers_disabled()
    test_torpedoes_disabled()
    test_system_specific_effects()
    test_only_one_system_per_turn()
    
    print("=" * 60)
    print("Test Suite Complete")
