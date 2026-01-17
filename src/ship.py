"""
Wade Space Game - Ship Systems

Core ship implementation with all onboard systems.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict
import random
from src.universe_objects import Position


@dataclass
class ShipWeaponSystem:
    """Manages ship weapons."""
    phaser_operational: bool = True
    phaser_charge: float = 100.0  # 0-100%
    phaser_locked_target: Optional[str] = None
    phaser_range: float = 5.0  # AU
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
    # Warp energy cost is now calculated dynamically based on speed
    max_normal_warp: float = 9.0  # AU per turn


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
        # Player starts with reputation 70-100, enemies get 0-100
        self.reputation = random.randint(70, 100) if is_player else random.randint(0, 100)
        
        # Behavior trait for npc ships (aggressive, neutral, timid)
        self.behavior_trait = None  # Only assigned for npc ships
        
        # Track ships that have fired upon this ship (for return fire logic)
        self.fired_upon_by = set()  # Set of ship IDs that have fired upon this ship
        
        # Stance tracking: For NPC ships and starbases - tracks stance toward other ships
        # Keys are ship/starbase IDs, values are 'hostile', 'neutral', or 'friendly'
        # Only used for NPC ships (not player ship)
        self.stances: Dict[str, str] = {} if not is_player else {}
        
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
        self.auto_nav_warp_speed: Optional[float] = None  # Custom warp speed for auto-nav
        self.is_docked_with: Optional[str] = None
        self.is_destroyed = False
        self.is_disabled = False
        
        # Docking tracking
        self.docked_at: Optional[str] = None  # ID of starbase/planet ship is docked at
        self.turns_since_last_dock: int = 999  # Track turns since last dock (start high to allow immediate docking)
        self.crew_received_this_dock: bool = False  # Track if crew was received during current dock
        
        # Repair tracking
        self.manual_repair_this_turn = False  # Track if manual repair was used this turn
        
        # System damage tracking
        # Set of disabled systems: 'shields', 'engines', 'torpedoes', 'phasers', 'scanners', 'radios', 'computers'
        self.disabled_systems = set()
        
        # Game statistics (for player ships only)
        self.stats = {
            'enemies_destroyed': 0,
            'phasers_fired': 0,
            'torpedos_fired': 0,
            'torpedo_hits': 0,
        }
    
    def can_move(self) -> bool:
        """Check if ship can move."""
        return (self.energy > 0 and self.crew > 0 and not self.is_destroyed and 
                'engines' not in self.disabled_systems)
    
    def can_fire_weapons(self) -> bool:
        """Check if ship can fire weapons."""
        # Can fire if at least one weapon system is operational
        has_working_weapon = ('phasers' not in self.disabled_systems or 
                            'torpedoes' not in self.disabled_systems)
        return self.energy > 0 and self.crew > 0 and not self.is_destroyed and has_working_weapon
    
    def update_shields(self, active: bool) -> None:
        """Activate or deactivate shields."""
        # Can only activate shields if system is not disabled
        if 'shields' in self.disabled_systems:
            self.shields_active = False
        else:
            self.shields_active = active
    
    def get_current_energy_consumption(self) -> float:
        """Calculate and return current energy consumption per turn."""
        energy_drain = 0.0
        
        # Shield drain
        if self.shields_active:
            energy_drain += 2.0
        
        # Propulsion drain
        if self.propulsion.warp_active:
            if self.propulsion.current_speed <= self.propulsion.max_normal_warp:
                # Linear interpolation: 0.1% at minimum warp (2 AU), 0.3% at max warp (9 AU)
                min_warp = 2.0
                max_warp = self.propulsion.max_normal_warp
                min_energy = 0.1
                max_energy = 0.3
                
                if self.propulsion.current_speed >= min_warp:
                    speed_ratio = (self.propulsion.current_speed - min_warp) / (max_warp - min_warp)
                    warp_energy_cost = min_energy + (speed_ratio * (max_energy - min_energy))
                else:
                    warp_energy_cost = min_energy
                
                energy_drain += warp_energy_cost
            else:
                # Beyond maximum warp: 0.3% + (speed - max_warp) / 100
                excess_speed = self.propulsion.current_speed - self.propulsion.max_normal_warp
                max_energy = 0.3
                energy_drain += max_energy + (excess_speed / 100.0)
        elif self.propulsion.impulse_active:
            energy_drain += self.propulsion.impulse_energy_cost
        
        return energy_drain
    
    def update_energy(self) -> None:
        """Update energy based on active systems."""
        energy_drain = 0.0
        
        # Shield drain
        if self.shields_active:
            energy_drain += 2.0
        
        # Propulsion drain
        if self.propulsion.warp_active:
            # Calculate warp energy consumption proportional to speed
            # Between 0.1% and 0.3% for speeds 2-9 AU (linear scaling)
            # Beyond 9 AU: 0.3% + (speed - 9) / 100
            if self.propulsion.current_speed <= self.propulsion.max_normal_warp:
                # Linear interpolation: 0.1% at minimum warp (2 AU), 0.3% at max warp (9 AU)
                min_warp = 2.0
                max_warp = self.propulsion.max_normal_warp
                min_energy = 0.1
                max_energy = 0.3
                
                # Calculate proportional energy cost
                if self.propulsion.current_speed >= min_warp:
                    speed_ratio = (self.propulsion.current_speed - min_warp) / (max_warp - min_warp)
                    warp_energy_cost = min_energy + (speed_ratio * (max_energy - min_energy))
                else:
                    warp_energy_cost = min_energy
                
                energy_drain += warp_energy_cost
            else:
                # Beyond maximum warp: 0.3% + (speed - max_warp) / 100
                excess_speed = self.propulsion.current_speed - self.propulsion.max_normal_warp
                max_energy = 0.3  # Base energy at max warp
                energy_drain += max_energy + (excess_speed / 100.0)
                # Also increase warp core temperature for excess speed
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
        
        Note: Auto-repair is skipped if manual repair was used this turn.
        """
        # Skip auto-repair if manual repair was used this turn
        if self.manual_repair_this_turn:
            self.manual_repair_this_turn = False  # Reset for next turn
            return
        
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
    
    def take_damage(self, damage: float, bypass_shields: bool = False, messages: list = None) -> None:
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
        
        # Check for system damage if ship is now heavily damaged
        if self.damage > 50.0 and messages is not None:
            self.check_for_system_damage(messages)
    
    def take_shield_hit(self, damage: float = 5.0, messages: list = None) -> None:
        """Take a phaser hit to shields."""
        if self.shields_active:
            self.shields = max(0.0, self.shields - damage)
        else:
            # Direct ship damage
            self.damage += damage
        
        # Check if destroyed
        if self.damage >= 100.0:
            self.is_destroyed = True
        
        # Check for system damage if ship is now heavily damaged
        if self.damage > 50.0 and messages is not None:
            self.check_for_system_damage(messages)
    
    def fire_phaser(self, target_ship: 'Ship') -> dict:
        """
        Attempt to fire phasers at a target.
        
        Returns:
            dict with keys: 'hit' (bool), 'damage' (float), 'target_id' (str), 'damage_type' (str)
            or empty dict if fire failed
        """
        if not self.can_fire_weapons():
            return {}
        
        # Check if phasers are disabled
        if 'phasers' in self.disabled_systems:
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
            # Variable damage based on shield status
            if target_ship.shields_active and target_ship.shields > 0:
                # Shields up: 20-30% damage to shields
                damage = random.uniform(20.0, 30.0)
            else:
                # Shields down: 10-20% damage to hull
                damage = random.uniform(10.0, 20.0)
        
        # Record that this ship fired upon the target
        target_ship.fired_upon_by.add(self.id)
        
        # Record shield status before damage
        shields_before = target_ship.shields
        target_ship.take_shield_hit(damage, messages=[])
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
        
        # Check if torpedoes are disabled
        if 'torpedoes' in self.disabled_systems:
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
    
    def check_for_system_damage(self, messages: list) -> None:
        """
        Check if ship should suffer system damage.
        Called when ship takes additional damage after already having >50% damage.
        25% chance to disable one of 7 major systems.
        """
        # Only check if damage is over 50%
        if self.damage <= 50.0:
            return
        
        # 25% chance for a system to be disabled
        if random.random() >= 0.25:
            return
        
        # List of all possible systems
        all_systems = ['shields', 'engines', 'torpedoes', 'phasers', 'scanners', 'radios', 'computers']
        
        # Filter out already disabled systems
        available_systems = [s for s in all_systems if s not in self.disabled_systems]
        
        # If all systems are disabled, nothing to do
        if not available_systems:
            return
        
        # Randomly pick a system to disable
        system_to_disable = random.choice(available_systems)
        self.disabled_systems.add(system_to_disable)
        
        # Apply system-specific effects
        if system_to_disable == 'shields':
            # Shields become ineffective
            self.shields_active = False
            if self.is_player:
                messages.append(">>> CRITICAL: Shield system disabled due to severe damage! <<<")
        
        elif system_to_disable == 'engines':
            # Ship comes to a full stop
            self.stop()
            if self.is_player:
                messages.append(">>> CRITICAL: Engine system disabled due to severe damage! <<<")
        
        elif system_to_disable == 'torpedoes':
            # Torpedoes inoperative
            if self.is_player:
                messages.append(">>> CRITICAL: Torpedo system disabled due to severe damage! <<<")
        
        elif system_to_disable == 'phasers':
            # Phasers inoperative
            if self.is_player:
                messages.append(">>> CRITICAL: Phaser system disabled due to severe damage! <<<")
        
        elif system_to_disable == 'scanners':
            # Scanners inoperative
            if self.is_player:
                messages.append(">>> CRITICAL: Scanner system disabled due to severe damage! <<<")
        
        elif system_to_disable == 'radios':
            # Radios inoperative
            if self.is_player:
                messages.append(">>> CRITICAL: Radio system disabled due to severe damage! <<<")
        
        elif system_to_disable == 'computers':
            # Computers inoperative - cancel weapons lock and auto-nav
            self.weapons.phaser_locked_target = None
            if self.auto_nav_target_id:
                # Cancel auto-nav but keep ship moving on current heading
                self.auto_nav_target_id = None
                self.auto_nav_warp_speed = None
            if self.is_player:
                messages.append(">>> CRITICAL: Computer system disabled due to severe damage! <<<")
    
    def attempt_system_repair(self, messages: list) -> None:
        """
        Attempt to repair one disabled system per turn.
        Repair chance: 25% if damage >= 50%, 50% if damage < 50%
        Only one system can be repaired per turn.
        """
        # No systems to repair
        if not self.disabled_systems:
            return
        
        # Determine repair chance based on damage level
        repair_chance = 0.25 if self.damage >= 50.0 else 0.50
        
        # Roll for repair
        if random.random() >= repair_chance:
            return
        
        # Pick a random system to repair
        system_to_repair = random.choice(list(self.disabled_systems))
        self.disabled_systems.remove(system_to_repair)
        
        # Display repair message
        if self.is_player:
            messages.append(f">> System repair: {system_to_repair.upper()} system is now operational <<")
        
        # Note: No special logic needed here since checks for disabled systems
        # are done in the relevant command/action methods
    
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
            'disabled_systems': list(self.disabled_systems),
        }
