#!/usr/bin/env python3
"""Debug torpedo hitting starbase."""

from src.game_engine import GameEngine
from src.ship import Position
from src.universe_objects import Starbase

game = GameEngine()
game.player_ship.position = Position(100.0, 100.0)
game.player_ship.torpedos = 50

# Create a hostile starbase
starbase = Starbase("sb1", Position(102.0, 100.0))
starbase.shields = 100.0
starbase.shields_active = True
starbase.damage = 0.0
starbase.stances[game.player_ship.id] = 'hostile'
game.universe_objects["sb1"] = starbase

print(f"Before torpedo:")
print(f"  Starbase position: ({starbase.position.x}, {starbase.position.y})")
print(f"  Starbase shields: {starbase.shields:.2f}%")
print(f"  Starbase damage: {starbase.damage:.2f}%")
print(f"  Starbase is Starbase: {isinstance(starbase, Starbase)}")

# Fire torpedo
print(f"\nPlayer ship status before firing:")
print(f"  Can fire: {game.player_ship.can_fire_weapons()}")
print(f"  Torpedo operational: {game.player_ship.weapons.torpedo_operational}")
print(f"  Torpedos available: {game.player_ship.weapons.torpedos}")
print(f"  Energy: {game.player_ship.energy:.2f}")

game._execute_torpedo(game.player_ship, "sb1")
print(f"\nAfter execute_torpedo:")
print(f"  Active torpedos: {len(game.player_ship.weapons.active_torpedos)}")

if game.player_ship.weapons.active_torpedos:
    torpedo = game.player_ship.weapons.active_torpedos[0]
    print(f"  Torpedo current pos: ({torpedo['current_pos'].x}, {torpedo['current_pos'].y})")
    print(f"  Torpedo target pos: ({torpedo['target_pos'].x}, {torpedo['target_pos'].y})")
    
    # Move torpedo to just before starbase
    torpedo['current_pos'] = Position(starbase.position.x - 1.5, starbase.position.y)
    print(f"\nManually moved torpedo to ({torpedo['current_pos'].x}, {torpedo['current_pos'].y})")
    print(f"  Distance to starbase: {starbase.position.distance_to(torpedo['current_pos']):.2f} AU")
    
    # Process torpedo movement - should hit
    print("\nProcessing torpedo movement...")
    game._update_torpedos()
    
    print(f"\nAfter processing:")
    print(f"  Active torpedos remaining: {len(game.player_ship.weapons.active_torpedos)}")
    print(f"  Starbase shields: {starbase.shields:.2f}%")
    print(f"  Starbase damage: {starbase.damage:.2f}%")
    print(f"  Messages: {game.messages}")
