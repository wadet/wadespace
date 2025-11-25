"""
Wade Space Game - Universe Generator

Generates a random universe with all required objects.
"""

import random
import math
from typing import List, Dict, Optional, Tuple
from src.universe_objects import (
    Position, Star, Planet, BlackHole, Pulsar, WormHole, Starbase, AsteroidField
)
from src.identifiers import ObjectIdentifier


class SpatialGrid:
    """Grid-based spatial partitioning for efficient object placement."""
    
    def __init__(self, width: float, height: float, cell_size: float):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = int(width / cell_size) + 1
        self.grid_height = int(height / cell_size) + 1
        self.grid: Dict[Tuple[int, int], List[Position]] = {}
    
    def _get_cell(self, position: Position) -> Tuple[int, int]:
        """Get grid cell coordinates for a position."""
        x = int(position.x / self.cell_size)
        y = int(position.y / self.cell_size)
        return (max(0, min(x, self.grid_width - 1)), max(0, min(y, self.grid_height - 1)))
    
    def add(self, position: Position) -> None:
        """Add a position to the grid."""
        cell = self._get_cell(position)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(position)
    
    def get_nearby(self, position: Position, radius: float) -> List[Position]:
        """Get all positions within radius of a point."""
        cell = self._get_cell(position)
        cells_to_check = int(math.ceil(radius / self.cell_size)) + 1
        nearby = []
        
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                check_cell = (cell[0] + dx, cell[1] + dy)
                if check_cell in self.grid:
                    nearby.extend(self.grid[check_cell])
        
        return nearby


