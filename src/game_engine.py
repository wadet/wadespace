"""
Wade Space Game - Game Engine

Main game loop and state management.
"""

from typing import Dict, List, Optional
import random
import math
from src.universe import UniverseGenerator
from src.ship import Ship
from src.universe_objects import Position, Star, Starbase, Planet, BlackHole, AsteroidField
from src.identifiers import ObjectIdentifier
from src.llm_handler import LLMHandler


class GameEngine:
    """Main game engine managing game state and turn processing."""
    
    def __init__(self, universe_seed: Optional[int] = None):
        self.turn_count = 0
        self.universe_seed = universe_seed
        self.id_generator = ObjectIdentifier()
        
        # Initialize LLM handler for enemy AI
        self.llm_handler = LLMHandler()
        
        # Generate universe
        self.universe_generator = UniverseGenerator(seed=universe_seed)
        self.universe_objects = self.universe_generator.generate()
        
        # Create player ship
        player_start_pos = self._find_player_start_position()
        player_id = self.id_generator.generate('ship')
        self.player_ship = Ship(player_id, player_start_pos, is_player=True)
        
        # Create enemy ships
        self.enemy_ships: Dict[str, Ship] = {}
        self._spawn_initial_enemies()
        
        # Active projectiles
        self.active_phasers: List[dict] = []
        self.active_torpedos: List[dict] = []
        
        # Game state
        self.game_over = False
        self.game_over_reason = ""
        self.messages: List[str] = []
        self.debug_mode = False
    
    def _find_player_start_position(self) -> Position:
        """Find a suitable starting position for player ship."""
        # Find a star with nearby planets
        stars = [obj for obj in self.universe_objects.values() if isinstance(obj, Star)]
        if stars:
            start_star = random.choice(stars)
            return Position(start_star.position.x + random.uniform(10, 50), 
                          start_star.position.y + random.uniform(10, 50))
        else:
            return Position(5000, 5000)
    
    def _spawn_initial_enemies(self) -> None:
        """Spawn initial enemy ships, with 1-3 near player start position."""
        # Place 1-3 enemy ships near player's starting position
        nearby_count = random.randint(1, 3)
        for _ in range(nearby_count):
            # Place within 50 AU of player start position
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 50)  # 10-50 AU from player
            pos = Position(
                self.player_ship.position.x + distance * math.cos(angle),
                self.player_ship.position.y + distance * math.sin(angle)
            )
            # Clamp to universe bounds
            pos.x = max(0, min(10000, pos.x))
            pos.y = max(0, min(10000, pos.y))
            
            enemy_id = self.id_generator.generate('ship')
            enemy_ship = Ship(enemy_id, pos, is_player=False)
            enemy_ship.cash = random.randint(500, 2000)
            enemy_ship.behavior_trait = random.choice(['aggressive', 'neutral', 'timid'])
            self.enemy_ships[enemy_id] = enemy_ship
        
        # Place remaining 47-49 enemy ships randomly across universe
        remaining_count = 50 - nearby_count
        for _ in range(remaining_count):
            pos = Position(random.uniform(0, 10000), random.uniform(0, 10000))
            enemy_id = self.id_generator.generate('ship')
            enemy_ship = Ship(enemy_id, pos, is_player=False)
            enemy_ship.cash = random.randint(500, 2000)
            enemy_ship.behavior_trait = random.choice(['aggressive', 'neutral', 'timid'])
            self.enemy_ships[enemy_id] = enemy_ship
    
    def _spawn_single_enemy(self) -> None:
        """Spawn a single new enemy ship at a random location in the universe."""
        pos = Position(random.uniform(0, 10000), random.uniform(0, 10000))
        enemy_id = self.id_generator.generate('ship')
        enemy_ship = Ship(enemy_id, pos, is_player=False)
        enemy_ship.cash = random.randint(500, 2000)
        enemy_ship.behavior_trait = random.choice(['aggressive', 'neutral', 'timid'])
        self.enemy_ships[enemy_id] = enemy_ship
    
    def _handle_ship_destruction(self, destroyer: Ship, destroyed: Ship, destroyed_id: str) -> None:
        """
        Handle reputation changes when one ship destroys another.
        
        Args:
            destroyer: The ship that destroyed the other
            destroyed: The ship that was destroyed
            destroyed_id: The ID of the destroyed ship
        """
        # Only apply reputation changes if destroyer is the player
        if not destroyer.is_player:
            return
        
        old_reputation = destroyer.reputation
        
        # Decrease reputation if destroyed ship was timid OR had reputation > 70
        if destroyed.behavior_trait == 'timid' or destroyed.reputation > 70:
            destroyer.reputation = max(0, destroyer.reputation - 10)
            if destroyer.reputation != old_reputation:
                self.messages.append(f"Reputation changed to {destroyer.reputation} (destroyed {destroyed_id})")
        
        # Increase reputation if destroyed ship was aggressive OR had reputation < 30
        elif destroyed.behavior_trait == 'aggressive' or destroyed.reputation < 30:
            destroyer.reputation = min(100, destroyer.reputation + 10)
            if destroyer.reputation != old_reputation:
                self.messages.append(f"Reputation changed to {destroyer.reputation} (destroyed {destroyed_id})")
    
    def get_objects_in_range(self, position: Position, range_au: float) -> List[tuple]:
        """
        Get all universe objects within range of a position.
        
        Returns:
            List of tuples (object_id, object, distance)
        """
        nearby = []
        for obj_id, obj in self.universe_objects.items():
            distance = position.distance_to(obj.position)
            if distance <= range_au:
                nearby.append((obj_id, obj, distance))
        return sorted(nearby, key=lambda x: x[2])
    
    def get_ships_in_range(self, position: Position, range_au: float, exclude_ship: Optional[str] = None) -> List[tuple]:
        """
        Get all ships within range.
        
        Returns:
            List of tuples (ship_id, ship, distance)
        """
        ships = []
        
        # Check player ship
        distance = position.distance_to(self.player_ship.position)
        if distance <= range_au and (exclude_ship is None or self.player_ship.id != exclude_ship):
            ships.append((self.player_ship.id, self.player_ship, distance))
        
        # Check enemy ships
        for enemy_id, enemy in self.enemy_ships.items():
            distance = position.distance_to(enemy.position)
            if distance <= range_au and (exclude_ship is None or enemy_id != exclude_ship):
                ships.append((enemy_id, enemy, distance))
        
        return sorted(ships, key=lambda x: x[2])
    
    def process_turn(self, player_command: Optional[dict] = None) -> None:
        """
        Process one complete game turn.
        
        Player and enemies execute commands simultaneously.
        """
        self.turn_count += 1
        self.messages = []
        
        # Execute player command
        if player_command:
            self._execute_command(self.player_ship, player_command)
        
        # Process auto-navigation for player ship
        self._process_auto_nav(self.player_ship)
        
        # Get 5 closest enemy ships for debug mode
        closest_enemies = set()
        if self.debug_mode and self.enemy_ships:
            enemy_distances = [
                (enemy_id, enemy_ship.position.distance_to(self.player_ship.position))
                for enemy_id, enemy_ship in self.enemy_ships.items()
            ]
            enemy_distances.sort(key=lambda x: x[1])
            closest_enemies = {enemy_id for enemy_id, _ in enemy_distances[:5]}
        
        # Generate and execute enemy commands (simplified for now)
        for enemy_id, enemy_ship in list(self.enemy_ships.items()):
            self._execute_enemy_command(enemy_ship, show_debug=(enemy_id in closest_enemies))
        
        # Update all objects
        self._update_all_objects()
        
        # Check for collisions and special events
        self._check_collisions()
        self._check_black_hole_destruction()
        self._check_game_over()
    
    def _execute_command(self, ship: Ship, command: dict) -> None:
        """Execute a command for a ship."""
        cmd = command.get('command')
        
        if cmd == 'warp':
            speed = command.get('speed', 5)
            if ship.set_warp_speed(float(speed)):
                self.messages.append(f"Warp drive engaged: {speed} AU/turn")
                # Cancel auto-navigate if active
                if ship.auto_nav_target_id:
                    self.messages.append(f"Auto-navigation cancelled")
                    ship.auto_nav_target_id = None
        
        elif cmd == 'impulse':
            # Cancel auto-navigate first (as per requirements)
            if ship.auto_nav_target_id:
                ship.auto_nav_target_id = None
                self.messages.append(f"Auto-navigation cancelled")
            
            active = command.get('active', False)
            percent = command.get('percent', 100)
            
            if active:
                # Calculate speed as percentage of 1 AU
                speed = percent / 100.0  # Convert percentage to decimal (1-100 -> 0.01-1.0)
                ship.propulsion.impulse_active = True
                ship.propulsion.warp_active = False
                ship.propulsion.current_speed = speed
                self.messages.append(f"Impulse drive activated at {percent}% ({speed:.2f} AU/turn)")
            else:
                ship.propulsion.impulse_active = False
                ship.propulsion.warp_active = False
                ship.propulsion.current_speed = 0.0
                self.messages.append(f"Impulse drive deactivated")
        
        elif cmd == 'heading':
            # Cancel auto-navigate first (as per requirements)
            if ship.auto_nav_target_id:
                ship.auto_nav_target_id = None
                self.messages.append(f"Auto-navigation cancelled")
            
            degrees = command.get('degrees', 0)
            ship.set_heading(float(degrees))
            self.messages.append(f"Heading set to {degrees}°")
            # Cancel auto-navigate if active
            if ship.auto_nav_target_id:
                self.messages.append(f"Auto-navigation cancelled")
                ship.auto_nav_target_id = None
        
        elif cmd == 'shields':
            active = command.get('active', False)
            ship.update_shields(active)
            self.messages.append(f"Shields {'raised' if active else 'lowered'}")
        
        elif cmd == 'scan':
            target_id = command.get('target_id')
            self._execute_scan(ship, target_id)
        
        elif cmd == 'lock':
            target_id = command.get('target_id')
            ship.lock_phasers(target_id)
            self.messages.append(f"Weapons locked onto {target_id}")
        
        elif cmd == 'fire':
            self._execute_fire(ship)
        
        elif cmd == 'torpedo':
            target_id = command.get('target_id')
            # If no target specified, use locked target
            if not target_id and ship.weapons.phaser_locked_target:
                target_id = ship.weapons.phaser_locked_target
                self.messages.append(f"Firing torpedo at locked target {target_id}")
            self._execute_torpedo(ship, target_id)
        
        elif cmd == 'status':
            self._execute_status(ship)
        
        elif cmd == 'stop':
            # Cancel auto-navigate and stop ship
            if ship.auto_nav_target_id:
                ship.auto_nav_target_id = None
                self.messages.append("Auto-navigation cancelled")
            ship.stop()
            self.messages.append("All stop")
        
        elif cmd == 'skip':
            self.messages.append("Turn skipped")
        
        elif cmd == 'nav':
            target_id = command.get('target_id')
            if target_id:
                # Check if target exists in universe or is an enemy ship
                target_obj = self.universe_objects.get(target_id)
                is_enemy = False
                if not target_obj:
                    target_obj = self.enemy_ships.get(target_id)
                    is_enemy = True
                
                if target_obj:
                    distance = ship.position.distance_to(target_obj.position)
                    target_type = "Enemy Ship" if is_enemy else "Object"
                    ship.auto_nav_target_id = target_id
                    self.messages.append(f"Auto-navigation engaged to {target_type} {target_id} ({distance:.1f} AU away)")
                else:
                    self.messages.append(f"Navigation error: Target {target_id} not found")
            else:
                self.messages.append("Navigation error: No target specified")
        
        elif cmd == 'tell':
            target_id = command.get('target_id')
            message = command.get('message', '')
            self._execute_tell(ship, target_id, message)
        
        elif cmd == 'hal':
            question = command.get('question', '')
            self._execute_hal(ship, question)
        
        elif cmd == 'targets':
            self._execute_targets(ship)
        
        elif cmd == 'debug':
            mode = command.get('mode', False)
            self.debug_mode = mode
            self.messages.append(f"Debug mode turned {'ON' if mode else 'OFF'}")
        
        elif cmd == 'repair':
            target_id = command.get('target_id')
            self._execute_repair(ship, target_id)
    
    def _process_auto_nav(self, ship: Ship) -> None:
        """Process auto-navigation for a ship."""
        if not ship.auto_nav_target_id:
            return
        
        # Get target object (check universe objects first, then enemy ships)
        target_obj = self.universe_objects.get(ship.auto_nav_target_id)
        if not target_obj:
            # Check if it's an enemy ship
            target_obj = self.enemy_ships.get(ship.auto_nav_target_id)
        
        if not target_obj:
            self.messages.append(f"Auto-nav: Target {ship.auto_nav_target_id} not found")
            ship.auto_nav_target_id = None
            return
        
        # Calculate distance to target
        distance = ship.position.distance_to(target_obj.position)
        
        # Check if target reached (0.5 AU as per requirements)
        # Use 0.51 to account for floating point precision
        if distance <= 0.51:
            self.messages.append(f"Auto-nav: Target {ship.auto_nav_target_id} reached (within 0.5 AU)")
            ship.auto_nav_target_id = None
            ship.propulsion.warp_active = False
            ship.propulsion.impulse_active = False
            ship.propulsion.current_speed = 0.0
            return
        
        # Calculate heading to target
        dx = target_obj.position.x - ship.position.x
        dy = target_obj.position.y - ship.position.y
        heading = math.degrees(math.atan2(dy, dx)) % 360
        ship.set_heading(heading)
        
        # Prevent overshoot: reduce speed if approaching target
        # If next turn's movement would overshoot, reduce speed accordingly
        safe_speed = distance - 0.5  # Stop 0.5 AU before target
        
        # Choose drive based on distance, but cap speed to prevent overshoot
        if distance > 20.0:
            # Use warp drive for long distances (speed 9 AU/turn max)
            desired_speed = min(9.0, safe_speed)
            if desired_speed >= 2.0:
                if ship.set_warp_speed(desired_speed):
                    ship.propulsion.impulse_active = False
                else:
                    # Warp failed (core overheated), try impulse instead
                    ship.propulsion.warp_active = False
                    ship.propulsion.impulse_active = True
                    ship.propulsion.current_speed = min(1.0, safe_speed)
            else:
                # Speed too low for warp, switch to impulse
                ship.propulsion.warp_active = False
                ship.propulsion.impulse_active = True
                ship.propulsion.current_speed = min(1.0, safe_speed)
        elif distance > 2.0:
            # Medium distance: use slower warp or fast impulse
            desired_speed = min(4.0, safe_speed)
            if desired_speed >= 2.0:
                if ship.set_warp_speed(desired_speed):
                    ship.propulsion.impulse_active = False
                else:
                    ship.propulsion.warp_active = False
                    ship.propulsion.impulse_active = True
                    ship.propulsion.current_speed = min(1.0, safe_speed)
            else:
                ship.propulsion.warp_active = False
                ship.propulsion.impulse_active = True
                ship.propulsion.current_speed = min(1.0, safe_speed)
        else:
            # Close approach: use slow impulse for precision
            # Calculate percentage based on distance (10-100%)
            percent = max(10, min(100, int(distance * 50)))
            speed = percent / 100.0
            ship.propulsion.warp_active = False
            ship.propulsion.impulse_active = True
            ship.propulsion.current_speed = min(speed, safe_speed)
    
    def _execute_enemy_command(self, ship: Ship, show_debug: bool = False) -> None:
        """Execute a command for an enemy ship using GPT-4o LLM when in sensor range."""
        if ship.is_destroyed or ship.is_disabled:
            return
        
        distance_to_player = ship.position.distance_to(self.player_ship.position)
        player_in_range = distance_to_player <= ship.sensors.sensor_range
        
        # Get decision from GPT-4o if player is in sensor range and LLM is available
        if player_in_range and self.llm_handler.enabled:
            decision = self._get_llm_decision(ship, distance_to_player)
            self._execute_llm_decision(ship, decision, distance_to_player, show_debug)
        else:
            # Fallback to basic AI if LLM unavailable or player not in range
            self._execute_basic_enemy_ai(ship, distance_to_player, player_in_range, show_debug)
    
    def _get_llm_decision(self, ship: Ship, distance_to_player: float) -> Dict:
        """Get tactical decision from GPT-4o."""
        # Get nearby objects for context
        nearby_objects = []
        for obj_id, obj in list(self.universe_objects.items())[:20]:
            if obj_id != self.player_ship.id:
                dist = ship.position.distance_to(obj.position)
                if dist < 50:  # Limit to objects within sensor range
                    direction = math.atan2(
                        obj.position.y - ship.position.y,
                        obj.position.x - ship.position.x
                    ) * 180 / math.pi
                    if direction < 0:
                        direction += 360
                    nearby_objects.append((obj_id, obj.get_display_symbol(), dist, direction))
        
        nearby_objects.sort(key=lambda x: x[2])  # Sort by distance
        
        # Get nearby enemy ships for targeting decisions
        nearby_enemy_ships = []
        for enemy_id, enemy_ship in self.enemy_ships.items():
            if enemy_id != ship.id and not enemy_ship.is_destroyed:  # Exclude self and destroyed ships
                dist = ship.position.distance_to(enemy_ship.position)
                if dist < 50:  # Within sensor range
                    nearby_enemy_ships.append(
                        (enemy_id, (enemy_ship.position.x, enemy_ship.position.y), 
                         enemy_ship.damage, dist)
                    )
        
        nearby_enemy_ships.sort(key=lambda x: x[3])  # Sort by distance
        
        # Request decision from LLM
        decision = self.llm_handler.get_enemy_decision(
            enemy_ship_id=ship.id,
            enemy_position=(ship.position.x, ship.position.y),
            enemy_damage=ship.damage,
            enemy_energy=ship.energy,
            enemy_shields=ship.shields,
            enemy_behavior=ship.behavior_trait if ship.behavior_trait else 'neutral',
            player_position=(self.player_ship.position.x, self.player_ship.position.y),
            player_damage=self.player_ship.damage,
            player_reputation=self.player_ship.reputation,
            nearby_objects=nearby_objects,
            nearby_enemy_ships=nearby_enemy_ships,
            turn_count=self.turn_count
        )
        
        return decision
    
    def _execute_llm_decision(self, ship: Ship, decision: Dict, 
                             distance_to_player: float, show_debug: bool) -> None:
        """Execute the decision from LLM. Only ONE action per turn."""
        action_taken = None
        
        # Determine target from decision
        target_id = decision.get('target_id', 'PLAYER')
        target_ship = None
        target_distance = distance_to_player
        
        if target_id == 'PLAYER':
            target_ship = self.player_ship
            target_distance = distance_to_player
        elif target_id in self.enemy_ships:
            target_ship = self.enemy_ships[target_id]
            target_distance = ship.position.distance_to(target_ship.position)
            if target_ship.is_destroyed:
                target_ship = self.player_ship  # Fallback to player if target destroyed
                target_distance = distance_to_player
        else:
            target_ship = self.player_ship  # Default to player if invalid target
            target_distance = distance_to_player
        
        # Priority 1: Fire phasers if requested and in range
        if decision['fire_phasers'] and target_distance < 10:
            ship.weapons.phaser_locked_target = target_ship.id
            result = ship.fire_phaser(target_ship)
            if result:  # result is now a dict
                damage = result.get('damage', 0)
                damage_type = result.get('damage_type', 'unknown')
                target_name = "you" if target_ship == self.player_ship else target_ship.id
                self.messages.append(f"{ship.id} fires phasers at {target_name}! Hit for {damage:.1f}% {damage_type} damage!")
                action_taken = "fire_phasers"
                if show_debug:
                    self.messages.append(f"[DEBUG] {ship.id}: phaser attack on {target_name} - {decision['reason']}")
        
        # Priority 2: Fire torpedoes if no other action and requested
        elif decision['fire_torpedos'] and target_distance < 50 and ship.weapons.torpedos > 0:
            result = ship.fire_torpedo(target_ship.position, target_ship)
            if result:  # result is now a dict
                result_target_id = result.get('target_id', 'unknown')
                target_name = "you" if result_target_id == self.player_ship.id else result_target_id
                self.messages.append(f"{ship.id} launches a torpedo at {target_name}!")
                action_taken = "fire_torpedo"
                if show_debug:
                    self.messages.append(f"[DEBUG] {ship.id}: torpedo attack on {target_name}")
        
        # Priority 3: Movement if no weapons fired
        else:
            ship.set_heading(decision['heading'])
            ship.set_warp_speed(decision['speed'])
            action_taken = "movement"
            
            # If fleeing, only return fire if already fired upon by the target
            if decision['action'] == 'evade':
                # Only return fire if this ship has been fired upon by the target
                if target_ship.id in ship.fired_upon_by:
                    # Lock on to target for potential return fire
                    ship.lock_phasers(target_ship.id)
                    
                    # Try phasers first if in range (< 10 AU)
                    if target_distance < 10 and ship.weapons.phaser_operational:
                        result = ship.fire_phaser(target_ship)
                        if result:
                            target_name = "you" if result['target_id'] == self.player_ship.id else result['target_id']
                            self.messages.append(f"[{ship.id}] Return fire while fleeing! Phaser hit on {target_name}: {result['damage']:.1f}% {result['damage_type']} damage")
                    # Otherwise try torpedos if in range (< 50 AU) and have ammo
                    elif target_distance < 50 and ship.weapons.torpedos > 0:
                        result = ship.fire_torpedo(target_ship.position, target_ship)
                        if result:
                            target_name = "you" if result['target_id'] == self.player_ship.id else result['target_id']
                            self.messages.append(f"[{ship.id}] Return fire while fleeing! Torpedo launched at {target_name}")
            
            if show_debug:
                action = decision['action']
                heading = decision['heading']
                speed = decision['speed']
                target_name = "PLAYER" if target_ship == self.player_ship else target_ship.id
                self.messages.append(
                    f"[DEBUG] {ship.id}: {action} @ heading {heading}° warp {speed} targeting {target_name} - {decision['reason']}"
                )
    
    def _execute_basic_enemy_ai(self, ship: Ship, distance_to_player: float, 
                               player_in_range: bool, show_debug: bool) -> None:
        """Fallback basic AI for when LLM is unavailable. Only ONE action per turn."""
        action_desc = None
        behavior = ship.behavior_trait if ship.behavior_trait else 'neutral'
        player_rep = self.player_ship.reputation
        
        # Find nearby enemy ships as potential targets
        nearby_enemies = []
        for enemy_id, enemy_ship in self.enemy_ships.items():
            if enemy_id != ship.id and not enemy_ship.is_destroyed:
                dist = ship.position.distance_to(enemy_ship.position)
                if dist < 50:  # Within sensor range
                    nearby_enemies.append((enemy_id, enemy_ship, dist))
        
        # Sort by distance
        nearby_enemies.sort(key=lambda x: x[2])
        
        # Determine best target (player or another enemy)
        target_ship = self.player_ship
        target_distance = distance_to_player
        target_is_player = True
        
        # Consider attacking nearby enemy ships based on behavior and tactical situation
        if nearby_enemies:
            # Aggressive enemies are opportunistic - attack any nearby damaged enemy
            if behavior == 'aggressive':
                for enemy_id, enemy_ship, dist in nearby_enemies[:5]:  # Check 5 closest
                    # Target damaged enemies that are close
                    if enemy_ship.damage > 30 and dist < 25:
                        target_ship = enemy_ship
                        target_distance = dist
                        target_is_player = False
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: Targeting damaged enemy {enemy_id} ({enemy_ship.damage:.1f}% dmg, {dist:.1f} AU)")
                        break
                    # Or target very close enemies even if not damaged
                    elif dist < 10 and enemy_ship.damage > 0:
                        target_ship = enemy_ship
                        target_distance = dist
                        target_is_player = False
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: Targeting close enemy {enemy_id} ({dist:.1f} AU)")
                        break
            
            # Neutral enemies target damaged nearby enemies if they're easier than player
            elif behavior == 'neutral':
                for enemy_id, enemy_ship, dist in nearby_enemies[:3]:
                    # Target heavily damaged enemies that are closer
                    if enemy_ship.damage > 40 and dist < distance_to_player * 0.8:
                        target_ship = enemy_ship
                        target_distance = dist
                        target_is_player = False
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: Targeting damaged enemy {enemy_id} ({enemy_ship.damage:.1f}% dmg)")
                        break
            
            # Timid enemies only attack very damaged enemies or if cornered
            elif behavior == 'timid':
                for enemy_id, enemy_ship, dist in nearby_enemies[:2]:
                    # Only target very damaged enemies
                    if enemy_ship.damage > 60 and dist < 20:
                        target_ship = enemy_ship
                        target_distance = dist
                        target_is_player = False
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: Targeting very damaged enemy {enemy_id} ({enemy_ship.damage:.1f}% dmg)")
                        break
        
        if player_in_range or target_distance < 50:
            # Determine if enemy should attack based on behavior trait
            should_attack = False
            should_flee = False
            
            # Check attack conditions based on behavior trait
            if behavior == 'aggressive':
                # Aggressive: attack if player reputation < 70 or targeting any damaged enemy
                if (target_is_player and player_rep < 70) or (not target_is_player and target_ship.damage > 20):
                    should_attack = True
                # Flee only if own damage > 80%
                if ship.damage > 80.0:
                    should_flee = True
                    should_attack = False
            
            elif behavior == 'neutral':
                # Neutral: attack only if provoked or player reputation < 50, or targeting damaged enemy
                # For now, consider "provoked" if player has attacked (damage > 0)
                if (ship.damage > 0 or (target_is_player and player_rep < 50)) or (not target_is_player and target_ship.damage > 30):
                    should_attack = True
                # Flee if own damage > 50%
                if ship.damage > 50.0:
                    should_flee = True
                    should_attack = False
            
            elif behavior == 'timid':
                # Timid: attack only if provoked or player reputation < 25, or very damaged enemy
                if (ship.damage > 0 or (target_is_player and player_rep < 25)) or (not target_is_player and target_ship.damage > 50):
                    should_attack = True
                # Flee if own damage > 30%, unless player reputation < 10
                if ship.damage > 30.0 and player_rep >= 10:
                    should_flee = True
                    should_attack = False
            
            # Execute flee behavior
            if should_flee:
                dx = ship.position.x - target_ship.position.x
                dy = ship.position.y - target_ship.position.y
                
                if dx != 0 or dy != 0:
                    escape_heading = math.atan2(dy, dx) * 180 / math.pi
                    if escape_heading < 0:
                        escape_heading += 360
                    
                    ship.set_heading(escape_heading)
                    ship.set_warp_speed(8.0)
                    target_name = "player" if target_is_player else target_ship.id
                    action_desc = f"fleeing from {target_name} ({behavior}, damage {ship.damage:.0f}%) at {target_distance:.1f} AU"
                    
