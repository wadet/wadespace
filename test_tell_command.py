#!/usr/bin/env python3
"""
Test script for the tell command with LLM-generated npc responses.
"""

from src.game_engine import GameEngine
from src.command_parser import CommandParser

def test_tell_command():
    """Test the tell command functionality."""
    print("Initializing game engine...")
    engine = GameEngine(universe_seed=42)
    parser = CommandParser()
    
    # Get the first npc ship ID
    if not engine.npc_ships:
        print("ERROR: No npc ships found!")
        return
    
    npc_id = list(engine.npc_ships.keys())[0]
    print(f"\nFound npc ship: {npc_id}")
    print(f"NPC position: {engine.npc_ships[npc_id].position}")
    print(f"Player position: {engine.player_ship.position}")
    
    # Test 1: Valid tell command
    print("\n" + "="*60)
    print("TEST 1: Sending message to npc ship")
    print("="*60)
    command = parser.parse(f"tell {npc_id} Prepare to be destroyed!")
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
    command = parser.parse(f"tell {npc_id} Surrender now and I'll let you live")
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
    
    # Test 4: Message after damaging the npc
    print("\n" + "="*60)
    print("TEST 4: Taunt after damaging npc ship")
    print("="*60)
    # Damage the npc ship
    npc_ship = engine.npc_ships[npc_id]
    npc_ship.damage += 50  # Add 50% damage
    print(f"NPC ship damage: {npc_ship.damage:.1f}%")
    
    command = parser.parse(f"tell {npc_id} How do you like that?")
    if command:
        print(f"Parsed command: {command}")
        engine._execute_command(engine.player_ship, command)
        print("\nMessages:")
        for msg in engine.messages:
            print(f"  {msg}")
        engine.messages.clear()
        # Test 5: Message when npc is nearly destroyed
    print("\n" + "="*60)
    print("TEST 5: Taunt when npc is critically damaged")
    print("="*60)
    # Damage the npc ship more
    npc_ship.damage = 85  # Set to 85% damage
    print(f"NPC ship damage: {npc_ship.damage:.1f}%")
    
    command = parser.parse(f"tell {npc_id} Ready to surrender yet?")
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
