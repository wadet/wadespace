"""
Wade Space Game - Basic Unit Tests
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.identifiers import ObjectIdentifier
from src.universe_objects import Position, Star, Planet, BlackHole
from src.ship import Ship
from src.command_parser import CommandParser
from src.universe import UniverseGenerator
from src.game_engine import GameEngine


class TestIdentifiers:
    """Test unique identifier generation."""
    
    def test_generate_star_id(self):
        """Test generating star identifier."""
        id_gen = ObjectIdentifier()
        star_id = id_gen.generate('star')
        assert star_id.startswith('st')
        assert len(star_id) >= 4  # 'st' + at least 1 digit
    
    def test_generate_ship_id(self):
        """Test generating ship identifier."""
        id_gen = ObjectIdentifier()
        ship_id = id_gen.generate('ship')
        assert ship_id.startswith('s')
    
    def test_unique_ids(self):
        """Test that generated IDs are unique."""
        id_gen = ObjectIdentifier()
        ids = set()
        for _ in range(100):
            star_id = id_gen.generate('star')
            assert star_id not in ids
            ids.add(star_id)


class TestPosition:
    """Test position calculations."""
    
    def test_distance(self):
        """Test distance calculation."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        assert pos1.distance_to(pos2) == 5.0
    
    def test_self_distance(self):
        """Test distance to self."""
        pos = Position(10, 20)
        assert pos.distance_to(pos) == 0.0


class TestUniverseObjects:
    """Test universe object creation."""
    
    def test_star_creation(self):
        """Test creating a star."""
        star = Star('st1', Position(100, 200))
        assert star.id == 'st1'
        assert star.position.x == 100
        assert star.position.y == 200
        assert star.get_display_symbol() == "★"
    
    def test_planet_creation(self):
        """Test creating a planet."""
        star = Star('st1', Position(100, 200))
        planet = Planet('pl1', Position(150, 250), star)
        assert planet.id == 'pl1'
        assert planet.parent_star == star


class TestShip:
    """Test ship mechanics."""
    
    def test_ship_creation(self):
        """Test creating a ship."""
        ship = Ship('s1', Position(100, 100), is_player=True)
        assert ship.id == 's1'
        assert ship.energy == 100.0
        assert ship.shields == 100.0
        assert ship.damage == 0.0
        assert ship.crew == 1000
    
    def test_shield_activation(self):
        """Test shield activation."""
        ship = Ship('s1', Position(100, 100))
        assert not ship.shields_active
        ship.update_shields(True)
        assert ship.shields_active
    
    def test_energy_drain_shields(self):
        """Test energy drain from shields."""
        ship = Ship('s1', Position(100, 100))
        ship.update_shields(True)
        initial_energy = ship.energy
        ship.update_energy()
        assert ship.energy < initial_energy
    
    def test_warp_speed_setting(self):
        """Test setting warp speed."""
        ship = Ship('s1', Position(100, 100))
        assert ship.set_warp_speed(5.0)
        assert ship.propulsion.current_speed == 5.0
        assert ship.propulsion.warp_active
    
    def test_invalid_warp_speed(self):
        """Test invalid warp speeds are rejected."""
        ship = Ship('s1', Position(100, 100))
        assert not ship.set_warp_speed(1.0)  # Too slow
        assert not ship.set_warp_speed(25.0)  # Too fast
    
    def test_damage_repair(self):
        """Test damage repair."""
        ship = Ship('s1', Position(100, 100))
        ship.damage = 50.0
        ship.update_damage_repair()
        assert ship.damage == 45.0


class TestCommandParser:
    """Test natural language command parsing."""
    
    def test_warp_command(self):
        """Test parsing warp command."""
        parser = CommandParser()
        cmd = parser.parse("warp 8")
        assert cmd['command'] == 'warp'
        assert cmd['speed'] == 8
    
    def test_heading_command(self):
        """Test parsing heading command."""
        parser = CommandParser()
        cmd = parser.parse("heading 180")
        assert cmd['command'] == 'heading'
        assert cmd['degrees'] == 180.0
    
    def test_shields_up_command(self):
        """Test parsing shields up."""
        parser = CommandParser()
        cmd = parser.parse("shields up")
        assert cmd['command'] == 'shields'
        assert cmd['active']
    
    def test_shields_down_command(self):
        """Test parsing shields down."""
        parser = CommandParser()
        cmd = parser.parse("shields down")
        assert cmd['command'] == 'shields'
        assert not cmd['active']
    
    def test_scan_command(self):
        """Test parsing scan command."""
        parser = CommandParser()
        cmd = parser.parse("scan st12345")
        assert cmd['command'] == 'scan'
        assert cmd['target_id'] == 'st12345'
    
    def test_fire_command(self):
        """Test parsing fire command."""
        parser = CommandParser()
        cmd = parser.parse("fire")
        assert cmd['command'] == 'fire'
    
    def test_torpedo_command(self):
        """Test parsing torpedo command."""
        parser = CommandParser()
        cmd = parser.parse("torpedo s1")
        assert cmd['command'] == 'torpedo'
        assert cmd['target_id'] == 's1'


class TestUniverseGenerator:
    """Test universe generation."""
    
    def test_generate_universe(self):
        """Test generating a universe."""
        generator = UniverseGenerator(seed=42)
        universe = generator.generate()
        
        # Count objects by type
        stars = [obj for obj in universe.values() if isinstance(obj, Star)]
        assert len(stars) == 1000
    
    def test_reproducible_generation(self):
        """Test that same seed produces same universe."""
        gen1 = UniverseGenerator(seed=42)
        uni1 = gen1.generate()
        
        gen2 = UniverseGenerator(seed=42)
        uni2 = gen2.generate()
        
        # Both should have same number of objects
        assert len(uni1) == len(uni2)


class TestGameEngine:
    """Test game engine."""
    
    def test_engine_initialization(self):
        """Test initializing the game engine."""
        engine = GameEngine(universe_seed=42)
        assert engine.player_ship is not None
        assert engine.turn_count == 0
        assert len(engine.universe_objects) > 0
    
    def test_turn_processing(self):
        """Test processing a game turn."""
        engine = GameEngine(universe_seed=42)
        initial_turn = engine.turn_count
        engine.process_turn()
        assert engine.turn_count == initial_turn + 1
    
    def test_get_objects_in_range(self):
        """Test getting objects in range."""
        engine = GameEngine(universe_seed=42)
        pos = engine.player_ship.position
        nearby = engine.get_objects_in_range(pos, 50.0)
        assert len(nearby) > 0
    
    def test_npc_ship_creation(self):
        """Test npc ships are created."""
        engine = GameEngine()
        assert len(engine.npc_ships) == 50


class TestCombat:
    """Test combat mechanics."""
    
    def test_shield_damage(self):
        """Test shield damage calculation."""
        ship = Ship('s1', Position(100, 100))
        ship.shields_active = True
        initial_shields = ship.shields
        ship.take_shield_hit(10.0)
        assert ship.shields < initial_shields
    
    def test_hull_damage_no_shields(self):
        """Test hull takes damage when shields down."""
        ship = Ship('s1', Position(100, 100))
        ship.shields = 0.0
        initial_damage = ship.damage
        ship.take_damage(10.0)
        assert ship.damage > initial_damage
    
    def test_ship_destruction(self):
        """Test ship destruction at 100% damage."""
        ship = Ship('s1', Position(100, 100))
        ship.damage = 100.0
        ship.take_damage(1.0)
        assert ship.is_destroyed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
