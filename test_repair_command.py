"""
Comprehensive tests for the repair command implementation.

Tests cover:
- Command parsing
- Self-repair when stopped (10% manual)
- Self-repair when moving (should fail for manual, auto-repair should work)
- Repairing other ships
- Repairing friendly starbases
- Error conditions (distance, moving, enemy starbases)
"""

from src.command_parser import CommandParser
from src.game_engine import GameEngine
from src.universe_objects import Position, Starbase


def test_repair_command_parsing():
    """Test that repair command is parsed correctly."""
    print("\n" + "=" * 60)
    print("TEST: Repair Command Parsing")
    print("=" * 60)
    
    parser = CommandParser()
    
    # Test self-repair command
    result = parser.parse("repair")
    assert result is not None
    assert result['command'] == 'repair'
    assert 'target_id' not in result
    print("✓ Self-repair command parsed correctly")
    
    # Test repair with target
    result = parser.parse("repair s123")
    assert result is not None
    assert result['command'] == 'repair'
    assert result['target_id'] == 's123'
    print("✓ Repair with ship target command parsed correctly")
    
    # Test repair with starbase target
    result = parser.parse("repair sb456")
    assert result is not None
    assert result['command'] == 'repair'
    assert result['target_id'] == 'sb456'
    print("✓ Repair starbase command parsed correctly")


def test_self_repair_when_stopped():
    """Test self-repair command when ship is stopped (should repair 10% and disable auto-repair)."""
    print("\n" + "=" * 60)
    print("TEST: Self-Repair When Stopped")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Damage the player ship and ensure it's stopped
    engine.player_ship.damage = 50.0
    engine.player_ship.propulsion.current_speed = 0.0
    print(f"Initial damage: {engine.player_ship.damage}%")
    print(f"Ship speed: {engine.player_ship.propulsion.current_speed} AU/turn")
    
    # Execute self-repair command
    engine.process_turn({'command': 'repair'})
    
    # Should repair 10% and NOT get additional auto-repair
    # 50% - 10% = 40%
    expected_damage = 40.0
    actual_damage = engine.player_ship.damage
    
    print(f"After manual repair: {actual_damage}%")
    print(f"Expected: {expected_damage}%")
    
    assert abs(actual_damage - expected_damage) < 0.1, f"Expected {expected_damage}%, got {actual_damage}%"
    print("✓ Ship repaired 10% without auto-repair stacking")
    
    # Check messages
    repair_msg = [msg for msg in engine.messages if 'Self-repair' in msg and '10.0%' in msg]
    assert len(repair_msg) > 0, "Expected self-repair message"
    print(f"✓ Repair message: {repair_msg[0]}")


def test_self_repair_when_moving():
    """Test that manual self-repair fails when moving, but auto-repair still works."""
    print("\n" + "=" * 60)
    print("TEST: Self-Repair When Moving")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Damage the player ship and set it moving
    engine.player_ship.damage = 50.0
    engine.player_ship.propulsion.current_speed = 5.0
    engine.player_ship.propulsion.warp_active = True
    print(f"Initial damage: {engine.player_ship.damage}%")
    print(f"Ship speed: {engine.player_ship.propulsion.current_speed} AU/turn")
    
    # Try to execute self-repair command (should fail)
    engine.process_turn({'command': 'repair'})
    
    # Should get auto-repair of 1% while moving, not manual repair
    # 50% - 1% = 49%
    expected_damage = 49.0
    actual_damage = engine.player_ship.damage
    
    print(f"After attempted manual repair: {actual_damage}%")
    print(f"Expected (auto-repair only): {expected_damage}%")
    
    assert abs(actual_damage - expected_damage) < 0.1, f"Expected {expected_damage}%, got {actual_damage}%"
    print("✓ Manual repair blocked, auto-repair worked (1%)")
    
    # Check error message
    error_msg = [msg for msg in engine.messages if 'must be stopped' in msg]
    assert len(error_msg) > 0, "Expected error message about being stopped"
    print(f"✓ Error message: {error_msg[0]}")


def test_auto_repair_when_stopped_no_command():
    """Test that auto-repair still works when stopped with no repair command."""
    print("\n" + "=" * 60)
    print("TEST: Auto-Repair When Stopped (No Manual Command)")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Damage the player ship and ensure it's stopped
    engine.player_ship.damage = 50.0
    engine.player_ship.propulsion.current_speed = 0.0
    engine.player_ship.crew = 1000  # Full crew
    print(f"Initial damage: {engine.player_ship.damage}%")
    print(f"Ship speed: {engine.player_ship.propulsion.current_speed} AU/turn")
    print(f"Crew: {engine.player_ship.crew}")
    
    # Process turn with skip command (no repair)
    engine.process_turn({'command': 'skip'})
    
    # Should get auto-repair of 5% (full crew, stationary)
    # 50% - 5% = 45%
    expected_damage = 45.0
    actual_damage = engine.player_ship.damage
    
    print(f"After auto-repair: {actual_damage}%")
    print(f"Expected: {expected_damage}%")
    
    assert abs(actual_damage - expected_damage) < 0.1, f"Expected {expected_damage}%, got {actual_damage}%"
    print("✓ Auto-repair worked correctly (5% for stationary with full crew)")