class UniverseGenerator:
    """Generates a random universe with all game objects."""
    
    UNIVERSE_WIDTH = 10000  # AU
    UNIVERSE_HEIGHT = 10000  # AU
    MIN_DISTANCE_BETWEEN_OBJECTS = 5.0  # AU
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.id_generator = ObjectIdentifier()
        self.objects: Dict[str, object] = {}
        self.spatial_grid = SpatialGrid(self.UNIVERSE_WIDTH, self.UNIVERSE_HEIGHT, 100.0)
    
    def generate(self) -> Dict[str, object]:
        """
        Generate a complete universe using improved algorithms.
        
        Returns:
            Dictionary of all universe objects keyed by ID
        """
        self.objects = {}
        self.spatial_grid = SpatialGrid(self.UNIVERSE_WIDTH, self.UNIVERSE_HEIGHT, 100.0)
        
        # Generate stars first (planets depend on them)
        stars = self._generate_stars(1000)
        self.objects.update(stars)
        
        # Generate planets around stars (reduced to fit 4-digit ID limit)
        planets = self._generate_planets(stars, 9000)
        self.objects.update(planets)
        
        # Generate black holes
        black_holes = self._generate_objects('black_hole', BlackHole, 100, min_distance=20.0)
        self.objects.update(black_holes)
        
        # Generate pulsars
        pulsars = self._generate_objects('pulsar', Pulsar, 100, min_distance=15.0)
        self.objects.update(pulsars)
        
        # Generate wormholes (paired)
        wormholes = self._generate_wormholes(20)
        self.objects.update(wormholes)
        
        # Generate starbases (100 total, 50 friendly to player)
        starbases = self._generate_starbases(100)
        self.objects.update(starbases)
        
        # Generate asteroid fields (reduced to fit 4-digit ID limit)
        asteroid_fields = self._generate_objects('asteroid_field', AsteroidField, 600, min_distance=3.0)
        self.objects.update(asteroid_fields)
        
        return self.objects
    
    def _get_random_position(self) -> Position:
        """Generate a random position in the universe using uniform distribution."""
        return Position(
            random.uniform(0, self.UNIVERSE_WIDTH),
            random.uniform(0, self.UNIVERSE_HEIGHT)
        )
    
    def _get_distributed_position(self, sector_index: int = 0, total_sectors: int = 1) -> Position:
        """Generate a position distributed across a sector of the universe."""
        sector_width = self.UNIVERSE_WIDTH / int(math.sqrt(total_sectors))
        sector_height = self.UNIVERSE_HEIGHT / int(math.sqrt(total_sectors))
        
        sector_x = (sector_index % int(math.sqrt(total_sectors))) * sector_width
        sector_y = (sector_index // int(math.sqrt(total_sectors))) * sector_height
        
        return Position(
            random.uniform(sector_x, sector_x + sector_width),
            random.uniform(sector_y, sector_y + sector_height)
        )
    
    def _is_valid_position(self, position: Position, min_distance: float = MIN_DISTANCE_BETWEEN_OBJECTS) -> bool:
        """Check if a position is far enough from all existing objects using spatial grid."""
        nearby = self.spatial_grid.get_nearby(position, min_distance)
        
        for nearby_pos in nearby:
            if position.distance_to(nearby_pos) < min_distance:
                return False
        return True
    
    def _find_valid_position(self, min_distance: float = MIN_DISTANCE_BETWEEN_OBJECTS, 
                            max_attempts: int = 100) -> Optional[Position]:
        """Find a valid position for a new object using smart sampling."""
        # Try random positions first
        for _ in range(max_attempts // 2):
            position = self._get_random_position()
            if self._is_valid_position(position, min_distance):
                self.spatial_grid.add(position)
                return position
        
        # If random fails, try grid-based search
        cell_size = int(math.sqrt((self.UNIVERSE_WIDTH * self.UNIVERSE_HEIGHT) / 1000))
        for x in range(0, int(self.UNIVERSE_WIDTH), cell_size):
            for y in range(0, int(self.UNIVERSE_HEIGHT), cell_size):
                # Try random point in this cell
                pos_x = random.uniform(x, min(x + cell_size, self.UNIVERSE_WIDTH))
                pos_y = random.uniform(y, min(y + cell_size, self.UNIVERSE_HEIGHT))
                position = Position(pos_x, pos_y)
                
                if self._is_valid_position(position, min_distance):
                    self.spatial_grid.add(position)
                    return position
        
        return None
    
    def _generate_stars(self, count: int) -> Dict[str, Star]:
        """Generate stars using sector-based distribution."""
        stars = {}
        sectors = int(math.sqrt(count / 100)) or 1  # Divide into sectors
        attempt_per_sector = count // (sectors * sectors) + 1
        
        for sector in range(sectors * sectors):
            for _ in range(attempt_per_sector):
                position = self._get_distributed_position(sector, sectors * sectors)
                
                if self._is_valid_position(position, min_distance=8.0):
                    star_id = self.id_generator.generate('star')
                    star = Star(star_id, position)
                    stars[star_id] = star
                
                if len(stars) >= count:
                    return stars
        
        return stars
    
    def _generate_planets(self, stars: Dict[str, Star], count: int) -> Dict[str, Planet]:
        """Generate planets using proper orbital mechanics."""
        planets = {}
        star_list = list(stars.values())
        planets_per_star = max(1, count // len(star_list))
        
        for star in star_list:
            for _ in range(planets_per_star):
                if len(planets) >= count:
                    return planets
                
                # Use proper orbital mechanics: polar coordinates with cos/sin
                distance = random.uniform(5, 50)  # AU from star
                angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
                
                # Proper conversion to Cartesian coordinates
                position = Position(
                    star.position.x + distance * math.cos(angle),
                    star.position.y + distance * math.sin(angle)
                )
                
                # Clamp to universe bounds
                position.x = max(0, min(self.UNIVERSE_WIDTH, position.x))
                position.y = max(0, min(self.UNIVERSE_HEIGHT, position.y))
                
                if self._is_valid_position(position, min_distance=3.0):
                    planet_id = self.id_generator.generate('planet')
                    planet = Planet(planet_id, position, star)
                    planets[planet_id] = planet
        
        return planets
    
    def _generate_objects(self, obj_type: str, obj_class, count: int, 
                         min_distance: float = MIN_DISTANCE_BETWEEN_OBJECTS) -> Dict[str, object]:
        """Generate objects of a specific type with better distribution."""
        objects = {}
        attempts = 0
        max_total_attempts = count * 50  # Prevent infinite loops
        
        while len(objects) < count and attempts < max_total_attempts:
            position = self._find_valid_position(min_distance=min_distance, max_attempts=10)
            
            if position is not None:
                obj_id = self.id_generator.generate(obj_type)
                obj = obj_class(obj_id, position)
                objects[obj_id] = obj
            
            attempts += 1
        
        return objects
    
    def _generate_wormholes(self, count: int) -> Dict[str, WormHole]:
        """Generate paired wormholes in distributed locations."""
        wormholes = {}
        attempts = 0
        max_attempts = count * 100
        
        while len(wormholes) < count * 2 and attempts < max_attempts:
            # Generate first wormhole
            position1 = self._find_valid_position(min_distance=15.0, max_attempts=10)
            if position1 is None:
                attempts += 1
                continue
            
            # Generate paired wormhole at different location (far apart)
            position2 = self._find_valid_position(min_distance=15.0, max_attempts=10)
            if position2 is None:
                attempts += 1
                continue
            
            id1 = self.id_generator.generate('worm_hole')
            id2 = self.id_generator.generate('worm_hole')
            
            wh1 = WormHole(id1, position1, pair_id=id2)
            wh2 = WormHole(id2, position2, pair_id=id1)
            
            # Link them
            wh1.pair = wh2
            wh2.pair = wh1
            
            wormholes[id1] = wh1
            wormholes[id2] = wh2
            
            attempts += 1
        
        return wormholes
    
    def _generate_starbases(self, total_count: int) -> Dict[str, Starbase]:
        """Generate starbases distributed across the universe."""
        starbases = {}
        friendly_count = total_count // 2
        enemy_count = total_count - friendly_count
        
        # Generate friendly starbases with sector distribution
        friendly_sectors = int(math.sqrt(friendly_count / 10)) or 1
        for sector in range(friendly_sectors * friendly_sectors):
            for _ in range((friendly_count // (friendly_sectors * friendly_sectors)) + 1):
                if len([s for s in starbases.values() if s.friendly_to_player]) >= friendly_count:
                    break
                
                position = self._get_distributed_position(sector, friendly_sectors * friendly_sectors)
                
                if self._is_valid_position(position, min_distance=12.0):
                    sb_id = self.id_generator.generate('starbase')
                    sb = Starbase(sb_id, position, friendly_to_player=True)
                    starbases[sb_id] = sb
        
        # Generate enemy starbases
        enemy_sectors = int(math.sqrt(enemy_count / 10)) or 1
        for sector in range(enemy_sectors * enemy_sectors):
            for _ in range((enemy_count // (enemy_sectors * enemy_sectors)) + 1):
                if len([s for s in starbases.values() if not s.friendly_to_player]) >= enemy_count:
                    break
                
                position = self._get_distributed_position(sector, enemy_sectors * enemy_sectors)
                
                if self._is_valid_position(position, min_distance=12.0):
                    sb_id = self.id_generator.generate('starbase')
                    sb = Starbase(sb_id, position, friendly_to_player=False)
                    starbases[sb_id] = sb
        
        return starbases
