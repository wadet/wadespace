#!/usr/bin/env python3
"""
Test script for the tell command with enemy starbases.
"""

from src.game_engine import GameEngine
from src.command_parser import CommandParser
from src.universe_objects import Starbase

def test_starbase_tell():
    """Test the tell command with enemy starbases."""
    print("Initializing game engine...")
    engine = GameEngine(universe_seed=42)
    parser = CommandParser()
    
    # Find an enemy starbase
    enemy_starbase_id = None
    friendly_starbase_id = None
    
    for obj_id, obj in engine.universe_objects.items():
        if isinstance(obj, Starbase):
            if not obj.friendly_to_player and not enemy_starbase_id:
                enemy_starbase_id = obj_id
            elif obj.friendly_to_player and not friendly_starbase_id:
                friendly_starbase_id = obj_id
        
        if enemy_starbase_id and friendly_starbase_id:
            break
    
    if not enemy_starbase_id:
        print("ERROR: No enemy starbases found!")
        return
    
    enemy_starbase = engine.universe_objects[enemy_starbase_id]
    print(f"\nFound enemy starbase: {enemy_starbase_id}")
    print(f"Starbase position: {enemy_starbase.position}")
    print(f"Starbase damage: {enemy_starbase.damage}%")
    print(f"Starbase shields: {enemy_starbase.shields}%")
    print(f"Player position: {engine.player_ship.position}")
    
    # Test 1: Send message to enemy starbase
    print("\n" + "="*60)
    print("TEST 1: Sending threat to enemy starbase")
    print("="*60)
    command = parser.parse(f"tell {enemy_starbase_id} Your base will be destroyed!")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
    
    # Test 2: Demand surrender from starbase
    print("\n" + "="*60)
    print("TEST 2: Demanding surrender from starbase")
    print("="*60)
    command = parser.parse(f"tell {enemy_starbase_id} Surrender your base or be annihilated")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
    
    # Test 3: Try to send message to friendly starbase (should fail)
    if friendly_starbase_id:
        print("\n" + "="*60)
        print("TEST 3: Try sending message to friendly starbase (should fail)")
        print("="*60)
        command = parser.parse(f"tell {friendly_starbase_id} Hello friend")
        if command:
            print(f"Parsed command: {command}")
            engine._execute_command(engine.player_ship, command)
            print("\nMessages:")
            for msg in engine.messages:
                print(f"  {msg}")
            engine.messages.clear()
    
    # Test 4: Taunt damaged starbase
    print("\n" + "="*60)
    print("TEST 4: Taunt damaged enemy starbase")
    print("="*60)
    # Damage the starbase
    enemy_starbase.damage = 60
    enemy_starbase.shields = 30
    print(f"Starbase damage now: {enemy_starbase.damage}%")
    print(f"Starbase shields now: {enemy_starbase.shields}%")
    
    command = parser.parse(f"tell {enemy_starbase_id} Your defenses are failing!")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
    
    # Test 5: Compare ship vs starbase responses
    enemy_ship_id = list(engine.enemy_ships.keys())[0] if engine.enemy_ships else None
    if enemy_ship_id:
        print("\n" + "="*60)
        print("TEST 5: Compare ship vs starbase response to same message")
        print("="*60)
        
        test_message = "You're in my way"
        
        print(f"\nSending to enemy ship {enemy_ship_id}:")
        command = parser.parse(f"tell {enemy_ship_id} {test_message}")
        if command:
            engine._execute_command(engine.player_ship, command)
            print("\nMessages:")
            for msg in engine.messages:
                print(f"  {msg}")
            engine.messages.clear()
        
        # Reset starbase damage for fair comparison
        enemy_starbase.damage = 0
        enemy_starbase.shields = 100
        
        print(f"\nSending to enemy starbase {enemy_starbase_id}:")
        command = parser.parse(f"tell {enemy_starbase_id} {test_message}")
        if command:
            engine._execute_command(engine.player_ship, command)
            print("\nMessages:")
            for msg in engine.messages:
                print(f"  {msg}")
            engine.messages.clear()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_starbase_tell()
