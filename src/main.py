"""
Wade Space Game - Main Entry Point

Initializes and runs the game.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.game_engine import GameEngine
from src.command_parser import CommandParser


def main():
    """Main game loop."""
    print("=" * 60)
    print("WADE SPACE - A 2D Turn-Based Space Game")
    print("=" * 60)
    print()
    
    # Initialize game
    engine = GameEngine()
    parser = CommandParser()
    
    print(f"Your ship: {engine.player_ship.id}")
    print(f"Starting position: {engine.player_ship.position}")
    print()
    print("Commands: warp, impulse, heading, shields, scan, fire, torpedo,")
    print("          status, stop, nav, ask, tell, skip")
    print()
    
    # Main game loop
    while not engine.game_over:
        try:
            print(f"\n--- Turn {engine.turn_count + 1} ---")
            print(f"Position: ({engine.player_ship.position.x:.1f}, {engine.player_ship.position.y:.1f})")
            print(f"Energy: {engine.player_ship.energy:.1f}%  Shields: {engine.player_ship.shields:.1f}%")
            print(f"Damage: {engine.player_ship.damage:.1f}%  Crew: {engine.player_ship.crew}")
            print()
            
            # Get player command
            user_input = input("Enter command: ").strip()
            
            if not user_input:
                # If empty, show status
                command = {'command': 'status'}
            else:
                command = parser.parse(user_input)
                if command is None:
                    print("Invalid command. Try again.")
                    continue
            
            # Process turn
            engine.process_turn(player_command=command)
            
            # Display messages
            for msg in engine.messages:
                print(msg)
        
        except KeyboardInterrupt:
            print("\nGame interrupted.")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            break
    
    # Game over
    print("\n" + "=" * 60)
    print("GAME OVER")
    print(engine.game_over_reason)
    print("=" * 60)


if __name__ == '__main__':
    main()
