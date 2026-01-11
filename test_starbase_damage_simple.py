#!/usr/bin/env python3
"""
Simple direct test of starbase damage.
"""

from src.game_engine import GameEngine
from src.ship import Ship, Position
from src.universe_objects import Starbase

def test_direct_phaser():
    """Direct test of phaser damage."""
    print("\n" + "="*70)
    print("DIRECT PHASER TEST")
    print("="*70)
    
    game = GameEngine()
    
    # Position ship close to starbase
    game.player_ship.position = Position(100.0, 100.0)
    game.player_ship.energy = 100.0
    game.player_ship.crew = 1000
    
    # Create starbase
    starbase = Starbase("sb001", Position(105.0, 100.0))  # 5 AU away, within phaser range of 10 AU
    starbase.shields = 100.0
    starbase.shields_active = True
    starbase.damage = 0.0
    starbase.stances[game.player_ship.id] = 'hostile'
    game.universe_objects["sb001"] = starbase
    
    print(f"\nInitial state:")
    print(f"  Player position: ({game.player_ship.position.x}, {game.player_ship.position.y})")
    print(f"  Player energy: {game.player_ship.energy}%")
    print(f"  Player can fire: {game.player_ship.can_fire_weapons()}")
    print(f"  Starbase position: ({starbase.position.x}, {starbase.position.y})")
    print(f"  Distance: {game.player_ship.position.distance_to(starbase.position):.2f} AU")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    
    # Lock phasers
    game.player_ship.weapons.phaser_locked_target = "sb001"
    print(f"\n  Locked target: {game.player_ship.weapons.phaser_locked_target}")
    print(f"  Universe objects: {list(game.universe_objects.keys())}")
    print(f"  'sb001' in universe_objects: {'sb001' in game.universe_objects}")
    # Check the actual object
    obj = game.universe_objects.get("sb001")
    print(f"  Object type: {type(obj)}")
    print(f"  Is Starbase (using test's Starbase): {isinstance(obj, Starbase)}")
    
    # Let's also check if it's an instance of the game_engine's Starbase
    from src.universe_objects import Starbase as GameEngineStarbase
    print(f"  Is Starbase (using game_engine's Starbase): {isinstance(obj, GameEngineStarbase)}")
    print(f"  test's Starbase class: {Starbase}")
    print(f"  game_engine's Starbase class: {GameEngineStarbase}")
    
    # Fire
    print(f"\n Calling _execute_fire...")
    game._execute_fire(game.player_ship)
    
    print(f"\nAfter firing:")
    print(f"  Messages: {game.messages}")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Shield damage taken: {100.0 - starbase.shields:.2f}%")
    
    expected = 5.0 * 0.25
    actual = 100.0 - starbase.shields
    print(f"\nExpected: {expected:.2f}%")
    print(f"Actual: {actual:.2f}%")
    
    if abs(actual - expected) < 0.01:
        print("✓ PASS")
    else:
        print("✗ FAIL")


if __name__ == "__main__":
    test_direct_phaser()
