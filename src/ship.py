"""
Wade Space Game - Ship Systems

Core ship implementation with all onboard systems.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
import random
from src.universe_objects import Position


@dataclass
class ShipWeaponSystem:
    """Manages ship weapons."""
    phaser_operational: bool = True
    phaser_charge: float = 100.0  # 0-100%
    phaser_locked_target: Optional[str] = None
    phaser_range: float = 10.0  # AU
    phaser_recharge_rate: float = 25.0  # % per turn
    phaser_damage: float = 5.0  # % per hit
    phaser_can_fire_this_turn: bool = True
    
    torpedo_operational: bool = True
    torpedos: int = 50
    max_torpedos: int = 50
    torpedo_range: float = 20.0  # AU
    torpedo_speed: float = 1.0  # AU per turn
    torpedo_damage: float = 10.0  # % per hit
    active_torpedos: List[dict] = field(default_factory=list)  # {id, start_pos, current_pos, target_pos, fired_turn}


@dataclass
class ShipPropulsionSystem:
    """Manages ship propulsion."""
    impulse_active: bool = False
    warp_active: bool = False
    current_speed: float = 0.0  # AU per turn
    current_heading: float = 0.0  # 0-359 degrees
    
    warp_core_temp: float = 0.0  # 0-100%
    warp_core_max_temp: float = 100.0
    
    impulse_energy_cost: float = 1.0  # % per turn
    warp_energy_cost: float = 0.5  # % per turn


@dataclass
class ShipSensorSystem:
    """Manages ship sensors."""
    operational: bool = True
    sensor_range: float = 50.0  # AU
    scan_range_detailed: float = 20.0  # AU for detailed scans
    disrupted: bool = False


class Ship:
    """Represents a starship with all onboard systems."""
    
    def __init__(self, ship_id: str, position: Position, is_player: bool = False):
        self.id = ship_id
        self.position = position
        self.is_player = is_player
        
        # Vital statistics
        self.damage = 0.0  # 0-100%
        self.energy = 100.0  # 0-100%
        self.shields = 100.0  # 0-100%
        self.shields_active = False
        self.crew = 1000
        self.cash = random.randint(1000, 5000)
        self.reputation = random.randint(0, 100)  # 0-100, randomly assigned
        
        # Behavior trait for enemy ships (aggressive, neutral, timid)
        self.behavior_trait = None  # Only assigned for enemy ships
        
        # Systems
        self.weapons = ShipWeaponSystem()
        self.propulsion = ShipPropulsionSystem()
        self.sensors = ShipSensorSystem()
        
        # Movement tracking
        self.last_position = position
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Navigation
        self.auto_nav_target_id: Optional[str] = None
        self.is_docked_with: Optional[str] = None
        self.is_destroyed = False
        self.is_disabled = False
        
        # Game statistics (for player ships only)
        self.stats = {
            'enemies_destroyed': 0,
            'phasers_fired': 0,
            'torpedos_fired': 0,
            'torpedo_hits': 0,
        }
    
    def can_move(self) -> bool:
        """Check if ship can move."""
        return self.energy > 0 and self.crew > 0 and not self.is_destroyed
    
    def can_fire_weapons(self) -> bool:
        """Check if ship can fire weapons."""
        return self.energy > 0 and self.crew > 0 and not self.is_destroyed
    
    def update_shields(self, active: bool) -> None:
        """Activate or deactivate shields."""
        self.shields_active = active
    
    def update_energy(self) -> None:
        """Update energy based on active systems."""
        energy_drain = 0.0
        
        # Shield drain
        if self.shields_active:
            energy_drain += 2.0
        
        # Propulsion drain
        if self.propulsion.warp_active:
            energy_drain += self.propulsion.warp_energy_cost
            # Calculate additional drain for speeds over 9 AU/turn
            if self.propulsion.current_speed > 9.0:
                excess_speed = self.propulsion.current_speed - 9.0
                self.propulsion.warp_core_temp += excess_speed
        elif self.propulsion.impulse_active:
            energy_drain += self.propulsion.impulse_energy_cost
        
        self.energy = max(0.0, self.energy - energy_drain)
    
    def update_damage_repair(self) -> None:
        """Repair damage each turn, with different rates for stationary vs moving ships.
        
        Stationary ships: Maximum repair is 5% per turn with full crew.
        Repair scales proportionally with crew percentage.
        For example: 50% crew = 2.5% repair per turn.
        
        Moving ships: Auto repair 1% per turn regardless of crew.
        """
        if self.propulsion.current_speed == 0.0:
            # Stationary: repair up to 5% scaled by crew percentage
            crew_percentage = self.crew / 1000.0  # Returns 0.0 to 1.0
            max_repair = 5.0 * crew_percentage
            self.damage = max(0.0, self.damage - max_repair)
        else:
            # Moving: auto repair 1% per turn
            self.damage = max(0.0, self.damage - 1.0)
    
    def update_warp_core(self) -> None:
        """Update warp core temperature."""
        if not self.propulsion.warp_active:
            # Cool down 5% per turn when warp inactive
            self.propulsion.warp_core_temp = max(0.0, self.propulsion.warp_core_temp - 5.0)
        
        if not self.propulsion.impulse_active:
            # Cool down 10% per turn when impulse inactive
            self.propulsion.warp_core_temp = max(0.0, self.propulsion.warp_core_temp - 10.0)
        
        # Cap at max
        self.propulsion.warp_core_temp = min(
            self.propulsion.warp_core_max_temp,
            self.propulsion.warp_core_temp
        )
    
    def update_phaser_charge(self) -> None:
        """Recharge phasers."""
        if self.weapons.phaser_operational and not self.weapons.phaser_can_fire_this_turn:
            self.weapons.phaser_charge = min(
                100.0,
                self.weapons.phaser_charge + self.weapons.phaser_recharge_rate
            )
        self.weapons.phaser_can_fire_this_turn = False
    
    def take_damage(self, damage: float, bypass_shields: bool = False) -> None:
        """Apply damage to the ship."""
        if bypass_shields or self.shields <= 0:
            # Direct ship damage
            self.damage += damage
        else:
            # Damage shields first
            shield_damage = min(damage, self.shields)
            self.shields -= shield_damage
            remaining_damage = damage - shield_damage
            if remaining_damage > 0:
                self.damage += remaining_damage
        
        # Check if destroyed
        if self.damage >= 100.0:
            self.is_destroyed = True
    
    def take_shield_hit(self, damage: float = 5.0) -> None:
        """Take a phaser hit to shields."""
        if self.shields_active:
            self.shields = max(0.0, self.shields - damage)
        else:
            # Direct ship damage
            self.damage += damage
        
        # Check if destroyed
        if self.damage >= 100.0:
            self.is_destroyed = True
    
    def fire_phaser(self, target_ship: 'Ship') -> dict:
        """
        Attempt to fire phasers at a target.
        
        Returns:
            dict with keys: 'hit' (bool), 'damage' (float), 'target_id' (str), 'damage_type' (str)
            or empty dict if fire failed
        """
        if not self.can_fire_weapons():
            return {}
        
        if not self.weapons.phaser_operational:
            return {}
        
        if self.weapons.phaser_locked_target != target_ship.id:
            return {}
        
        distance = self.position.distance_to(target_ship.position)
        if distance > self.weapons.phaser_range:
            return {}
        
        # Track phaser fire for player ship
        if self.is_player:
            self.stats['phasers_fired'] += 1
        
        # Determine if hit (50-100% accuracy)
        hit_chance = random.uniform(0.5, 1.0)
        
        # Hit calculation with 1% warp core hit chance
        is_warp_core_hit = random.random() < 0.01
        
        damage_type = 'shield'  # Default to shield damage
        if is_warp_core_hit and target_ship.propulsion.warp_core_temp < 100:
            target_ship.propulsion.warp_core_temp += 10.0
            damage = 0  # Warp core hit doesn't cause normal damage
            damage_type = 'warp core'
        else:
            damage = self.weapons.phaser_damage
        
        # Record shield status before damage
        shields_before = target_ship.shields
        target_ship.take_shield_hit(damage)
        shields_after = target_ship.shields
        
        # Determine actual damage type applied
        if shields_before > shields_after:
            damage_type = 'shield'
            actual_damage = shields_before - shields_after
        else:
            # Shields were down, damage went to ship
            damage_type = 'ship'
            actual_damage = damage
        
        self.weapons.phaser_can_fire_this_turn = True
        self.energy -= 1.0  # Energy to fire
        
        return {
            'hit': True,
            'damage': actual_damage,
            'target_id': target_ship.id,
            'damage_type': damage_type,
            'weapon': 'phaser'
        }
    
    def fire_torpedo(self, target_position: Position, target_ship: Optional['Ship'] = None) -> dict:
        """
        Fire a torpedo toward a target position.
        
        Args:
            target_position: Target coordinates
            target_ship: Optional reference to target ship for tracking
        
        Returns:
            dict with 'fired' (bool) and 'weapon' (str) on success
            or empty dict if fire failed
        """
        if not self.can_fire_weapons():
            return {}
        
        if not self.weapons.torpedo_operational:
            return {}
        
        if self.weapons.torpedos <= 0:
            return {}
        
        if self.energy < 1.0:
            return {}
        
        # Track torpedo fire for player ship
        if self.is_player:
            self.stats['torpedos_fired'] += 1
        
        # Create torpedo
        torpedo_id = f"torp_{len(self.weapons.active_torpedos)}"
        torpedo = {
            'id': torpedo_id,
            'start_pos': self.position,
            'current_pos': self.position,
            'target_pos': target_position,
            'fired_turn': 0,
            'distance_traveled': 0.0,
            'source_ship_id': self.id
        }
        
        self.weapons.active_torpedos.append(torpedo)
        self.weapons.torpedos -= 1
        self.energy -= 1.0
        
        return {
            'fired': True,
            'weapon': 'torpedo',
            'target_id': target_ship.id if target_ship else 'unknown'
        }
    
    def lock_phasers(self, target_id: str) -> None:
        """Lock phasers on a target."""
        self.weapons.phaser_locked_target = target_id
    
    def unlock_phasers(self) -> None:
        """Unlock phasers."""
        self.weapons.phaser_locked_target = None
    
    def set_warp_speed(self, speed: float) -> bool:
        """
        Set warp speed (2-9 AU/turn, can exceed with core heat buildup).
        
        Returns:
            True if speed set successfully
        """
        if speed < 2.0 or speed > 20.0:
            return False
        
        if self.propulsion.warp_core_temp >= 100.0:
            return False
        
        self.propulsion.current_speed = speed
        self.propulsion.warp_active = True
        self.propulsion.impulse_active = False
        
        return True
    
    def set_heading(self, heading: float) -> None:
        """Set ship heading (0-359 degrees)."""
        heading = heading % 360.0
        self.propulsion.current_heading = heading
    
    def move(self) -> None:
        """Move ship based on current velocity."""
        if not self.can_move():
            return
        
        import math
        heading_rad = math.radians(self.propulsion.current_heading)
        
        # Calculate velocity
        distance = self.propulsion.current_speed
        self.position.x += distance * math.cos(heading_rad)
        self.position.y += distance * math.sin(heading_rad)
        
        # Clamp to universe bounds
        self.position.x = max(0, min(10000, self.position.x))
        self.position.y = max(0, min(10000, self.position.y))
    
    def stop(self) -> None:
        """Stop the ship."""
        self.propulsion.current_speed = 0.0
        self.propulsion.warp_active = False
        self.propulsion.impulse_active = False
    
    def get_status_dict(self) -> dict:
        """Return ship status as dictionary."""
        return {
            'id': self.id,
            'position': (self.position.x, self.position.y),
            'damage': self.damage,
            'energy': self.energy,
            'shields': self.shields,
            'crew': self.crew,
            'cash': self.cash,
            'torpedos': self.weapons.torpedos,
            'phaser_charge': self.weapons.phaser_charge,
            'warp_core_temp': self.propulsion.warp_core_temp,
            'shields_active': self.shields_active,
            'is_destroyed': self.is_destroyed,
            'is_disabled': self.is_disabled,
        }
