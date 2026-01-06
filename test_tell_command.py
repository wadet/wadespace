#!/usr/bin/env python3
"""
Test script for the tell command with LLM-generated enemy responses.
"""

from src.game_engine import GameEngine
from src.command_parser import CommandParser

def test_tell_command():
    """Test the tell command functionality."""
    print("Initializing game engine...")
    engine = GameEngine(universe_seed=42)
    parser = CommandParser()
    
    # Get the first enemy ship ID
    if not engine.enemy_ships:
        print("ERROR: No enemy ships found!")
        return
    
    enemy_id = list(engine.enemy_ships.keys())[0]
    print(f"\nFound enemy ship: {enemy_id}")
    print(f"Enemy position: {engine.enemy_ships[enemy_id].position}")
    print(f"Player position: {engine.player_ship.position}")
    
    # Test 1: Valid tell command
    print("\n" + "="*60)
    print("TEST 1: Sending message to enemy ship")
    print("="*60)
    command = parser.parse(f"tell {enemy_id} Prepare to be destroyed!")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
    
    # Test 2: Another message with different tone
    print("\n" + "="*60)
    print("TEST 2: Sending another message")
    print("="*60)
    command = parser.parse(f"tell {enemy_id} Surrender now and I'll let you live")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
    
    # Test 3: Invalid target
    print("\n" + "="*60)
    print("TEST 3: Sending message to invalid target")
    print("="*60)
    command = parser.parse("tell st1234 Hello star")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
    
    # Test 4: Message after damaging the enemy
    print("\n" + "="*60)
    print("TEST 4: Taunt after damaging enemy ship")
    print("="*60)
    # Damage the enemy ship
    enemy_ship = engine.enemy_ships[enemy_id]
    enemy_ship.damage += 50  # Add 50% damage
    print(f"Enemy ship damage: {enemy_ship.damage:.1f}%")
    
    command = parser.parse(f"tell {enemy_id} How do you like that?")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
        # Test 5: Message when enemy is nearly destroyed
    print("\n" + "="*60)
    print("TEST 5: Taunt when enemy is critically damaged")
    print("="*60)
    # Damage the enemy ship more
    enemy_ship.damage = 85  # Set to 85% damage
    print(f"Enemy ship damage: {enemy_ship.damage:.1f}%")
    
    command = parser.parse(f"tell {enemy_id} Ready to surrender yet?")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
        print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_tell_command()