def test_repair_other_ship():
    """Test repairing another ship when within 0.5 AU and stopped."""
    print("\n" + "=" * 60)
    print("TEST: Repair Other Ship")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Stop the player ship
    engine.player_ship.propulsion.current_speed = 0.0
    
    # Get an enemy ship and position it near the player
    enemy_id = list(engine.enemy_ships.keys())[0]
    enemy_ship = engine.enemy_ships[enemy_id]
    
    # Position enemy very close to player (within 0.5 AU)
    enemy_ship.position = Position(
        engine.player_ship.position.x + 0.3,
        engine.player_ship.position.y + 0.3
    )
    
    # Damage the enemy ship
    enemy_ship.damage = 40.0
    print(f"Enemy ship {enemy_id} initial damage: {enemy_ship.damage}%")
    print(f"Distance: {engine.player_ship.position.distance_to(enemy_ship.position):.2f} AU")
    
    # Execute repair command on enemy ship
    engine.process_turn({'command': 'repair', 'target_id': enemy_id})
    
    # Should repair 5% without auto-repair stacking
    # 40% - 5% = 35%
    expected_damage = 35.0
    actual_damage = enemy_ship.damage
    
    print(f"After repair: {actual_damage}%")
    print(f"Expected: {expected_damage}%")
    
    assert abs(actual_damage - expected_damage) < 0.1, f"Expected {expected_damage}%, got {actual_damage}%"
    print(f"✓ Enemy ship repaired 5% without auto-repair")
    
    # Check messages
    repair_msg = [msg for msg in engine.messages if 'Repairing' in msg and enemy_id in msg and '5.0%' in msg]
    assert len(repair_msg) > 0, "Expected repair message"
    print(f"✓ Repair message: {repair_msg[0]}")


def test_repair_friendly_starbase():
    """Test repairing a friendly starbase at 2% per turn."""
    print("\n" + "=" * 60)
    print("TEST: Repair Friendly Starbase")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Stop the player ship
    engine.player_ship.propulsion.current_speed = 0.0
    
    # Find or create a friendly starbase near the player
    friendly_starbase = None
    starbase_id = None
    
    for obj_id, obj in engine.universe_objects.items():
        if isinstance(obj, Starbase) and obj.friendly_to_player:
            friendly_starbase = obj
            starbase_id = obj_id
            break
    
    if friendly_starbase:
        # Position starbase close to player
        friendly_starbase.position = Position(
            engine.player_ship.position.x + 0.4,
            engine.player_ship.position.y
        )
        
        # Damage the starbase
        friendly_starbase.damage = 30.0
        print(f"Starbase {starbase_id} initial damage: {friendly_starbase.damage}%")
        print(f"Distance: {engine.player_ship.position.distance_to(friendly_starbase.position):.2f} AU")
        
        # Execute repair command on starbase
        engine.process_turn({'command': 'repair', 'target_id': starbase_id})
        
        # Should repair 2%
        # 30% - 2% = 28%
        expected_damage = 28.0
        actual_damage = friendly_starbase.damage
        
        print(f"After repair: {actual_damage}%")
        print(f"Expected: {expected_damage}%")
        
        assert abs(actual_damage - expected_damage) < 0.1, f"Expected {expected_damage}%, got {actual_damage}%"
        print(f"✓ Friendly starbase repaired 2%")
        
        # Check messages
        repair_msg = [msg for msg in engine.messages if 'starbase' in msg and starbase_id in msg and '2.0%' in msg]
        assert len(repair_msg) > 0, "Expected starbase repair message"
        print(f"✓ Repair message: {repair_msg[0]}")
    else:
        print("⚠ No friendly starbase found, skipping test")


