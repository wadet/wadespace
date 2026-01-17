"""
Test that NPC system damage notifications appear when player's scanners are operational.
"""
import sys
sys.path.insert(0, '/home/wade/workspace/wadespace')

import random
from src.game_engine import GameEngine
from src.universe_objects import Position

def test_npc_system_damage_notifications():
    """Test that player gets notified when NPC systems are disabled (if scanners work)"""
    print("\n=== Testing NPC System Damage Notifications ===\n")
    
    # Create game engine
    engine = GameEngine()
    
    # Position player and NPC close together
    engine.player_ship.position = Position(100, 100)
    
    # Find an NPC ship
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    npc_ship.position = Position(102, 100)  # 2 AU away
    
    # Give player full health and weapons
    engine.player_ship.damage = 0
    engine.player_ship.torpedoes = 10
    engine.player_ship.weapons.phaser_energy = 100.0
    engine.player_ship.shields = 100
    engine.player_ship.shields_active = True
    
    # Ensure player scanners are operational
    if 'scanners' in engine.player_ship.disabled_systems:
        engine.player_ship.disabled_systems.remove('scanners')
    
    # Weaken NPC to increase chance of system damage
    npc_ship.damage = 55.0  # Above 50% threshold
    npc_ship.shields = 0
    npc_ship.shields_active = False
    
    print(f"Initial state:")
    print(f"  Player damage: {engine.player_ship.damage}%")
    print(f"  Player scanners: {'DISABLED' if 'scanners' in engine.player_ship.disabled_systems else 'operational'}")
    print(f"  NPC {npc_id} damage: {npc_ship.damage}%")
    print(f"  NPC {npc_id} disabled systems: {npc_ship.disabled_systems}")
    
    # Fire at NPC multiple times to trigger system damage
    print(f"\nFiring at {npc_id} to trigger system damage...")
    
    max_attempts = 50
    notifications_received = []
    
    for attempt in range(max_attempts):
        # Clear messages
        engine.messages = []
        
        # Record NPC systems before firing
        systems_before = set(npc_ship.disabled_systems)
        
        # Fire phaser at NPC
        engine.player_ship.weapons.phaser_locked_target = npc_id
        engine._execute_fire(engine.player_ship)
        
        # Check if any new systems were disabled
        systems_after = set(npc_ship.disabled_systems)
        new_disabled = systems_after - systems_before
        
        if new_disabled:
            print(f"\n  Attempt {attempt + 1}: System damage detected!")
            print(f"    New disabled systems: {new_disabled}")
            print(f"    Messages received:")
            for msg in engine.messages:
                print(f"      - {msg}")
                if "[SCAN]" in msg and "system has been disabled" in msg:
                    notifications_received.append(msg)
            
            # If we got notification, test passed
            if notifications_received:
                break
        
        # Reset NPC for next attempt if destroyed
        if npc_ship.is_destroyed or npc_ship.damage >= 100:
            npc_ship.damage = 55.0
            npc_ship.is_destroyed = False
            npc_ship.disabled_systems.clear()
    
    print(f"\n--- Results ---")
    print(f"Total attempts: {attempt + 1}")
    print(f"Notifications received: {len(notifications_received)}")
    
    if notifications_received:
        print(f"\n✓ TEST PASSED - Received notifications:")
        for notif in notifications_received:
            print(f"  {notif}")
        return True
    else:
        print(f"\n✗ TEST FAILED - No notifications received after {max_attempts} attempts")
        print(f"  NPC final disabled systems: {npc_ship.disabled_systems}")
        return False


def test_no_notification_when_scanners_disabled():
    """Test that player doesn't get notified when their scanners are disabled"""
    print("\n\n=== Testing No Notifications When Scanners Disabled ===\n")
    
    # Create game engine
    engine = GameEngine()
    
    # Position player and NPC close together
    engine.player_ship.position = Position(100, 100)
    
    # Find an NPC ship
    npc_id = list(engine.npc_ships.keys())[0]
    npc_ship = engine.npc_ships[npc_id]
    npc_ship.position = Position(102, 100)  # 2 AU away
    
    # Give player full health and weapons
    engine.player_ship.damage = 0
    engine.player_ship.torpedoes = 10
    engine.player_ship.weapons.phaser_energy = 100.0
    engine.player_ship.shields = 100
    engine.player_ship.shields_active = True
    
    # DISABLE player scanners
    engine.player_ship.disabled_systems.add('scanners')
    
    # Weaken NPC to increase chance of system damage
    npc_ship.damage = 55.0  # Above 50% threshold
    npc_ship.shields = 0
    npc_ship.shields_active = False
    
    print(f"Initial state:")
    print(f"  Player scanners: {'DISABLED' if 'scanners' in engine.player_ship.disabled_systems else 'operational'}")
    print(f"  NPC {npc_id} damage: {npc_ship.damage}%")
    
    # Fire at NPC multiple times
    print(f"\nFiring at {npc_id} with scanners disabled...")
    
    max_attempts = 50
    notifications_received = []
    systems_disabled = False
    
    for attempt in range(max_attempts):
        # Clear messages
        engine.messages = []
        
        # Record NPC systems before firing
        systems_before = set(npc_ship.disabled_systems)
        
        # Fire phaser at NPC
        engine.player_ship.weapons.phaser_locked_target = npc_id
        engine._execute_fire(engine.player_ship)
        
        # Check if any new systems were disabled
        systems_after = set(npc_ship.disabled_systems)
        new_disabled = systems_after - systems_before
        
        if new_disabled:
            systems_disabled = True
            print(f"\n  Attempt {attempt + 1}: NPC system damaged: {new_disabled}")
            print(f"    Messages received:")
            for msg in engine.messages:
                print(f"      - {msg}")
                if "[SCAN]" in msg and "system has been disabled" in msg:
                    notifications_received.append(msg)
            
            # Keep going to see if any notifications appear
        
        # Reset NPC for next attempt if destroyed
        if npc_ship.is_destroyed or npc_ship.damage >= 100:
            npc_ship.damage = 55.0
            npc_ship.is_destroyed = False
            npc_ship.disabled_systems.clear()
    
    print(f"\n--- Results ---")
    print(f"Total attempts: {max_attempts}")
    print(f"NPC systems disabled: {systems_disabled}")
    print(f"Notifications received: {len(notifications_received)}")
    
    if systems_disabled and not notifications_received:
        print(f"\n✓ TEST PASSED - NPC systems disabled but no notifications (scanners disabled)")
        return True
    elif not systems_disabled:
        print(f"\n⚠ TEST INCONCLUSIVE - No NPC systems disabled during test")
        return None
    else:
        print(f"\n✗ TEST FAILED - Received notifications despite disabled scanners:")
        for notif in notifications_received:
            print(f"  {notif}")
        return False


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    test1_passed = test_npc_system_damage_notifications()
    test2_result = test_no_notification_when_scanners_disabled()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Test 1 (Notifications with operational scanners): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Test 2 (No notifications with disabled scanners): {'✓ PASSED' if test2_result else ('⚠ INCONCLUSIVE' if test2_result is None else '✗ FAILED')}")
    
    if test1_passed and test2_result:
        print("\n✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED OR INCONCLUSIVE")
        sys.exit(1)
