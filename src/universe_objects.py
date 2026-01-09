"""
Wade Space Game - Universe Objects

Base classes and implementations for all objects in the universe.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import random
from abc import ABC, abstractmethod


@dataclass
class Position:
    """Represents a 2D position in the universe."""
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def __repr__(self) -> str:
        return f"Position({self.x:.1f}, {self.y:.1f})"


class UniverseObject(ABC):
    """Base class for all objects in the universe."""
    
    def __init__(self, obj_id: str, position: Position, energy: float = 100.0):
        self.id = obj_id
        self.position = position
        self.energy = energy
        self.max_energy = 100.0
    
    @abstractmethod
    def update(self) -> None:
        """Update object state each turn."""
        pass
    
    @abstractmethod
    def get_display_symbol(self) -> str:
        """Return ASCII symbol for map display."""
        pass
    
    def distance_to(self, other: 'UniverseObject') -> float:
        """Calculate distance to another object."""
        return self.position.distance_to(other.position)


class Star(UniverseObject):
    """A star that provides energy to ships."""
    
    def __init__(self, obj_id: str, position: Position):
        super().__init__(obj_id, position, energy=100.0)
        self.max_energy = float('inf')  # Stars have infinite energy
    
    def update(self) -> None:
        """Stars don't change."""
        pass
    
    def get_display_symbol(self) -> str:
        return "★"


class Planet(UniverseObject):
    """A planet that may be inhabited."""
    
    def __init__(self, obj_id: str, position: Position, parent_star: 'Star'):
        super().__init__(obj_id, position)
        self.parent_star = parent_star
        self.is_inhabited = random.choice([True, False])
        self.crew_available = random.randint(0, 1000) if self.is_inhabited else 0
    
    def update(self) -> None:
        """Planets don't change."""
        pass
    
    def get_display_symbol(self) -> str:
        return "●" if self.is_inhabited else "○"


class BlackHole(UniverseObject):
    """A black hole that destroys ships within range."""
    
    def __init__(self, obj_id: str, position: Position):
        super().__init__(obj_id, position)
        self.destruction_range = 3.0  # AU
    
    def update(self) -> None:
        """Black holes don't change."""
        pass
    
    def get_display_symbol(self) -> str:
        return "⊗"


class Pulsar(UniverseObject):
    """A pulsar that disrupts sensors."""
    
    def __init__(self, obj_id: str, position: Position):
        super().__init__(obj_id, position)
        self.disruption_range = 2.0  # AU
        self.pulse_period = random.randint(5, 15)
        self.pulse_counter = 0
    
    def update(self) -> None:
        """Update pulsar state."""
        self.pulse_counter = (self.pulse_counter + 1) % self.pulse_period
    
    def get_display_symbol(self) -> str:
        return "◇"


class WormHole(UniverseObject):
    """A wormhole that teleports ships to a paired wormhole."""
    
    def __init__(self, obj_id: str, position: Position, pair_id: Optional[str] = None):
        super().__init__(obj_id, position)
        self.pair_id = pair_id
        self.pair = None  # Reference to paired wormhole, set later
        self.entry_range = 1.0  # AU
    
    def update(self) -> None:
        """Wormholes don't change."""
        pass
    
    def get_display_symbol(self) -> str:
        return "◎"


class Starbase(UniverseObject):
    """A starbase that provides repairs, refueling, and supplies."""
    
    def __init__(self, obj_id: str, position: Position, friendly_to_player: bool = True):
        super().__init__(obj_id, position, energy=100.0)
        self.friendly_to_player = friendly_to_player
        self.shields = 100.0
        self.damage = 0.0
        self.max_torpedos = 500
        self.torpedos = 500
        self.service_range = 1.0  # AU
        self.defense_range = 10.0  # AU
        
        # Stance tracking: tracks stance toward ships
        # Keys are ship IDs, values are 'hostile', 'neutral', or 'friendly'
        self.stances: Dict[str, str] = {}
    
    def update(self) -> None:
        """Update starbase state - regenerate energy."""
        if self.energy < 100.0:
            self.energy = min(100.0, self.energy + 1.0)
    
    def get_display_symbol(self) -> str:
        return "⊕"  # Green (friendly) or red (npc) in actual UI


class AsteroidField(UniverseObject):
    """An asteroid field where ships can mine for dollars."""
    
    def __init__(self, obj_id: str, position: Position):
        super().__init__(obj_id, position)
        self.asteroids = random.randint(5, 20)
        self.cluster_radius = 2.5  # Can occupy 5x5 AU
        # Generate individual asteroid positions relative to field center
        self.asteroid_positions = [
            (random.uniform(-self.cluster_radius, self.cluster_radius),
             random.uniform(-self.cluster_radius, self.cluster_radius))
            for _ in range(self.asteroids)
        ]
    
    def update(self) -> None:
        """Asteroids don't change."""
        pass
    
    def get_display_symbol(self) -> str:
        return "✕"
    
    def get_asteroid_count(self) -> int:
        """Return number of asteroids in field."""
        return len(self.asteroid_positions)