def test_repair_error_too_far():
    """Test error when trying to repair a ship too far away."""
    print("\n" + "=" * 60)
    print("TEST: Error - Target Too Far")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Stop the player ship
    engine.player_ship.propulsion.current_speed = 0.0
    
    # Get an enemy ship and position it far from player
    enemy_id = list(engine.enemy_ships.keys())[0]
    enemy_ship = engine.enemy_ships[enemy_id]
    enemy_ship.position = Position(
        engine.player_ship.position.x + 10.0,  # 10 AU away
        engine.player_ship.position.y
    )
    initial_damage = 40.0
    enemy_ship.damage = initial_damage
    
    distance = engine.player_ship.position.distance_to(enemy_ship.position)
    print(f"Distance to target: {distance:.2f} AU (limit is 0.5 AU)")
    
    # Try to repair
    engine.process_turn({'command': 'repair', 'target_id': enemy_id})
    
    # The enemy AI might cause it to move, which gives 1% auto-repair
    # The key point is it should NOT get 5% manual repair
    # So damage should be either:
    # - 35% if stopped (5% auto-repair)
    # - 39% if moving (1% auto-repair)
    # But NOT 35% from manual repair (which would be 40% - 5% manual = 35%)
    final_damage = enemy_ship.damage
    
    print(f"Enemy damage after turn: {final_damage}%")
    print(f"Initial damage: {initial_damage}%")
    
    # Manual repair would reduce by exactly 5%, so if we got manual repair
    # we'd see 35.0% damage. Any other value means we didn't get manual repair.
    # With auto-repair we expect 39% (moving) or 35% (stopped with full crew auto)
    manual_repair_damage = initial_damage - 5.0  # Would be 35% if manual repair happened
    
    # Check that we didn't get exactly the manual repair amount when stopped
    # (we might get 35% from auto-repair if enemy stopped, but then speed would be 0)
    if abs(final_damage - manual_repair_damage) < 0.1:
        # Could be manual or auto - check if the ship is stopped
        assert enemy_ship.propulsion.current_speed > 0, "Got manual repair when should have been blocked"
        print(f"✓ Damage reduced by auto-repair (enemy moving at {enemy_ship.propulsion.current_speed} AU/turn)")
    else:
        print(f"✓ Manual repair blocked (damage went from {initial_damage}% to {final_damage}%)")
    
    # Check error message
    error_msg = [msg for msg in engine.messages if 'too far away' in msg]
    assert len(error_msg) > 0, "Expected error message about distance"
    print(f"✓ Error message: {error_msg[0]}")


def test_repair_error_while_moving():
    """Test error when trying to repair another ship while moving."""
    print("\n" + "=" * 60)
    print("TEST: Error - Repairing While Moving")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Set player ship moving
    engine.player_ship.propulsion.current_speed = 5.0
    
    # Get an enemy ship and position it close
    enemy_id = list(engine.enemy_ships.keys())[0]
    enemy_ship = engine.enemy_ships[enemy_id]
    enemy_ship.position = Position(
        engine.player_ship.position.x + 0.3,
        engine.player_ship.position.y
    )
    enemy_ship.damage = 40.0
    
    print(f"Ship speed: {engine.player_ship.propulsion.current_speed} AU/turn")
    
    # Try to repair
    engine.process_turn({'command': 'repair', 'target_id': enemy_id})
    
    # Damage should not change (except for auto-repair)
    # Enemy was moving, so it got 1% auto-repair: 40% - 1% = 39%
    assert enemy_ship.damage == 39.0, "Ship should only get auto-repair"
    print("✓ Target ship not manually repaired while player is moving")
    
    # Check error message
    error_msg = [msg for msg in engine.messages if 'must be stopped' in msg]
    assert len(error_msg) > 0, "Expected error message about being stopped"
    print(f"✓ Error message: {error_msg[0]}")


def test_repair_error_enemy_starbase():
    """Test error when trying to repair an enemy starbase."""
    print("\n" + "=" * 60)
    print("TEST: Error - Cannot Repair Enemy Starbase")
    print("=" * 60)
    
    engine = GameEngine(universe_seed=42)
    
    # Stop the player ship
    engine.player_ship.propulsion.current_speed = 0.0
    
    # Find an enemy starbase
    enemy_starbase = None
    starbase_id = None
    
    for obj_id, obj in engine.universe_objects.items():
        if isinstance(obj, Starbase) and not obj.friendly_to_player:
            enemy_starbase = obj
            starbase_id = obj_id
            break
    
    if enemy_starbase:
        # Position starbase close to player
        enemy_starbase.position = Position(
            engine.player_ship.position.x + 0.4,
            engine.player_ship.position.y
        )
        enemy_starbase.damage = 30.0
        
        print(f"Enemy starbase {starbase_id} damage: {enemy_starbase.damage}%")
        
        # Try to repair enemy starbase
        engine.process_turn({'command': 'repair', 'target_id': starbase_id})
        
        # Damage should not change
        assert enemy_starbase.damage == 30.0, "Enemy starbase should not be repaired"
        print("✓ Enemy starbase not repaired")
        
        # Check error message
        error_msg = [msg for msg in engine.messages if 'Cannot repair enemy starbase' in msg]
        assert len(error_msg) > 0, "Expected error message about enemy starbase"
        print(f"✓ Error message: {error_msg[0]}")
    else:
        print("⚠ No enemy starbase found, skipping test")


def run_all_tests():
    """Run all repair command tests."""
    print("\n" + "=" * 60)
    print("REPAIR COMMAND - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_repair_command_parsing,
        test_self_repair_when_stopped,
        test_self_repair_when_moving,
        test_auto_repair_when_stopped_no_command,
        test_repair_other_ship,
        test_repair_friendly_starbase,
        test_repair_error_too_far,
        test_repair_error_while_moving,
        test_repair_error_enemy_starbase,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n❌ FAILED: {test.__name__}")
            print(f"   Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n❌ ERROR in {test.__name__}")
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
