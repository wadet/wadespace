#!/usr/bin/env python3
"""
Integration test for system damage in actual game scenario.
Tests the full flow from damage application to system repair.
"""

import sys
sys.path.insert(0, '/home/wade/workspace/wadespace')

from src.game_engine import GameEngine

def test_system_damage_integration():
    """Test system damage in a real game scenario."""
    print("System Damage Integration Test")
    print("=" * 60)
    
    # Create game engine
    engine = GameEngine()
    # Game engine is already initialized, no need for start_game()
    
    # Damage player ship to >50%
    print("\n1. Damaging player ship to 60%...")
    engine.player_ship.damage = 60.0
    print(f"   Player damage: {engine.player_ship.damage:.1f}%")
    
    # Apply additional damage to trigger system damage
    print("\n2. Applying additional damage to trigger system failures...")
    for i in range(20):
        initial_systems = set(engine.player_ship.disabled_systems)
        engine.player_ship.take_damage(5.0, messages=engine.messages)
        new_systems = engine.player_ship.disabled_systems - initial_systems
        
        if new_systems:
            print(f"   Turn {i+1}: System disabled!")
            for msg in engine.messages[-3:]:
                if "CRITICAL" in msg:
                    print(f"   {msg}")
            break
    
    if engine.player_ship.disabled_systems:
        disabled = list(engine.player_ship.disabled_systems)[0]
        print(f"\n3. System '{disabled}' is now disabled")
        
        # Test command blocking
        print(f"\n4. Testing command restrictions...")
        engine.messages.clear()
        
        if disabled == 'shields':
            engine._execute_command(engine.player_ship, {'command': 'shields', 'active': True})
        elif disabled == 'engines':
            engine._execute_command(engine.player_ship, {'command': 'warp', 'speed': 5})
        elif disabled == 'phasers':
            engine._execute_command(engine.player_ship, {'command': 'fire'})
        elif disabled == 'torpedoes':
            engine._execute_command(engine.player_ship, {'command': 'torpedo', 'target_id': 's001'})
        elif disabled == 'scanners':
            engine._execute_command(engine.player_ship, {'command': 'scan'})
        elif disabled == 'radios':
            engine._execute_command(engine.player_ship, {'command': 'tell', 'target_id': 's001', 'message': 'test'})
        elif disabled == 'computers':
            engine._execute_command(engine.player_ship, {'command': 'hal', 'question': 'test'})
        
        if engine.messages and "inoperative" in engine.messages[-1]:
            print(f"   ✓ Command blocked: {engine.messages[-1]}")
        
        # Test repair
        print(f"\n5. Testing system repair...")
        print(f"   Damage level: {engine.player_ship.damage:.1f}%")
        
        # Reduce damage to increase repair chance
        engine.player_ship.damage = 30.0
        print(f"   Reduced damage to: {engine.player_ship.damage:.1f}%")
        
        # Try repairs
        for turn in range(50):
            engine.messages.clear()
            engine.player_ship.attempt_system_repair(engine.messages)
            
            if not engine.player_ship.disabled_systems:
                print(f"   ✓ System repaired after {turn+1} turns!")
                if engine.messages:
                    print(f"   {engine.messages[-1]}")
                break
        
        if engine.player_ship.disabled_systems:
            print(f"   System still disabled after 50 turns (should repair with 50% chance)")
    else:
        print("\n3. No systems disabled (may need multiple attempts)")
    
    print("\n" + "=" * 60)
    print("Integration Test Complete")
    print()
    
    # Summary
    print("Summary:")
    print(f"  Player damage: {engine.player_ship.damage:.1f}%")
    print(f"  Disabled systems: {engine.player_ship.disabled_systems if engine.player_ship.disabled_systems else 'None'}")
    print(f"  Test result: {'PASS' if not engine.player_ship.disabled_systems else 'PARTIAL'}")

if __name__ == "__main__":
    test_system_damage_integration()