# Only return fire if already fired upon by the target
                if target_ship.id in ship.fired_upon_by:
                    ship.lock_phasers(target_ship.id)
                    
                    # Try phasers first if in range (< 10 AU)
                    if target_distance < 10 and ship.weapons.phaser_operational:
                        result = ship.fire_phaser(target_ship)
                        if result:
                            result_name = "you" if result['target_id'] == self.player_ship.id else result['target_id']
                            self.messages.append(f"[{ship.id}] Return fire while fleeing! Phaser hit on {result_name}: {result['damage']:.1f}% {result['damage_type']} damage")
                    # Otherwise try torpedos if in range (< 50 AU) and have ammo
                    elif target_distance < 50 and ship.weapons.torpedos > 0:
                        result = ship.fire_torpedo(target_ship.position, target_ship)
                        if result:
                            result_name = "you" if result['target_id'] == self.player_ship.id else result['target_id']
                            self.messages.append(f"[{ship.id}] Return fire while fleeing! Torpedo launched at {result_name}")
                    
                    if show_debug:
                        self.messages.append(f"[DEBUG] {ship.id}: {action_desc}")
            
            # Execute attack behavior
            elif should_attack:
                # Priority: Fire phasers if very close (30% chance)
                if target_distance < 15 and random.random() < 0.3:
                    ship.weapons.phaser_locked_target = target_ship.id
                    result = ship.fire_phaser(target_ship)
                    if result:  # result is now a dict
                        damage = result.get('damage', 0)
                        damage_type = result.get('damage_type', 'unknown')
                        target_name = "you" if result['target_id'] == self.player_ship.id else result['target_id']
                        self.messages.append(f"{ship.id} fires phasers at {target_name}! Hit for {damage:.1f}% {damage_type} damage!")
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: phaser attack on {target_name} ({behavior})")
                # Or fire torpedoes if in range (20% chance)
                elif target_distance < 50 and target_distance > 15 and random.random() < 0.2 and ship.weapons.torpedos > 0:
                    result = ship.fire_torpedo(target_ship.position, target_ship)
                    if result:  # result is now a dict
                        result_target_id = result.get('target_id', 'unknown')
                        target_name = "you" if result_target_id == self.player_ship.id else result_target_id
                        self.messages.append(f"{ship.id} launches a torpedo at {target_name}!")
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: torpedo attack on {target_name} ({behavior})")
                # Otherwise move to close in
                else:
                    dx = target_ship.position.x - ship.position.x
                    dy = target_ship.position.y - ship.position.y
                    
                    if dx != 0 or dy != 0:
                        attack_heading = math.atan2(dy, dx) * 180 / math.pi
                        if attack_heading < 0:
                            attack_heading += 360
                        
                        ship.set_heading(attack_heading)
                        ship.set_warp_speed(6.0)
                        target_name = "player" if target_is_player else target_ship.id
                        action_desc = f"closing in to attack {target_name} ({behavior}) at {target_distance:.1f} AU"
                        if show_debug:
                            self.messages.append(f"[DEBUG] {ship.id}: {action_desc}")
            else:
                # Not attacking or fleeing - patrol or maintain distance
                if random.random() < 0.3:
                    random_heading = random.uniform(0, 359)
                    random_speed = random.choice([2, 4])
                    ship.set_heading(random_heading)
                    ship.set_warp_speed(float(random_speed))
                    action_desc = f"patrolling ({behavior}) heading {random_heading:.0f}° at warp {random_speed}"
                    if show_debug:
                        self.messages.append(f"[DEBUG] {ship.id}: {action_desc}")
        else:
            # Player not in sensor range - random patrol behavior
            if random.random() < 0.25:
                random_heading = random.uniform(0, 359)
                random_speed = random.choice([2, 4, 6, 8])
                ship.set_heading(random_heading)
                ship.set_warp_speed(float(random_speed))
                action_desc = f"patrolling ({behavior}) heading {random_heading:.0f}° at warp {random_speed}"
                if show_debug:
                    self.messages.append(f"[DEBUG] {ship.id}: {action_desc}")
    
    
    def _execute_scan(self, ship: Ship, target_id: Optional[str] = None) -> None:
        """Execute scan command."""
        if not ship.sensors.operational:
            self.messages.append("Sensors offline!")
            return
        
        if target_id:
            # Scan specific object
            target_obj = None
            distance = 0.0
            
            # Check if it's a universe object (star, planet, etc.)
            if target_id in self.universe_objects:
                target_obj = self.universe_objects[target_id]
                distance = ship.position.distance_to(target_obj.position)
            # Check if it's the player ship
            elif target_id == self.player_ship.id:
                target_obj = self.player_ship
                distance = ship.position.distance_to(self.player_ship.position)
            # Check if it's an enemy ship
            elif target_id in self.enemy_ships:
                target_obj = self.enemy_ships[target_id]
                distance = ship.position.distance_to(target_obj.position)
            
            if target_obj:
                if distance > ship.sensors.sensor_range:
                    self.messages.append(f"{target_id} is out of sensor range")
                else:
                    # Display scan information
                    if isinstance(target_obj, Ship):
                        # For ships, show more detailed information
                        status = "destroyed" if target_obj.is_destroyed else "operational"
                        shields_status = "up" if target_obj.shields_active else "down"
                        behavior = f", Behavior: {target_obj.behavior_trait}" if target_obj.behavior_trait else ""
                        self.messages.append(f"Scan of {target_id}: Ship at {distance:.1f} AU")
                        self.messages.append(f"  Status: {status}, Damage: {target_obj.damage:.1f}%, Energy: {target_obj.energy:.1f}%")
                        self.messages.append(f"  Shields: {shields_status} ({target_obj.shields:.1f}%), Crew: {target_obj.crew}{behavior}")
                        self.messages.append(f"  Speed: {target_obj.propulsion.current_speed:.1f} AU/turn, Heading: {target_obj.propulsion.current_heading:.0f}°")
                    else:
                        # For universe objects
                        self.messages.append(f"Scan of {target_id}: {target_obj.get_display_symbol()} at {distance:.1f} AU")
            else:
                self.messages.append(f"Object {target_id} not found")
        else:
            # Scan nearby objects - include both universe objects and ships
            nearby_objects = self.get_objects_in_range(ship.position, ship.sensors.sensor_range)
            nearby_ships = self.get_ships_in_range(ship.position, ship.sensors.sensor_range, exclude_ship=ship.id)
            
            # Combine and sort by distance
            all_nearby = nearby_objects + nearby_ships
            all_nearby.sort(key=lambda x: x[2])
            
            self.messages.append(f"Scan results (sensor range: {ship.sensors.sensor_range:.0f} AU):")
            if not all_nearby:
                self.messages.append("  No objects detected")
            else:
                for obj_id, obj, distance in all_nearby[:20]:
                    if hasattr(obj, 'get_display_symbol'):
                        symbol = obj.get_display_symbol()
                    else:
                        symbol = "SHIP"
                    self.messages.append(f"  {obj_id}: {symbol} @ {distance:.1f} AU")
                if len(all_nearby) > 20:
                    self.messages.append(f"  ... and {len(all_nearby) - 20} more objects")
    
    def _execute_fire(self, ship: Ship) -> None:
        """Execute phaser fire."""
        if not ship.weapons.phaser_locked_target:
            self.messages.append("No target locked")
            return
        
        # Find target
        target_id = ship.weapons.phaser_locked_target
        target_ship = None
        
        if target_id == self.player_ship.id:
            target_ship = self.player_ship
        else:
            target_ship = self.enemy_ships.get(target_id)
        
        if not target_ship:
            self.messages.append(f"Target {target_id} not found")
            ship.weapons.phaser_locked_target = None  # Clear invalid lock
            return
        
        distance = ship.position.distance_to(target_ship.position)
        if distance > ship.weapons.phaser_range:
            self.messages.append(f"Target out of phaser range ({distance:.1f} AU)")
            return
        
        result = ship.fire_phaser(target_ship)
        if result:  # result is now a dict
            damage = result.get('damage', 0)
            damage_type = result.get('damage_type', 'unknown')
            self.messages.append(f"Phaser fired at {target_id}! Hit for {damage:.1f}% {damage_type} damage!")
            
            # Check if target destroyed and apply reputation changes
            if target_ship.is_destroyed:
                self._handle_ship_destruction(ship, target_ship, target_id)
    
    def _execute_torpedo(self, ship: Ship, target_id: Optional[str] = None) -> None:
        """Execute torpedo fire."""
        if not target_id:
            self.messages.append("No target specified for torpedo")
            return
        
        # Find target
        target_ship = None
        target_pos = None
        
        if target_id == self.player_ship.id:
            target_ship = self.player_ship
            target_pos = target_ship.position
        elif target_id in self.enemy_ships:
            target_ship = self.enemy_ships[target_id]
            target_pos = target_ship.position
        elif target_id in self.universe_objects:
            obj = self.universe_objects[target_id]
            target_pos = obj.position
        
        if not target_pos:
            self.messages.append(f"Target {target_id} not found")
            return
        
        result = ship.fire_torpedo(target_pos)
        if result:  # result is now a dict
            self.messages.append(f"Torpedo fired at {target_id}")
    
    def _execute_status(self, ship: Ship) -> None:
        """Display ship status."""
        status = ship.get_status_dict()
        self.messages.append(f"=== {ship.id} Status ===")
        self.messages.append(f"Damage: {status['damage']:.1f}%")
        self.messages.append(f"Energy: {status['energy']:.1f}%")
        self.messages.append(f"Shields: {status['shields']:.1f}%")
        self.messages.append(f"Crew: {status['crew']}/1000")
        self.messages.append(f"Cash: ${status['cash']}")
        self.messages.append(f"Torpedos: {status['torpedos']}")
    
    def _execute_hal(self, ship: Ship, question: str) -> None:
        """Execute hal command (query system with natural language support)."""
        # First, try using LLM for natural language understanding
        if self.llm_handler.enabled:
            try:
                # Check if question is asking for "nearest" or "closest" - search entire universe
                lower_q = question.lower()
                search_entire_universe = any(keyword in lower_q for keyword in 
                    ['nearest', 'closest', 'where is', 'find', 'locate'])
                
                universe_data = self._get_universe_data_for_llm(ship, search_entire_universe)
                answer = self.llm_handler.answer_player_question(question, universe_data)
                
                # Split the answer into lines for better message display
                for line in answer.split('\n'):
                    if line.strip():
                        self.messages.append(line.strip())
                return
            except Exception as e:
                # If LLM fails, fall back to pattern matching
                print(f"[WARNING] LLM question answering failed: {e}")
                self.messages.append("Ship's computer degraded - using basic pattern matching.")
        
        # Fallback: Use hardcoded pattern matching
        lower_q = question.lower()
        
        # Query: Nearest enemy ship
        if any(keyword in lower_q for keyword in ['nearest enemy', 'closest enemy', 'nearest hostile', 'closest hostile']):
            self._query_nearest_enemy(ship)
        
        # Query: Nearest starbase (check before star to avoid partial match)
        elif any(keyword in lower_q for keyword in ['nearest starbase', 'closest starbase', 'nearest base', 'closest base', 'nearest enemy base', 'closest enemy base']):
            self._query_nearest_object(ship, 'sb', 'starbase')
        
        # Query: Nearest star
        elif any(keyword in lower_q for keyword in ['nearest star', 'closest star']):
            self._query_nearest_object(ship, 'st', 'star')
        
        # Query: Nearest planet
        elif any(keyword in lower_q for keyword in ['nearest planet', 'closest planet']):
            self._query_nearest_object(ship, 'pl', 'planet')
        
        # Query: Nearest black hole
        elif any(keyword in lower_q for keyword in ['nearest black hole', 'closest black hole']):
            self._query_nearest_object(ship, 'bh', 'black hole')
        
        # Query: Nearest wormhole
        elif any(keyword in lower_q for keyword in ['nearest wormhole', 'closest wormhole']):
            self._query_nearest_object(ship, 'wh', 'wormhole')
        
        # Query: Nearest pulsar
        elif any(keyword in lower_q for keyword in ['nearest pulsar', 'closest pulsar']):
            self._query_nearest_object(ship, 'pu', 'pulsar')
        
        # Query: Nearest asteroid field
        elif any(keyword in lower_q for keyword in ['nearest asteroid', 'closest asteroid']):
            self._query_nearest_object(ship, 'af', 'asteroid field')
        
        # Query: Object count
        elif 'how many' in lower_q or 'count' in lower_q:
            self._query_object_count(lower_q)
        
        # Query: Enemy count
        elif 'enemies left' in lower_q or 'enemy count' in lower_q:
            active_enemies = len([e for e in self.enemy_ships.values() if not e.is_destroyed])
            self.messages.append(f"Active enemy ships: {active_enemies}/{len(self.enemy_ships)}")
        
        # Query: Where am I
        elif 'where am i' in lower_q or 'my location' in lower_q or 'my position' in lower_q:
            self.messages.append(f"Your position: ({ship.position.x:.1f}, {ship.position.y:.1f})")
        
        # Query: Distance to object
        elif 'distance to' in lower_q or 'how far' in lower_q:
            self._query_distance(ship, question)
        
        # Query: Objects in range
        elif 'in range' in lower_q or 'nearby' in lower_q or 'around me' in lower_q:
            self._query_nearby_objects(ship)
        
        # Query: Specific object info
        elif 'what is' in lower_q or 'tell me about' in lower_q or 'info on' in lower_q:
            self._query_object_info(question)
        
        else:
            self.messages.append("I don't understand that question. Try asking:")
            self.messages.append("  - 'nearest enemy', 'nearest starbase', 'nearest planet'")
            self.messages.append("  - 'how many enemies left', 'where am i'")
            self.messages.append("  - 'distance to <id>', 'nearby objects'")
            self.messages.append("  - 'what is <id>', 'how many stars'")
    
    def _execute_tell(self, ship: Ship, target_id: str, message: str) -> None:
        """Execute tell command - send message to enemy ship or enemy starbase and get LLM-generated response."""
        # Check if target is an enemy ship
        target_entity = None
        entity_type = None
        
        if target_id in self.enemy_ships:
            target_entity = self.enemy_ships[target_id]
            entity_type = 'ship'
            
            # Check if enemy ship is destroyed
            if target_entity.is_destroyed:
                self.messages.append(f"Cannot send message: {target_id} has been destroyed.")
                return
        
        # Check if target is an enemy starbase
        elif target_id in self.universe_objects:
            obj = self.universe_objects[target_id]
            if isinstance(obj, Starbase):
                if not obj.friendly_to_player:
                    target_entity = obj
                    entity_type = 'starbase'
                else:
                    self.messages.append(f"Cannot send message: {target_id} is a friendly starbase.")
                    return
            else:
                self.messages.append(f"Cannot send message: {target_id} is not a valid target.")
                return
        else:
            self.messages.append(f"Cannot send message: {target_id} not found.")
            return
        
        # Calculate distance to target
        distance = ship.position.distance_to(target_entity.position)
        
        # Display player's message
        self.messages.append(f"You to {target_id}: {message}")
        
        # Generate LLM response with combat context
        if self.llm_handler.enabled:
            # Build context for the enemy captain/commander
            player_damage = ship.damage
            target_damage = getattr(target_entity, 'damage', 0)
            
            context = {
                'player_message': message,
                'distance': distance,
                'player_damage': player_damage,
                'enemy_damage': target_damage,
                'player_shields': ship.shields,
                'enemy_shields': getattr(target_entity, 'shields', 100),
                'turn_count': self.turn_count,
                'entity_type': entity_type
            }
            
            response = self.llm_handler.get_enemy_taunt(target_id, context)
        else:
            # Fallback response if LLM is not available
            response = f"[{target_id}]: *Static interference*"
        
        self.messages.append(response)

    
    def _query_nearest_enemy(self, ship: Ship) -> None:
        """Find and report the nearest enemy ship."""
        if not self.enemy_ships:
            self.messages.append("No enemy ships detected in the universe.")
            return
        
        # Find nearest active enemy
        nearest_enemy = None
        nearest_distance = float('inf')
        
        for enemy_id, enemy_ship in self.enemy_ships.items():
            if not enemy_ship.is_destroyed:
                distance = ship.position.distance_to(enemy_ship.position)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_enemy = (enemy_id, enemy_ship)
        
        if nearest_enemy:
            enemy_id, enemy_ship = nearest_enemy
            health = 100.0 - enemy_ship.damage
            self.messages.append(f"Nearest enemy: {enemy_id}")
            self.messages.append(f"  Location: ({enemy_ship.position.x:.1f}, {enemy_ship.position.y:.1f})")
            self.messages.append(f"  Distance: {nearest_distance:.1f} AU")
            self.messages.append(f"  Health: {health:.1f}% | Shields: {enemy_ship.shields:.1f}%")
        else:
            self.messages.append("No active enemy ships detected.")
    
    def _query_nearest_object(self, ship: Ship, prefix: str, obj_name: str) -> None:
        """Find and report the nearest object of a given type."""
        nearby = self.get_objects_in_range(ship.position, 10000.0)  # Search entire universe
        objects = [(obj_id, obj, dist) for obj_id, obj, dist in nearby if obj_id.startswith(prefix)]
        
        if objects:
            nearest_id, nearest_obj, distance = objects[0]
            self.messages.append(f"Nearest {obj_name}: {nearest_id}")
            self.messages.append(f"  Location: ({nearest_obj.position.x:.1f}, {nearest_obj.position.y:.1f})")
            self.messages.append(f"  Distance: {distance:.1f} AU")
        else:
            self.messages.append(f"No {obj_name}s found in the universe.")
    
    def _query_object_count(self, query: str) -> None:
        """Count objects of a specific type."""
        if 'star' in query:
            count = len([obj for obj in self.universe_objects.values() if isinstance(obj, Star)])
            self.messages.append(f"Stars in universe: {count}")
        elif 'planet' in query:
            count = len([obj for obj in self.universe_objects.values() if isinstance(obj, Planet)])
            self.messages.append(f"Planets in universe: {count}")
        elif 'starbase' in query or 'base' in query:
            count = len([obj for obj in self.universe_objects.values() if isinstance(obj, Starbase)])
            self.messages.append(f"Starbases in universe: {count}")
        elif 'black hole' in query:
            count = len([obj for obj in self.universe_objects.values() if isinstance(obj, BlackHole)])
            self.messages.append(f"Black holes in universe: {count}")
        elif 'asteroid' in query:
            count = len([obj for obj in self.universe_objects.values() if isinstance(obj, AsteroidField)])
            self.messages.append(f"Asteroid fields in universe: {count}")
        elif 'enemy' in query or 'enemies' in query or 'hostile' in query:
            count = len([e for e in self.enemy_ships.values() if not e.is_destroyed])
            self.messages.append(f"Active enemy ships: {count}/{len(self.enemy_ships)}")
        else:
            self.messages.append(f"Total objects in universe: {len(self.universe_objects)}")
            self.messages.append(f"Active enemy ships: {len(self.enemy_ships)}")
    
    def _query_distance(self, ship: Ship, query: str) -> None:
        """Calculate distance to a specific object."""
        # Extract object ID from query using regex for better accuracy
        import re
        # Match patterns like st1234, pl5678, s1234, etc.
        match = re.search(r'\b(st\d+|pl\d+|sb\d+|bh\d+|wh\d+|pu\d+|af\d+|s\d+)\b', query, re.IGNORECASE)
        
        if not match:
            self.messages.append("Please specify an object ID (e.g., 'distance to st1')")
            return
        
        target_id = match.group(1).lower()
        
        # Check universe objects
        if target_id in self.universe_objects:
            obj = self.universe_objects[target_id]
            distance = ship.position.distance_to(obj.position)
            self.messages.append(f"Distance to {target_id}: {distance:.1f} AU")
            self.messages.append(f"  Location: ({obj.position.x:.1f}, {obj.position.y:.1f})")
        # Check enemy ships
        elif target_id in self.enemy_ships:
            enemy = self.enemy_ships[target_id]
            distance = ship.position.distance_to(enemy.position)
            self.messages.append(f"Distance to {target_id}: {distance:.1f} AU")
            self.messages.append(f"  Location: ({enemy.position.x:.1f}, {enemy.position.y:.1f})")
        else:
            self.messages.append(f"Object {target_id} not found.")
    
    def _query_nearby_objects(self, ship: Ship) -> None:
        """List objects within sensor range."""
        nearby = self.get_objects_in_range(ship.position, ship.sensors.sensor_range)
        
        if not nearby:
            self.messages.append(f"No objects within sensor range ({ship.sensors.sensor_range:.0f} AU)")
            return
        
        self.messages.append(f"Objects within {ship.sensors.sensor_range:.0f} AU:")
        for obj_id, obj, distance in nearby[:10]:
            symbol = obj.get_display_symbol() if hasattr(obj, 'get_display_symbol') else '?'
            self.messages.append(f"  {obj_id} ({symbol}): {distance:.1f} AU")
        
        if len(nearby) > 10:
            self.messages.append(f"  ... and {len(nearby) - 10} more objects")
    
    def _query_object_info(self, query: str) -> None:
        """Get detailed information about a specific object."""
        # Extract object ID from query using regex for better accuracy
        import re
        # Match patterns like st1234, pl5678, s1234, etc.
        match = re.search(r'\b(st\d+|pl\d+|sb\d+|bh\d+|wh\d+|pu\d+|af\d+|s\d+)\b', query, re.IGNORECASE)
        
        if not match:
            self.messages.append("Please specify an object ID (e.g., 'what is st1')")
            return
        
        target_id = match.group(1).lower()
        
        # Check universe objects
        if target_id in self.universe_objects:
            obj = self.universe_objects[target_id]
            symbol = obj.get_display_symbol() if hasattr(obj, 'get_display_symbol') else '?'
            self.messages.append(f"Object {target_id} ({symbol}):")
            self.messages.append(f"  Type: {type(obj).__name__}")
            self.messages.append(f"  Location: ({obj.position.x:.1f}, {obj.position.y:.1f})")
            distance = self.player_ship.position.distance_to(obj.position)
            self.messages.append(f"  Distance from you: {distance:.1f} AU")
        # Check enemy ships
        elif target_id in self.enemy_ships:
            enemy = self.enemy_ships[target_id]
            self.messages.append(f"Enemy ship {target_id}:")
            self.messages.append(f"  Location: ({enemy.position.x:.1f}, {enemy.position.y:.1f})")
            distance = self.player_ship.position.distance_to(enemy.position)
            self.messages.append(f"  Distance from you: {distance:.1f} AU")
            self.messages.append(f"  Health: {100 - enemy.damage:.1f}%")
            self.messages.append(f"  Shields: {enemy.shields:.1f}%")
            self.messages.append(f"  Status: {'DESTROYED' if enemy.is_destroyed else 'ACTIVE'}")
        else:
            self.messages.append(f"Object {target_id} not found.")
    
    def _get_universe_data_for_llm(self, ship: Ship, search_entire_universe: bool = False) -> Dict:
        """
        Extract and format universe data for LLM question answering.
        
        Args:
            ship: The player's ship
            search_entire_universe: If True, include ALL objects in universe (not just sensor range)
        
        Returns:
            Dictionary with all relevant universe data
        """
        # Determine search range
        if search_entire_universe:
            search_range = 100000.0  # Entire universe
        else:
            search_range = ship.sensors.sensor_range
        
        # Get objects within search range
        nearby = self.get_objects_in_range(ship.position, search_range)
        nearby_formatted = []
        for obj_id, obj, distance in nearby:
            obj_type = type(obj).__name__
            obj_data = {
                'type': obj_type,
                'position': (obj.position.x, obj.position.y),
                'distance': distance
            }
            # Add starbase-specific info
            if isinstance(obj, Starbase):
                obj_data['friendly'] = obj.friendly_to_player
            nearby_formatted.append((obj_id, obj_data))
        
        # Get all enemy ships data
        enemy_ships_data = {}
        for enemy_id, enemy_ship in self.enemy_ships.items():
            distance = ship.position.distance_to(enemy_ship.position)
            enemy_ships_data[enemy_id] = {
                'position': (enemy_ship.position.x, enemy_ship.position.y),
                'distance': distance,
                'damage': enemy_ship.damage,
                'shields': enemy_ship.shields,
                'energy': enemy_ship.energy,
                'is_destroyed': enemy_ship.is_destroyed
            }
        
        return {
            'player_position': (ship.position.x, ship.position.y),
            'nearby_objects': nearby_formatted,
            'enemy_ships': enemy_ships_data,
            'sensor_range': ship.sensors.sensor_range,
            'search_entire_universe': search_entire_universe
        }
    
    def _execute_targets(self, ship: Ship) -> None:
        """Display the 5 closest enemy ships to the player."""
        if not self.enemy_ships:
            self.messages.append("No enemy ships detected in the universe.")
            return
        
        self.messages.append(f"=== CLOSEST ENEMY SHIPS ===")
        
        # Sort enemy ships by distance from player
        enemy_list = []
        for enemy_id, enemy_ship in self.enemy_ships.items():
            distance = ship.position.distance_to(enemy_ship.position)
            status = "DESTROYED" if enemy_ship.is_destroyed else ("DISABLED" if enemy_ship.is_disabled else "ACTIVE")
            enemy_list.append((distance, enemy_id, enemy_ship, status))
        
        # Sort by distance (ascending)
        enemy_list.sort(key=lambda x: x[0])
        
        # Display first 5 closest ships
        for i, (distance, enemy_id, enemy_ship, status) in enumerate(enemy_list[:5]):
            health = 100.0 - enemy_ship.damage
            shield = enemy_ship.shields
            energy = enemy_ship.energy
            self.messages.append(
                f"  {i+1}. {enemy_id}: {distance:7.1f} AU | "
                f"HP:{health:5.1f}% SH:{shield:5.1f}% EN:{energy:5.1f}% [{status}]"
            )
        
        # Show total count
        self.messages.append(f"Total enemy ships in universe: {len(self.enemy_ships)}")
    
    def _execute_repair(self, ship: Ship, target_id: Optional[str] = None) -> None:
        """
        Execute repair command.
        
        If no target_id: repair player's own ship at 10% per turn (only when stopped).
        If target_id provided: repair another ship (5% per turn) or friendly starbase (2% per turn).
        Player's ship must be within 0.5 AU of target and not moving (stopped).
        
        Manual repair disables auto-repair for this turn.
        """
        if target_id:
            # Repairing another object
            # Check if ship is stopped
            if ship.propulsion.current_speed != 0.0:
                self.messages.append("Repair error: Ship must be stopped to repair another object")
                return
            
            # Find target object
            target_obj = None
            target_type = None
            
            # Check enemy ships
            if target_id in self.enemy_ships:
                target_obj = self.enemy_ships[target_id]
                target_type = 'ship'
            # Check player ship
            elif target_id == self.player_ship.id:
                target_obj = self.player_ship
                target_type = 'ship'
            # Check universe objects (for starbases)
            elif target_id in self.universe_objects:
                obj = self.universe_objects[target_id]
                if isinstance(obj, Starbase):
                    target_obj = obj
                    target_type = 'starbase'
                else:
                    self.messages.append(f"Repair error: Cannot repair {target_id} (not a ship or starbase)")
                    return
            else:
                self.messages.append(f"Repair error: Target {target_id} not found")
                return
            
            # Check distance to target
            distance = ship.position.distance_to(target_obj.position)
            if distance > 0.5:
                self.messages.append(f"Repair error: {target_id} is too far away ({distance:.2f} AU). Must be within 0.5 AU")
                return
            
            # Check if target is destroyed
            if hasattr(target_obj, 'is_destroyed') and target_obj.is_destroyed:
                self.messages.append(f"Repair error: {target_id} is destroyed and cannot be repaired")
                return
            
            # Determine repair rate and check if target is friendly
            if target_type == 'ship':
                # Can repair any ship at 5% per turn
                repair_rate = 5.0
                repair_amount = min(repair_rate, target_obj.damage)
                target_obj.damage = max(0.0, target_obj.damage - repair_amount)
                # Mark target as having received manual repair
                target_obj.manual_repair_this_turn = True
                self.messages.append(f"Repairing {target_id}: {repair_amount:.1f}% damage repaired (Damage: {target_obj.damage:.1f}%)")
            elif target_type == 'starbase':
                # Can only repair friendly starbases at 2% per turn
                if not target_obj.friendly_to_player:
                    self.messages.append(f"Repair error: Cannot repair enemy starbase {target_id}")
                    return
                repair_rate = 2.0
                repair_amount = min(repair_rate, target_obj.damage)
                target_obj.damage = max(0.0, target_obj.damage - repair_amount)
                self.messages.append(f"Repairing starbase {target_id}: {repair_amount:.1f}% damage repaired (Damage: {target_obj.damage:.1f}%)")
        else:
            # Self-repair - only works when stopped
            if ship.propulsion.current_speed != 0.0:
                self.messages.append("Repair error: Ship must be stopped to perform manual repair")
                return
            
            # Manual self-repair at 10% per turn
            repair_rate = 10.0
            repair_amount = min(repair_rate, ship.damage)
            ship.damage = max(0.0, ship.damage - repair_amount)
            # Mark ship as having used manual repair this turn (disables auto-repair)
            ship.manual_repair_this_turn = True
            self.messages.append(f"Self-repair: {repair_amount:.1f}% damage repaired (Damage: {ship.damage:.1f}%)")
    
    def _update_all_objects(self) -> None:
        """Update all game objects."""
        # Update universe objects
        for obj in self.universe_objects.values():
            obj.update()
        
        # Update player ship
        self._update_ship(self.player_ship)
        
        # Update enemy ships
        for enemy in self.enemy_ships.values():
            self._update_ship(enemy)
        
        # Update torpedos
        self._update_torpedos()
    
    def _update_ship(self, ship: Ship) -> None:
        """Update a ship's systems."""
        if ship.is_destroyed or ship.is_disabled:
            return
        
        # Move ship
        ship.move()
        
        # Update energy
        ship.update_energy()
        
        # Update damage
        ship.update_damage_repair()
        
        # Update warp core
        ship.update_warp_core()
        
        # Update phaser charge
        ship.update_phaser_charge()
        
        # Check if disabled
        if ship.crew <= 0:
            ship.is_disabled = True
    
    def _update_torpedos(self) -> None:
        """Update all active torpedos - move them 10 AU/turn toward target."""
        # Update player torpedos
        self._update_torpedos_for_ship(self.player_ship, is_player=True)
        
        # Update enemy torpedos
        for enemy_ship in self.enemy_ships.values():
            self._update_torpedos_for_ship(enemy_ship, is_player=False)
    
    def _update_torpedos_for_ship(self, ship: Ship, is_player: bool) -> None:
        """Update torpedos for a specific ship."""
        active_torpedos = ship.weapons.active_torpedos
        torpedos_to_remove = []
        
        for torpedo in active_torpedos:
            # Calculate direction vector to target
            current_pos = torpedo['current_pos']
            target_pos = torpedo['target_pos']
            
            dx = target_pos.x - current_pos.x
            dy = target_pos.y - current_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Move 10 AU per turn toward target
            if distance > 0:
                # Normalize direction and move
                move_distance = min(10.0, distance)  # Don't overshoot
                move_x = (dx / distance) * move_distance
                move_y = (dy / distance) * move_distance
                
                torpedo['current_pos'] = Position(
                    current_pos.x + move_x,
                    current_pos.y + move_y
                )
                torpedo['distance_traveled'] += move_distance
                
                # Check if torpedo reached target (within 2 AU)
                new_dx = target_pos.x - torpedo['current_pos'].x
                new_dy = target_pos.y - torpedo['current_pos'].y
                new_distance = math.sqrt(new_dx * new_dx + new_dy * new_dy)
                
                if new_distance < 2.0:
                    # Torpedo hit target - find what was hit by proximity
                    torpedos_to_remove.append(torpedo)
                    
                    if is_player:
                        # Player torpedo - check enemy ships first
                        hit_target = None
                        for enemy_id, enemy_ship in self.enemy_ships.items():
                            dist_to_enemy = enemy_ship.position.distance_to(torpedo['current_pos'])
                            if dist_to_enemy < 2.0:
                                hit_target = ('enemy', enemy_id, enemy_ship)
                                break
                        
                        # Check universe objects
                        if not hit_target:
                            for obj_id, obj in self.universe_objects.items():
                                dist_to_obj = obj.position.distance_to(torpedo['current_pos'])
                                if dist_to_obj < 2.0:
                                    hit_target = ('object', obj_id, obj)
                                    break
                        
                        # Apply damage if hit something
                        if hit_target:
                            hit_type, hit_id, hit_obj = hit_target
                            if hit_type == 'enemy':
                                damage = 25.0  # Torpedo damage
                                
                                # Record that player fired upon this enemy
                                hit_obj.fired_upon_by.add(torpedo['source_ship_id'])
                                
                                hit_obj.damage = min(100.0, hit_obj.damage + damage)
                                self.messages.append(f"Torpedo hit {hit_id}! Damage: {damage:.0f}%")
                                
                                # Track torpedo hit
                                self.player_ship.stats['torpedo_hits'] += 1
                                
                                # Check if destroyed
                                if hit_obj.damage >= 100.0:
                                    hit_obj.is_destroyed = True
                                    self.messages.append(f"{hit_id} destroyed!")
                                    
                                    # Handle ship destruction and reputation changes
                                    self._handle_ship_destruction(self.player_ship, hit_obj, hit_id)
                                    
                                    # Transfer cash from destroyed enemy ship
                                    cash_received = hit_obj.cash
                                    self.player_ship.cash += cash_received
                                    self.messages.append(f"Salvaged ${cash_received} from {hit_id}")
                                    
                                    # Track enemy destruction
                                    self.player_ship.stats['enemies_destroyed'] += 1
                                    
                                    # Cancel auto-navigate if this was the target
                                    if self.player_ship.auto_nav_target_id == hit_id:
                                        self.player_ship.auto_nav_target_id = None
                                        self.messages.append(f"Auto-navigation cancelled - target destroyed")
                                    
                                    # Clear weapon lock if this was the locked target
                                    if self.player_ship.weapons.phaser_locked_target == hit_id:
                                        self.player_ship.weapons.phaser_locked_target = None
                                    
                                    # Remove destroyed enemy ship and spawn a replacement
                                    if hit_id in self.enemy_ships:
                                        del self.enemy_ships[hit_id]
                                        self._spawn_single_enemy()
                                        new_enemy_id = list(self.enemy_ships.keys())[-1]
                                        new_enemy = self.enemy_ships[new_enemy_id]
                                        self.messages.append(f"New enemy ship {new_enemy_id} spawned at ({new_enemy.position.x:.0f}, {new_enemy.position.y:.0f})")
                            else:
                                self.messages.append(f"Torpedo impacted {hit_id}")
                        else:
                            self.messages.append("Torpedo target missed")
                    else:
                        # Enemy torpedo - check if hit player or other enemy ships
                        hit_something = False
                        
                        # First check if it hit the player
                        dist_to_player = self.player_ship.position.distance_to(torpedo['current_pos'])
                        if dist_to_player < 2.0:
                            # Hit the player!
                            hit_something = True
                            damage = 10.0  # 10% damage per torpedo hit (as per requirements)
                            
                            # Record that this ship fired upon the player
                            self.player_ship.fired_upon_by.add(torpedo['source_ship_id'])
                            
                            # Apply damage to shields first, then ship
                            if self.player_ship.shields_active and self.player_ship.shields > 0:
                                shield_damage = min(damage, self.player_ship.shields)
                                self.player_ship.shields -= shield_damage
                                remaining_damage = damage - shield_damage
                                
                                if remaining_damage > 0:
                                    self.player_ship.damage = min(100.0, self.player_ship.damage + remaining_damage)
                                    self.messages.append(f"Torpedo hit from {torpedo['source_ship_id']}! Shields absorbed {shield_damage:.1f}%, ship took {remaining_damage:.1f}% damage!")
                                else:
                                    self.messages.append(f"Torpedo hit from {torpedo['source_ship_id']}! Shields absorbed {shield_damage:.1f}% damage!")
                            else:
                                self.player_ship.damage = min(100.0, self.player_ship.damage + damage)
                                self.messages.append(f"Torpedo hit from {torpedo['source_ship_id']}! {damage:.1f}% damage to ship!")
                            
                            # 1% chance to damage warp core (as per requirements)
                            if random.random() < 0.01:
                                self.player_ship.propulsion.warp_core_temp = min(100.0, 
                                    self.player_ship.propulsion.warp_core_temp + 50.0)
                                self.messages.append("CRITICAL: Torpedo struck warp core!")
                            
                            # Check if player destroyed
                            if self.player_ship.damage >= 100.0:
                                self.player_ship.is_destroyed = True
                                self.messages.append("YOUR SHIP HAS BEEN DESTROYED!")
                        
                        # If didn't hit player, check other enemy ships
                        if not hit_something:
                            for enemy_id, enemy_ship in self.enemy_ships.items():
                                if enemy_id != torpedo['source_ship_id']:  # Don't hit yourself
                                    dist_to_enemy = enemy_ship.position.distance_to(torpedo['current_pos'])
                                    if dist_to_enemy < 2.0 and not enemy_ship.is_destroyed:
                                        # Hit another enemy ship!
                                        hit_something = True
                                        damage = 10.0  # 10% damage per torpedo hit
                                        
                                        # Record that this ship fired upon the enemy
                                        enemy_ship.fired_upon_by.add(torpedo['source_ship_id'])
                                        
                                        # Apply damage to shields first, then ship
                                        if enemy_ship.shields_active and enemy_ship.shields > 0:
                                            shield_damage = min(damage, enemy_ship.shields)
                                            enemy_ship.shields -= shield_damage
                                            remaining_damage = damage - shield_damage
                                            
                                            if remaining_damage > 0:
                                                enemy_ship.damage = min(100.0, enemy_ship.damage + remaining_damage)
                                                self.messages.append(f"{torpedo['source_ship_id']} torpedo hit {enemy_id}! {remaining_damage:.1f}% damage!")
                                            else:
                                                self.messages.append(f"{torpedo['source_ship_id']} torpedo hit {enemy_id}'s shields for {shield_damage:.1f}%!")
                                        else:
                                            enemy_ship.damage = min(100.0, enemy_ship.damage + damage)
                                            self.messages.append(f"{torpedo['source_ship_id']} torpedo hit {enemy_id}! {damage:.1f}% damage!")
                                        
                                        # 1% chance to damage warp core
                                        if random.random() < 0.01:
                                            enemy_ship.propulsion.warp_core_temp = min(100.0,
                                                enemy_ship.propulsion.warp_core_temp + 50.0)
                                            self.messages.append(f"CRITICAL: {enemy_id}'s warp core damaged!")
                                        
                                        # Check if destroyed
                                        if enemy_ship.damage >= 100.0:
                                            enemy_ship.is_destroyed = True
                                            self.messages.append(f"{enemy_id} destroyed by {torpedo['source_ship_id']}!")
                                            
                                            # Clear weapon lock if this was the locked target
                                            if self.player_ship.weapons.phaser_locked_target == enemy_id:
                                                self.player_ship.weapons.phaser_locked_target = None
                                            
                                            # Remove destroyed ship and spawn replacement
                                            if enemy_id in self.enemy_ships:
                                                del self.enemy_ships[enemy_id]
                                                self._spawn_single_enemy()
                                                new_enemy_id = list(self.enemy_ships.keys())[-1]
                                                new_enemy = self.enemy_ships[new_enemy_id]
                                                self.messages.append(f"New enemy ship {new_enemy_id} spawned at ({new_enemy.position.x:.0f}, {new_enemy.position.y:.0f})")
                                        
                                        break  # Only hit one ship
                        
                        if not hit_something:
                            # Missed everything
                            self.messages.append(f"{torpedo['source_ship_id']} torpedo missed")
            else:
                # Already at target
                torpedos_to_remove.append(torpedo)
        
        # Remove torpedos that hit or expired
        for torpedo in torpedos_to_remove:
            if torpedo in active_torpedos:
                active_torpedos.remove(torpedo)
    
    def _check_collisions(self) -> None:
        """Check for collisions and special interactions."""
        # Check stars for refueling
        for star in [obj for obj in self.universe_objects.values() if isinstance(obj, Star)]:
            if self.player_ship.position.distance_to(star.position) < 1.0:
                self.player_ship.energy = min(100.0, self.player_ship.energy + 10.0)
        
        # Check asteroid fields for mining
        for asteroid_field in [obj for obj in self.universe_objects.values() if isinstance(obj, AsteroidField)]:
            if self.player_ship.position.distance_to(asteroid_field.position) < 1.0:
                mined = random.randint(0, 1000)
                self.player_ship.cash += mined
                if mined > 0:
                    self.messages.append(f"Mined ${mined}")
        
        # Check starbases for docking services
        self._check_starbase_docking()
    
    def _check_starbase_docking(self) -> None:
        """Check if player ship is docked at friendly starbase and provide services."""
        docked_starbase = None
        
        # Find friendly starbase within 1 AU
        for obj_id, obj in self.universe_objects.items():
            if isinstance(obj, Starbase) and obj.friendly_to_player:
                if self.player_ship.position.distance_to(obj.position) < 1.0:
                    docked_starbase = obj
                    self.player_ship.is_docked_with = obj_id
                    break
        
        # If docked, provide services
        if docked_starbase:
            repairs_done = 0.0
            torpedos_purchased = 0
            fuel_loaded = 0.0
            cost = 0
            
            # Repair damage (can repair up to 25%)
            if self.player_ship.damage > 0 and self.player_ship.cash >= 1:
                repair_amount = min(25.0, self.player_ship.damage)
                self.player_ship.damage -= repair_amount
                repairs_done = repair_amount
            
            # Replenish torpedos (up to 25% of max)
            if self.player_ship.weapons.torpedos < self.player_ship.weapons.max_torpedos:
                torpedos_can_buy = self.player_ship.weapons.max_torpedos // 4  # 25%
                torpedos_needed = torpedos_can_buy - self.player_ship.weapons.torpedos
                torpedo_cost = min(torpedos_needed, self.player_ship.cash // 50)  # $50 per torpedo
                
                if torpedo_cost > 0:
                    self.player_ship.weapons.torpedos += torpedo_cost
                    torpedos_purchased = torpedo_cost
                    cost += torpedo_cost * 50
                    self.player_ship.cash -= cost
            
            # Refuel (up to 10%)
            if self.player_ship.energy < 100.0:
                fuel_to_load = min(10.0, 100.0 - self.player_ship.energy)
                self.player_ship.energy += fuel_to_load
                fuel_loaded = fuel_to_load
                # Starbase energy drain is 1% per turn per refueling ship
                docked_starbase.energy = max(0.0, docked_starbase.energy - 1.0)
            
            # Send docking message if any services were used
            if repairs_done > 0 or torpedos_purchased > 0 or fuel_loaded > 0:
                message = f"Docked at {docked_starbase.id}:"
                if repairs_done > 0:
                    message += f" Repaired {repairs_done:.1f}%"
                if torpedos_purchased > 0:
                    message += f" Purchased {torpedos_purchased} torpedos"
                if fuel_loaded > 0:
                    message += f" Loaded {fuel_loaded:.1f}% fuel"
                if cost > 0:
                    message += f" Cost: ${cost}"
                self.messages.append(message)
        else:
            # Clear docking status if not near friendly starbase
            if self.player_ship.is_docked_with:
                self.player_ship.is_docked_with = None
    
    def _check_black_hole_destruction(self) -> None:
        """Check if ships are destroyed by black holes."""
        for bh in [obj for obj in self.universe_objects.values() if isinstance(obj, BlackHole)]:
            # Check player ship
            if self.player_ship.position.distance_to(bh.position) < 3.0:
                self.player_ship.is_destroyed = True
                self.messages.append("SHIP DESTROYED: Captured by black hole!")
            
            # Check enemy ships
            for enemy_id, enemy in list(self.enemy_ships.items()):
                if enemy.position.distance_to(bh.position) < 3.0:
                    enemy.is_destroyed = True
                    # Clear weapon lock if this was the locked target
                    if self.player_ship.weapons.phaser_locked_target == enemy_id:
                        self.player_ship.weapons.phaser_locked_target = None
    
    def _check_game_over(self) -> None:
        """Check win/loss conditions."""
        if self.player_ship.is_destroyed:
            self.game_over = True
            self.game_over_reason = "Your ship was destroyed!"
        elif self.player_ship.is_disabled:
            self.game_over = True
            self.game_over_reason = "Your ship is disabled - no crew remaining!"
