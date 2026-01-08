#!/usr/bin/env python3
"""
Test script for the ask command with LLM integration.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Prevent UI from launching

import sys
from src.game_engine import GameEngine
from src.command_parser import CommandParser
from src.ship import Ship
from src.universe_objects import Position

def test_ask_command():
    """Test the ask command with various natural language questions."""
    print("=" * 60)
    print("Testing Ask Command with LLM Integration")
    print("=" * 60)
    
    # Create a game engine
    print("\n[1] Creating game engine...")
    engine = GameEngine(universe_seed=42)
    parser = CommandParser()
    print(f"    Player ship at: ({engine.player_ship.position.x:.1f}, {engine.player_ship.position.y:.1f})")
    print(f"    LLM enabled: {engine.llm_handler.enabled}")
    
    # Test questions
    test_questions = [
        "where is the nearest npc base?",
        "what is the closest hostile starbase?",
        "find me the nearest friendly base",
        "where is the closest npc ship?",
        "how many npcs are nearby?",
        "what stars are in range?"
    ]
    
    print("\n[2] Testing natural language questions:")
    print("-" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[Question {i}] {question}")
        engine.messages = []  # Clear messages
        
        # Parse and execute the command
        cmd = parser.parse(f"ask {question}")
        if cmd and cmd['command'] == 'ask':
            engine._execute_ask(engine.player_ship, cmd['question'])
            
            # Print the response
            print("Response:")
            for msg in engine.messages:
                print(f"  {msg}")
        else:
            print("  ERROR: Command parsing failed")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_ask_command()
