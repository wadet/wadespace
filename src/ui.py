"""
Wade Space Game - Rebuilt Pygame UI System

Complete graphical interface with:
- Left half: 20x20 AU 2D map with player-centered view
- Right half divided into thirds:
  - Top third: Ship status (left) + Minimap (right)
  - Middle third: Message area
  - Bottom third: Command prompt
"""

import pygame
import math
import sys
from typing import Optional, Tuple, List, Dict
from src.game_engine import GameEngine
from src.command_parser import CommandParser
from src.universe_objects import Star, Planet, BlackHole, Pulsar, WormHole, Starbase, AsteroidField


class Colors:
    """Color palette for the game UI."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DARK_GRAY = (40, 40, 40)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    
    # Status colors
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    
    # Specific UI colors
    HEALTHY = (0, 220, 0)
    WARNING = (255, 200, 0)
    DANGER = (255, 50, 50)
    BORDER = (100, 100, 100)


class GameUI:
    """Main UI system for Wade Space using Pygame."""
    
    FONT_SIZE = 30
    VIEWPORT_SIZE = 20.0  # AU visible on main map
    MINIMAP_BASE_SIZE = 500.0  # AU visible on minimap (before zoom)
    MAX_ZOOM_ADJUSTMENT = 300.0  # AU zoom range
    
    # Symbol sizes in pixels
    SYMBOL_SIZE = 12
    
    def __init__(self, game_engine: GameEngine):
        """Initialize the UI system."""
        pygame.init()
        
        self.engine = game_engine
        self.parser = CommandParser()
        
        # Detect screen resolution
        info = pygame.display.get_surface()
        if info is None:
            pygame.display.set_mode((1, 1))
        
        try:
            info = pygame.display.get_info()
            max_width = info.current_w
            max_height = info.current_h
        except (AttributeError, pygame.error):
            max_width = 1920
            max_height = 1080
        
        # Set window to 2/3 of max resolution
        self.screen_width = int(max_width * 0.66)
        self.screen_height = int(max_height * 0.66)
        
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Wade Space")
        
        # Font setup
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        self.font_small = pygame.font.Font(None, self.FONT_SIZE - 2)
        self.font_title = pygame.font.Font(None, self.FONT_SIZE + 4)
        
        # Layout calculations
        self._calculate_layout()
        
        # UI state
        self.messages = []
        self.command_history = []
        self.history_index = -1
        self.current_input = ""
        self.minimap_zoom_offset = 0.0  # 0 = 500 AU base, ±300 AU max adjustment
        self.mouse_pos = (0, 0)  # Track mouse position for hover effects
        self.minimap_objects = []  # Store (screen_x, screen_y, obj_id, radius) for click detection
        self.nav_target_id = None  # Track object being navigated to for yellow circle
        self.running = True
        self.clock = pygame.time.Clock()
        
    def _calculate_layout(self):
        """Calculate UI layout based on screen size."""
        # Left half: 2D map
        self.map_area_width = self.screen_width // 2
        self.map_area_height = self.screen_height
        self.map_rect = pygame.Rect(0, 0, self.map_area_width, self.map_area_height)
        
        # Right half: divided into thirds
        self.right_width = self.screen_width - self.map_area_width
        self.third_height = self.screen_height // 3
        
        # Top third: Status panel (left) + Minimap (right)
        self.status_area_width = self.right_width // 2
        self.status_area_height = self.third_height
        self.status_rect = pygame.Rect(
            self.map_area_width, 0,
            self.status_area_width, self.status_area_height
        )
        
        self.minimap_area_width = self.right_width - self.status_area_width
        self.minimap_area_height = self.third_height
        self.minimap_rect = pygame.Rect(
            self.map_area_width + self.status_area_width, 0,
            self.minimap_area_width, self.minimap_area_height
        )
        
        # Middle third: Message area
        self.message_area_width = self.right_width
        self.message_area_height = self.third_height
        self.message_rect = pygame.Rect(
            self.map_area_width, self.third_height,
            self.message_area_width, self.message_area_height
        )
        
        # Bottom third: Command prompt
        self.command_area_width = self.right_width
        self.command_area_height = self.third_height
        self.command_rect = pygame.Rect(
            self.map_area_width, self.third_height * 2,
            self.command_area_width, self.command_area_height
        )
    
    def add_message(self, message: str):
        """Add a message to the message log."""
        self.messages.append(message)
        # Keep only last 50 messages
        if len(self.messages) > 50:
            self.messages.pop(0)
    
    def _draw_border(self, rect: pygame.Rect, color: Tuple[int, int, int] = Colors.BORDER):
        """Draw a border around a rectangle."""
        pygame.draw.rect(self.screen, color, rect, 2)
    
    def _draw_2d_map(self):
        """Draw the 2D map showing 20x20 AU around player."""
        # Fill background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, self.map_rect)
        
        # Draw grid (optional, for reference)
        self._draw_map_grid()
        
        # Draw universe objects
        player_pos = self.engine.player_ship.position
        
        # Get all objects in range
        nearby_objects = self.engine.get_objects_in_range(
            player_pos, self.VIEWPORT_SIZE / 2
        )
        
        # Draw objects
        for obj_tuple in nearby_objects:
            obj = obj_tuple[1]  # Extract object from (id, obj, distance) tuple
            self._draw_map_object(obj, player_pos)
        
        # Draw enemy ships
        for enemy_id, enemy_ship in self.engine.enemy_ships.items():
            rel_x = enemy_ship.position.x - player_pos.x
            rel_y = enemy_ship.position.y - player_pos.y
            
            # Check if enemy is in viewport
            if abs(rel_x) <= self.VIEWPORT_SIZE / 2 and abs(rel_y) <= self.VIEWPORT_SIZE / 2:
                pixels_per_au_x = self.map_area_width / self.VIEWPORT_SIZE
                pixels_per_au_y = self.map_area_height / self.VIEWPORT_SIZE
                
                screen_x = self.map_rect.centerx + rel_x * pixels_per_au_x
                screen_y = self.map_rect.centery + rel_y * pixels_per_au_y
                
                # Draw enemy ship as Klingon Bird of Prey (top-down view)
                # Circular bridge/command pod at front
                bridge_radius = 4
                pygame.draw.circle(self.screen, Colors.RED, (int(screen_x), int(screen_y - 6)), bridge_radius)
                pygame.draw.circle(self.screen, (139, 0, 0), (int(screen_x), int(screen_y - 6)), bridge_radius, 1)
                
                # Thin neck connecting bridge to rear
                neck = pygame.Rect(screen_x - 1.5, screen_y - 2, 3, 8)
                pygame.draw.rect(self.screen, Colors.RED, neck)
                pygame.draw.rect(self.screen, (139, 0, 0), neck, 1)
                
                # Rear engineering section (small triangle)
                rear_section = [
                    (screen_x - 3, screen_y + 6),
                    (screen_x + 3, screen_y + 6),
                    (screen_x, screen_y + 10),
                ]
                pygame.draw.polygon(self.screen, Colors.RED, rear_section)
                pygame.draw.polygon(self.screen, (139, 0, 0), rear_section, 1)
                
                # Wing extensions (Bird of Prey style)
                # Left wing - swept back
                left_wing = [
                    (screen_x - 2, screen_y - 2),
                    (screen_x - 10, screen_y - 7),
                    (screen_x - 10, screen_y + 3),
                    (screen_x - 3, screen_y + 4),
                ]
                pygame.draw.polygon(self.screen, Colors.RED, left_wing)
                pygame.draw.polygon(self.screen, (139, 0, 0), left_wing, 1)
                
                # Right wing - swept back
                right_wing = [
                    (screen_x + 2, screen_y - 2),
                    (screen_x + 10, screen_y - 7),
                    (screen_x + 10, screen_y + 3),
                    (screen_x + 3, screen_y + 4),
                ]
                pygame.draw.polygon(self.screen, Colors.RED, right_wing)
                pygame.draw.polygon(self.screen, (139, 0, 0), right_wing, 1)
                
                # Draw enemy label with info
                label = f"{enemy_id}"
                if hasattr(enemy_ship, 'energy'):
                    label += f" E:{enemy_ship.energy:.0f}%"
                if hasattr(enemy_ship, 'shields'):
                    label += f" S:{enemy_ship.shields:.0f}%"
                
                text_surface = self.font_small.render(label, True, Colors.RED)
                self.screen.blit(text_surface, (screen_x + 15, screen_y - 5))
        
        # Draw active torpedos from player ship
        for torpedo in self.engine.player_ship.weapons.active_torpedos:
            rel_x = torpedo['current_pos'].x - player_pos.x
            rel_y = torpedo['current_pos'].y - player_pos.y
            
            # Check if torpedo is in viewport
            if abs(rel_x) <= self.VIEWPORT_SIZE / 2 and abs(rel_y) <= self.VIEWPORT_SIZE / 2:
                pixels_per_au_x = self.map_area_width / self.VIEWPORT_SIZE
                pixels_per_au_y = self.map_area_height / self.VIEWPORT_SIZE
                
                screen_x = self.map_rect.centerx + rel_x * pixels_per_au_x
                screen_y = self.map_rect.centery + rel_y * pixels_per_au_y
                
                # Draw torpedo as small green circle (matching player ship color)
                torpedo_radius = 2
                pygame.draw.circle(self.screen, Colors.GREEN, (int(screen_x), int(screen_y)), torpedo_radius)
                pygame.draw.circle(self.screen, Colors.GREEN, (int(screen_x), int(screen_y)), torpedo_radius, 1)
        
        # Draw active torpedos from enemy ships
        for enemy_id, enemy_ship in self.engine.enemy_ships.items():
            for torpedo in enemy_ship.weapons.active_torpedos:
                rel_x = torpedo['current_pos'].x - player_pos.x
                rel_y = torpedo['current_pos'].y - player_pos.y
                
                # Check if torpedo is in viewport
                if abs(rel_x) <= self.VIEWPORT_SIZE / 2 and abs(rel_y) <= self.VIEWPORT_SIZE / 2:
                    pixels_per_au_x = self.map_area_width / self.VIEWPORT_SIZE
                    pixels_per_au_y = self.map_area_height / self.VIEWPORT_SIZE
                    
                    screen_x = self.map_rect.centerx + rel_x * pixels_per_au_x
                    screen_y = self.map_rect.centery + rel_y * pixels_per_au_y
                    
                    # Draw torpedo as small red circle (matching enemy ship color)
                    torpedo_radius = 2
                    pygame.draw.circle(self.screen, Colors.RED, (int(screen_x), int(screen_y)), torpedo_radius)
                    pygame.draw.circle(self.screen, Colors.RED, (int(screen_x), int(screen_y)), torpedo_radius, 1)
        
        # Draw player ship at center
        center_x = self.map_rect.centerx
        center_y = self.map_rect.centery
        self._draw_player_ship(center_x, center_y)
        
        # Draw border
        self._draw_border(self.map_rect)
    
    def _draw_map_grid(self):
        """Draw optional grid on map for reference."""
        grid_spacing = (self.VIEWPORT_SIZE / 4)  # Show 5x5 grid
        pixels_per_au = self.map_area_width / self.VIEWPORT_SIZE
        
        for i in range(5):
            # Vertical lines
            x = self.map_rect.left + i * (self.map_area_width // 4)
            pygame.draw.line(
                self.screen, Colors.GRAY,
                (x, self.map_rect.top),
                (x, self.map_rect.bottom), 1
            )
            # Horizontal lines
            y = self.map_rect.top + i * (self.map_area_height // 4)
            pygame.draw.line(
                self.screen, Colors.GRAY,
                (self.map_rect.left, y),
                (self.map_rect.right, y), 1
            )
    
    def _draw_map_object(self, obj, player_pos):
        """Draw a single object on the map."""
        # Calculate relative position
        rel_x = obj.position.x - player_pos.x
        rel_y = obj.position.y - player_pos.y
        
        # Convert AU to pixels
        pixels_per_au = self.map_area_width / self.VIEWPORT_SIZE
        screen_x = self.map_rect.centerx + rel_x * pixels_per_au
        screen_y = self.map_rect.centery + rel_y * pixels_per_au
        
        # Only draw if on screen
        if not (self.map_rect.left <= screen_x <= self.map_rect.right and
                self.map_rect.top <= screen_y <= self.map_rect.bottom):
            return
        
        # Draw object with visual representation
        self._draw_object_visual(obj, screen_x, screen_y)
        
        # Draw label with info
        label = f"{obj.id}"
        if hasattr(obj, 'energy'):
            label += f" E:{obj.energy:.0f}%"
        if hasattr(obj, 'shields'):
            label += f" S:{obj.shields:.0f}%"
        
        text_surface = self.font_small.render(label, True, Colors.WHITE)
        self.screen.blit(text_surface, (screen_x + 15, screen_y - 5))
    
    def _get_object_symbol_and_color(self, obj) -> Tuple[str, Tuple[int, int, int]]:
        """Get symbol and color for an object."""
        if isinstance(obj, Star):
            return "★", Colors.YELLOW
        elif isinstance(obj, Planet):
            return "●", Colors.CYAN
        elif isinstance(obj, BlackHole):
            return "⊗", Colors.BLACK
        elif isinstance(obj, Pulsar):
            return "◇", Colors.MAGENTA
        elif isinstance(obj, WormHole):
            return "◎", Colors.CYAN
        elif isinstance(obj, Starbase):
            # Friendly or enemy based on some flag
            return "⊕", Colors.GREEN
        elif isinstance(obj, AsteroidField):
            return "✕", Colors.GRAY
        else:
            return "•", Colors.WHITE
    
    def _draw_object_visual(self, obj, x: float, y: float):
        """Draw a visual representation of an object on the map."""
        if isinstance(obj, Star):
            # Draw star as yellow circle with spikes
            pygame.draw.circle(self.screen, Colors.YELLOW, (int(x), int(y)), 6)
            # Draw spikes
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                import math
                rad = math.radians(angle)
                x1 = x + 8 * math.cos(rad)
                y1 = y + 8 * math.sin(rad)
                pygame.draw.line(self.screen, Colors.YELLOW, (int(x), int(y)), (int(x1), int(y1)), 1)
        
        elif isinstance(obj, Planet):
            # Draw planet as blue/cyan circle
            inhabited = getattr(obj, 'is_inhabited', False)
            color = Colors.CYAN if inhabited else Colors.BLUE
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 5)
            pygame.draw.circle(self.screen, Colors.LIGHT_GRAY, (int(x), int(y)), 5, 1)
        
        elif isinstance(obj, BlackHole):
            # Draw black hole as black circle with concentric rings
            pygame.draw.circle(self.screen, Colors.BLACK, (int(x), int(y)), 6)
            pygame.draw.circle(self.screen, Colors.ORANGE, (int(x), int(y)), 6, 1)
            pygame.draw.circle(self.screen, Colors.ORANGE, (int(x), int(y)), 4, 1)
        
        elif isinstance(obj, Pulsar):
            # Draw pulsar as rotating diamond
            size = 5
            points = [
                (x, y - size),
                (x + size, y),
                (x, y + size),
                (x - size, y),
            ]
            pygame.draw.polygon(self.screen, Colors.MAGENTA, points)
            pygame.draw.polygon(self.screen, Colors.LIGHT_GRAY, points, 1)
        
        elif isinstance(obj, WormHole):
            # Draw wormhole as concentric circles (portal effect)
            pygame.draw.circle(self.screen, Colors.CYAN, (int(x), int(y)), 6)
            pygame.draw.circle(self.screen, Colors.MAGENTA, (int(x), int(y)), 4, 1)
            pygame.draw.circle(self.screen, Colors.CYAN, (int(x), int(y)), 2)
        
        elif isinstance(obj, Starbase):
            # Draw starbase as green/red square or hexagon
            color = Colors.GREEN if getattr(obj, 'friendly_to_player', True) else Colors.RED
            size = 6
            pygame.draw.rect(self.screen, color, (int(x) - size, int(y) - size, size * 2, size * 2))
            pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (int(x) - size, int(y) - size, size * 2, size * 2), 1)
        
        elif isinstance(obj, AsteroidField):
            # Draw asteroid field as cluster of brown dots
            import random
            random.seed(hash(obj.id) % 2**32)  # Deterministic based on ID
            for _ in range(3):
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)
                pygame.draw.circle(self.screen, Colors.ORANGE, (int(x + offset_x), int(y + offset_y)), 2)
        
        else:
            # Default: draw as white circle
            pygame.draw.circle(self.screen, Colors.WHITE, (int(x), int(y)), 4)
    
    def _draw_symbol(self, x: float, y: float, symbol: str, color: Tuple[int, int, int]):
        """Draw a symbol at the given screen coordinates."""
        text_surface = self.font.render(symbol, True, color)
        rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, rect)
    
    def _draw_object_visual_small(self, obj, x: float, y: float):
        """Draw a small visual representation of an object for the minimap."""
        if isinstance(obj, Star):
            # Draw star as small yellow circle
            pygame.draw.circle(self.screen, Colors.YELLOW, (int(x), int(y)), 3)
        
        elif isinstance(obj, Planet):
            # Draw planet as small blue circle
            color = Colors.CYAN if getattr(obj, 'is_inhabited', False) else Colors.BLUE
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 2)
        
        elif isinstance(obj, BlackHole):
            # Draw black hole as small black circle with orange ring
            pygame.draw.circle(self.screen, Colors.BLACK, (int(x), int(y)), 3)
            pygame.draw.circle(self.screen, Colors.ORANGE, (int(x), int(y)), 3, 1)
        
        elif isinstance(obj, Pulsar):
            # Draw pulsar as small magenta diamond
            size = 2
            points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
            pygame.draw.polygon(self.screen, Colors.MAGENTA, points)
        
        elif isinstance(obj, WormHole):
            # Draw wormhole as small concentric circles
            pygame.draw.circle(self.screen, Colors.CYAN, (int(x), int(y)), 3)
            pygame.draw.circle(self.screen, Colors.MAGENTA, (int(x), int(y)), 1)
        
        elif isinstance(obj, Starbase):
            # Draw starbase as small colored square
            color = Colors.GREEN if getattr(obj, 'friendly_to_player', True) else Colors.RED
            pygame.draw.rect(self.screen, color, (int(x) - 2, int(y) - 2, 4, 4))
        
        elif isinstance(obj, AsteroidField):
            # Draw asteroid field as small brown dot
            pygame.draw.circle(self.screen, Colors.ORANGE, (int(x), int(y)), 2)
        
        else:
            # Default: draw as small white circle
            pygame.draw.circle(self.screen, Colors.WHITE, (int(x), int(y)), 2)
    
    def _draw_player_ship(self, x: float, y: float):
        """Draw the player's ship at the center - USS Enterprise top-down view."""
        # Draw the iconic Enterprise shape from top-down view
        
        # Saucer section (primary hull) - circular front
        saucer_radius = 8
        pygame.draw.circle(self.screen, Colors.GREEN, (int(x), int(y - 2)), saucer_radius)
        pygame.draw.circle(self.screen, Colors.LIGHT_GRAY, (int(x), int(y - 2)), saucer_radius, 1)
        
        # Secondary hull (engineering section) - elongated rectangle
        secondary_hull = pygame.Rect(x - 3, y + 3, 6, 10)
        pygame.draw.rect(self.screen, Colors.GREEN, secondary_hull)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, secondary_hull, 1)
        
        # Warp nacelles (port and starboard)
        nacelle_width = 3
        nacelle_height = 14
        
        # Port nacelle (left)
        left_nacelle = pygame.Rect(x - 12, y, nacelle_width, nacelle_height)
        pygame.draw.rect(self.screen, Colors.GREEN, left_nacelle)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, left_nacelle, 1)
        
        # Starboard nacelle (right)
        right_nacelle = pygame.Rect(x + 9, y, nacelle_width, nacelle_height)
        pygame.draw.rect(self.screen, Colors.GREEN, right_nacelle)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, right_nacelle, 1)
        
        # Connecting struts (pylons) from saucer to nacelles
        # Left pylon
        pygame.draw.line(self.screen, Colors.LIGHT_GRAY, (x - 6, y + 2), (x - 10, y + 3), 2)
        # Right pylon
        pygame.draw.line(self.screen, Colors.LIGHT_GRAY, (x + 6, y + 2), (x + 10, y + 3), 2)
        
        # Draw player ship label
        ship = self.engine.player_ship
        label = f"{ship.id}"
        if hasattr(ship, 'energy'):
            label += f" E:{ship.energy:.0f}%"
        if hasattr(ship, 'shields'):
            label += f" S:{ship.shields:.0f}%"
        
        text_surface = self.font_small.render(label, True, Colors.GREEN)
        self.screen.blit(text_surface, (x + 15, y - 5))
    
    def _draw_status_panel(self):
        """Draw the ship status panel."""
        # Fill background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, self.status_rect)
        
        # Get ship data
        ship = self.engine.player_ship
        
        # Draw title
        title = self.font_title.render(f"Ship {ship.id}", True, Colors.CYAN)
        self.screen.blit(title, (self.status_rect.left + 10, self.status_rect.top + 10))
        
        # Draw vital statistics as horizontal bars
        bar_height = 12
        start_y = self.status_rect.top + 50
        spacing = 26
        
        # Calculate label width based on longest label
        longest_label = max(["Energy", "Shields", "Damage", "Warp Core"], key=len)
        label_width = self.font_small.render(longest_label, True, Colors.WHITE).get_width()
        
        # Calculate total width available for the bar row (accounting for padding)
        total_bar_width = self.status_area_width - 20  # 10px padding on each side
        
        vitals = [
            ("Energy", ship.energy, Colors.CYAN),
            ("Shields", ship.shields, Colors.BLUE),
            ("Damage", 100 - ship.damage, Colors.GREEN),
            ("Warp Core", ship.propulsion.warp_core_temp, Colors.RED),
        ]
        
        for i, (label, value, color) in enumerate(vitals):
            y = start_y + i * spacing
            self._draw_status_bar(
                self.status_rect.left + 10, y,
                label, value, label_width, bar_height, color, total_bar_width
            )
        
        # Draw other vitals as text
        text_y = start_y + len(vitals) * spacing + 15
        other_vitals = [
            f"Crew: {ship.crew}",
            f"Cash: ${ship.cash}",
            f"Torpedos: {ship.weapons.torpedos}",
            f"Speed: {ship.propulsion.current_speed:.1f} AU/turn",
            f"Heading: {ship.propulsion.current_heading:.0f}°",
        ]
        
        for i, vital_text in enumerate(other_vitals):
            text = self.font_small.render(vital_text, True, Colors.WHITE)
            self.screen.blit(text, (self.status_rect.left + 10, text_y + i * 18))
        
        # Draw auto-navigation status if active
        status_line_count = 0
        if ship.auto_nav_target_id:
            # Calculate distance to target
            target_obj = self.engine.universe_objects.get(ship.auto_nav_target_id)
            if not target_obj:
                target_obj = self.engine.enemy_ships.get(ship.auto_nav_target_id)
            
            if target_obj:
                distance = ship.position.distance_to(target_obj.position)
                nav_text = f"Navigating to: {ship.auto_nav_target_id}  ({distance:.2f} AU)"
            else:
                nav_text = f"Navigating to: {ship.auto_nav_target_id}"
            
            text = self.font_small.render(nav_text, True, Colors.YELLOW)
            self.screen.blit(text, (self.status_rect.left + 10, text_y + len(other_vitals) * 18 + status_line_count * 18))
            status_line_count += 1
        
        # Draw weapon lock status if active
        if ship.weapons.phaser_locked_target:
            lock_text = f"Locked on: {ship.weapons.phaser_locked_target}"
            text = self.font_small.render(lock_text, True, Colors.RED)
            self.screen.blit(text, (self.status_rect.left + 10, text_y + len(other_vitals) * 18 + status_line_count * 18))
            status_line_count += 1
        
        # Draw game statistics
        stats_y = text_y + len(other_vitals) * 18 + 15
        # Add extra spacing for status lines
        if status_line_count > 0:
            stats_y += status_line_count * 18
        stats_title = self.font_small.render("Game Statistics", True, Colors.YELLOW)
        self.screen.blit(stats_title, (self.status_rect.left + 10, stats_y))
        
        game_stats = [
            f"Enemies Destroyed: {ship.stats['enemies_destroyed']}",
            f"Phasers Fired: {ship.stats['phasers_fired']}",
            f"Torpedos Fired: {ship.stats['torpedos_fired']}",
            f"Torpedo Hits: {ship.stats['torpedo_hits']}",
        ]
        
        for i, stat_text in enumerate(game_stats):
            text = self.font_small.render(stat_text, True, Colors.WHITE)
            self.screen.blit(text, (self.status_rect.left + 10, stats_y + (i + 1) * 18))
        
        # Draw border
        self._draw_border(self.status_rect)
    
    def _draw_status_bar(self, x: float, y: float, label: str, value: float,
                        label_width: float, bar_height: float, color: Tuple[int, int, int],
                        total_width: float):
        """Draw a single status bar with label, bar, and percentage."""
        # Draw label
        label_text = self.font_small.render(label, True, Colors.WHITE)
        self.screen.blit(label_text, (x, y))
        
        # Draw percentage text first to know its width
        percent_text = self.font_small.render(f"{value:.0f}%", True, Colors.WHITE)
        percent_width = percent_text.get_width()
        
        # Calculate bar position and width
        # Bar goes after label with 5px padding, and ends 5px before percentage
        bar_x = x + label_width + 5
        bar_end_x = x + total_width - percent_width - 5
        bar_width = max(50, bar_end_x - bar_x)  # Minimum bar width of 50px
        
        # Draw background bar
        pygame.draw.rect(self.screen, Colors.GRAY, (bar_x, y, bar_width, bar_height))
        
        # Draw fill bar
        fill_width = (value / 100.0) * bar_width
        pygame.draw.rect(self.screen, color, (bar_x, y, fill_width, bar_height))
        
        # Draw border
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (bar_x, y, bar_width, bar_height), 1)
        
        # Draw percentage text
        self.screen.blit(percent_text, (bar_end_x + 5, y))
    
    def _draw_minimap(self):
        """Draw the minimap showing 500x500 AU (with zoom adjustment)."""
        # Fill background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, self.minimap_rect)
        
        # Calculate visible AU range based on zoom
        visible_au = self.MINIMAP_BASE_SIZE + self.minimap_zoom_offset
        player_pos = self.engine.player_ship.position
        
        # Draw minimap title
        title = self.font.render("MINIMAP", True, Colors.CYAN)
        self.screen.blit(title, (self.minimap_rect.left + 10, self.minimap_rect.top + 5))
        
        # Get all objects in minimap range
        nearby_objects = self.engine.get_objects_in_range(
            player_pos, visible_au / 2
        )
        
        # Calculate pixels per AU
        pixels_per_au_x = self.minimap_area_width / visible_au
        pixels_per_au_y = self.minimap_area_height / visible_au
        
        # Track hovered object and clickable objects
        hovered_object = None
        hovered_position = None
        hover_radius = 8  # Pixels around object to detect hover
        self.minimap_objects = []  # Clear previous frame's objects
        
        # Draw objects
        positions_and_sizes = []
        for obj_tuple in nearby_objects:
            obj = obj_tuple[1]  # Extract object from (id, obj, distance) tuple
            rel_x = obj.position.x - player_pos.x
            rel_y = obj.position.y - player_pos.y
            
            screen_x = self.minimap_rect.centerx + rel_x * pixels_per_au_x
            screen_y = self.minimap_rect.centery + rel_y * pixels_per_au_y
            
            if (self.minimap_rect.left <= screen_x <= self.minimap_rect.right and
                self.minimap_rect.top <= screen_y <= self.minimap_rect.bottom):
                # Draw minimap object (smaller version)
                self._draw_object_visual_small(obj, screen_x, screen_y)
                
                # Draw yellow circle if this is the navigation target
                if self.nav_target_id == obj.id:
                    pygame.draw.circle(self.screen, Colors.YELLOW, (int(screen_x), int(screen_y)), 10, 2)
                
                # Store for click detection
                self.minimap_objects.append((screen_x, screen_y, obj.id, hover_radius))
                
                # Check if mouse is hovering over this object
                mouse_x, mouse_y = self.mouse_pos
                distance_to_mouse = ((screen_x - mouse_x) ** 2 + (screen_y - mouse_y) ** 2) ** 0.5
                if distance_to_mouse <= hover_radius:
                    hovered_object = obj
                    hovered_position = (screen_x, screen_y)
                
                # Store for label positioning
                positions_and_sizes.append((screen_x, screen_y, obj.id))
        
        # Draw enemy ships on minimap
        for enemy_id, enemy_ship in self.engine.enemy_ships.items():
            rel_x = enemy_ship.position.x - player_pos.x
            rel_y = enemy_ship.position.y - player_pos.y
            
            screen_x = self.minimap_rect.centerx + rel_x * pixels_per_au_x
            screen_y = self.minimap_rect.centery + rel_y * pixels_per_au_y
            
            if (self.minimap_rect.left <= screen_x <= self.minimap_rect.right and
                self.minimap_rect.top <= screen_y <= self.minimap_rect.bottom):
                # Draw enemy ship as red triangle (same size as player ship)
                size = 5
                points = [
                    (screen_x, screen_y - size),  # Top point
                    (screen_x + size, screen_y + size),  # Bottom right
                    (screen_x - size, screen_y + size)  # Bottom left
                ]
                pygame.draw.polygon(self.screen, Colors.RED, points)
                
                # Draw yellow circle if this is the navigation target
                if self.nav_target_id == enemy_id:
                    pygame.draw.circle(self.screen, Colors.YELLOW, (int(screen_x), int(screen_y)), 10, 2)
                
                # Store for click detection
                self.minimap_objects.append((screen_x, screen_y, enemy_id, hover_radius))
                
                # Check if mouse is hovering over this enemy ship
                mouse_x, mouse_y = self.mouse_pos
                distance_to_mouse = ((screen_x - mouse_x) ** 2 + (screen_y - mouse_y) ** 2) ** 0.5
                if distance_to_mouse <= hover_radius:
                    hovered_object = enemy_ship
                    hovered_object.id = enemy_id  # Ensure enemy has ID for display
                    hovered_position = (screen_x, screen_y)
        
        # Draw player ship as green triangle at center
        player_size = 5
        player_points = [
            (self.minimap_rect.centerx, self.minimap_rect.centery - player_size),  # Top point
            (self.minimap_rect.centerx + player_size, self.minimap_rect.centery + player_size),  # Bottom right
            (self.minimap_rect.centerx - player_size, self.minimap_rect.centery + player_size)  # Bottom left
        ]
        pygame.draw.polygon(self.screen, Colors.GREEN, player_points)
        pygame.draw.polygon(self.screen, Colors.LIGHT_GRAY, player_points, 1)  # Outline
        
        # Draw zoom level info
        zoom_text = self.font_small.render(
            f"Range: {visible_au:.0f} AU",
            True, Colors.WHITE
        )
        self.screen.blit(zoom_text, (self.minimap_rect.left + 10, self.minimap_rect.top + 30))
        
        # Draw hover label if an object is being hovered over
        if hovered_object and hovered_position:
            hover_x, hover_y = hovered_position
            hover_label = hovered_object.id
            hover_text = self.font_small.render(hover_label, True, Colors.YELLOW)
            
            # Position label on top of (above) the object, centered
            label_x = hover_x - hover_text.get_width() // 2
            label_y = hover_y - hover_text.get_height() - 8
            
            # Adjust if label would go off the left edge
            if label_x < self.minimap_rect.left + 5:
                label_x = self.minimap_rect.left + 5
            
            # Adjust if label would go off the right edge
            if label_x + hover_text.get_width() > self.minimap_rect.right - 5:
                label_x = self.minimap_rect.right - hover_text.get_width() - 5
            
            # Adjust if label would go off the top edge
            if label_y < self.minimap_rect.top + 5:
                label_y = hover_y + 10  # Place below instead
            
            # Draw semi-transparent background for better readability
            padding = 2
            bg_rect = pygame.Rect(
                label_x - padding,
                label_y - padding,
                hover_text.get_width() + padding * 2,
                hover_text.get_height() + padding * 2
            )
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)
            bg_surface.fill(Colors.BLACK)
            self.screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
            
            # Draw the label
            self.screen.blit(hover_text, (label_x, label_y))
        
        # Draw legend
        self._draw_minimap_legend()
        
        # Draw border
        self._draw_border(self.minimap_rect)
    
    def _draw_minimap_legend(self):
        """Draw legend for minimap colors."""
        legend_items = [
            (Colors.YELLOW, "Star"),
            (Colors.BLUE, "Planet"),
            (Colors.CYAN, "Wormhole"),
            (Colors.MAGENTA, "Pulsar"),
            (Colors.ORANGE, "Asteroid"),
            (Colors.GREEN, "Starbase"),
            (Colors.RED, "Enemy"),
        ]
        
        legend_x = self.minimap_rect.left + 10
        
        # Calculate line height based on font size + padding
        sample_text = self.font_small.render("Sample", True, Colors.WHITE)
        line_height = sample_text.get_height() + 4  # Add 4px padding between lines
        
        # Position legend at the very bottom of the minimap
        total_legend_height = len(legend_items) * line_height
        legend_y = self.minimap_rect.bottom - (total_legend_height + 5)
        
        for color, label in legend_items:
            # Draw colored symbol
            if label == "Enemy":
                # Draw red triangle for enemy ships
                size = 3
                center_x = legend_x + 3
                center_y = legend_y + 2
                points = [
                    (center_x, center_y - size),  # Top point
                    (center_x + size, center_y + size),  # Bottom right
                    (center_x - size, center_y + size)  # Bottom left
                ]
                pygame.draw.polygon(self.screen, color, points)
            else:
                # Draw colored dot for other objects
                pygame.draw.circle(self.screen, color, (int(legend_x + 3), int(legend_y + 2)), 2)
            
            # Draw label
            text = self.font_small.render(label, True, Colors.WHITE)
            self.screen.blit(text, (legend_x + 10, legend_y - 2))
            
            # Move to next line
            legend_y += line_height
    
    def _draw_message_area(self):
        """Draw the message area showing game messages."""
        # Fill background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, self.message_rect)
        
        # Draw title
        title = self.font.render("MESSAGES", True, Colors.YELLOW)
        self.screen.blit(title, (self.message_rect.left + 10, self.message_rect.top + 5))
        
        # Calculate available space and line height
        available_height = self.message_rect.height - 50  # Account for title and padding
        line_height = 20  # Line spacing in pixels
        max_visible_rows = max(1, available_height // line_height)  # At least 1 row
        
        # Draw messages (as many as fit in available space)
        visible_messages = self.messages[-max_visible_rows:]
        message_y = self.message_rect.top + 40
        
        for message in visible_messages:
            # Wrap long messages
            words = message.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                # Estimate line width
                test_line = " ".join(current_line)
                test_text = self.font_small.render(test_line, True, Colors.WHITE)
                if test_text.get_width() > self.message_area_width - 20:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
            
            if current_line:
                lines.append(" ".join(current_line))
            
            for line in lines:
                if message_y < self.message_rect.bottom - 20:
                    text = self.font_small.render(line, True, Colors.WHITE)
                    self.screen.blit(text, (self.message_rect.left + 10, message_y))
                    message_y += line_height
        
        # Draw border
        self._draw_border(self.message_rect)
    
    def _draw_command_prompt(self):
        """Draw the command input prompt."""
        # Fill background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, self.command_rect)
        
        # Draw title
        title = self.font.render("COMMAND", True, Colors.MAGENTA)
        self.screen.blit(title, (self.command_rect.left + 10, self.command_rect.top + 5))
        
        # Draw input box
        input_y = self.command_rect.top + 30
        input_box_height = 24
        input_box_rect = pygame.Rect(
            self.command_rect.left + 10,
            input_y,
            self.command_rect.width - 20,
            input_box_height
        )
        
        pygame.draw.rect(self.screen, Colors.BLACK, input_box_rect)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, input_box_rect, 2)
        
        # Draw input text
        if self.current_input or pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            input_text = self.font.render(self.current_input + ("|" if not self.current_input or pygame.time.get_ticks() % 1000 < 500 else ""), True, Colors.WHITE)
            self.screen.blit(input_text, (input_box_rect.left + 5, input_box_rect.top + 2))
        
        # Draw help text
        help_y = input_y + input_box_height + 10
        help_text = self.font_small.render(
            "Enter commands naturally (e.g., 'warp 5', 'scan', 'shields up')",
            True, Colors.LIGHT_GRAY
        )
        self.screen.blit(help_text, (self.command_rect.left + 10, help_y))
        
        # Draw recent command history
        history_y = help_y + 18
        history_text = self.font_small.render("↑↓ to navigate history", True, Colors.LIGHT_GRAY)
        self.screen.blit(history_text, (self.command_rect.left + 10, history_y))
        
        # Draw border
        self._draw_border(self.command_rect)
    
    def handle_events(self):
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                self.screen_width = event.size[0]
                self.screen_height = event.size[1]
                self._calculate_layout()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_minimap_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.current_input:
                        self._execute_command(self.current_input)
                        self.command_history.append(self.current_input)
                        self.history_index = -1
                        self.current_input = ""
                    else:
                        # Empty input treated as "skip" command
                        self._execute_command("skip")
                        self.history_index = -1
                
                elif event.key == pygame.K_BACKSPACE:
                    self.current_input = self.current_input[:-1]
                
                elif event.key == pygame.K_ESCAPE:
                    self.current_input = ""
                    self.history_index = -1
                
                elif event.key == pygame.K_UP:
                    if self.command_history:
                        self.history_index = min(self.history_index + 1, len(self.command_history) - 1)
                        self.current_input = self.command_history[-(self.history_index + 1)]
                
                elif event.key == pygame.K_DOWN:
                    if self.history_index > 0:
                        self.history_index -= 1
                        self.current_input = self.command_history[-(self.history_index + 1)]
                    elif self.history_index == 0:
                        self.history_index = -1
                        self.current_input = ""
                
                else:
                    # Add printable characters
                    if event.unicode.isprintable():
                        self.current_input += event.unicode
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom minimap with mouse scroll
                zoom_amount = -10.0 if event.y > 0 else 10.0
                new_zoom = self.minimap_zoom_offset + zoom_amount
                # Clamp to ±300 AU
                self.minimap_zoom_offset = max(-self.MAX_ZOOM_ADJUSTMENT,
                                               min(self.MAX_ZOOM_ADJUSTMENT, new_zoom))
        
        # Update mouse position for hover detection
        self.mouse_pos = pygame.mouse.get_pos()
    
    def _handle_minimap_click(self, click_pos):
        """Handle mouse click on minimap to navigate to clicked object."""
        click_x, click_y = click_pos
        
        # Check if click is within minimap bounds
        if not self.minimap_rect.collidepoint(click_x, click_y):
            return
        
        # Find clicked object
        for obj_x, obj_y, obj_id, radius in self.minimap_objects:
            distance = ((obj_x - click_x) ** 2 + (obj_y - click_y) ** 2) ** 0.5
            if distance <= radius:
                # Show immediate feedback message
                self.add_message(f"Setting course for {obj_id}")
                
                # Execute nav command first
                nav_command = f"nav {obj_id}"
                self._execute_command(nav_command)
                
                # Set navigation target after command to show yellow circle in subsequent frames
                self.nav_target_id = obj_id
                return
    
    def _execute_command(self, command: str):
        """Execute a command and add result to messages."""
        # Clear previous navigation target at the start of a new command
        prev_nav_target = self.nav_target_id
        self.nav_target_id = None
        
        # Check if player ship is destroyed
        if self.engine.player_ship.is_destroyed:
            self.add_message("Simulation completed. You have lost the battle!")
            return
        
        parsed = self.parser.parse(command)
        
        if parsed is None:
            self.add_message(f"Unknown command: {command}")
        else:
            # Execute the command in the game engine
            try:
                self.engine.process_turn(parsed)
                self.add_message(f"> {command}")
                # Add any messages from the engine
                for msg in self.engine.messages:
                    self.add_message(msg)
            except Exception as e:
                self.add_message(f"Error: {str(e)}")
    
    def update(self):
        """Update game state."""
        # Process one game turn if needed
        pass
    
    def draw(self):
        """Draw all UI elements."""
        # Clear screen
        self.screen.fill(Colors.BLACK)
        
        # Draw all areas
        self._draw_2d_map()
        self._draw_status_panel()
        self._draw_minimap()
        self._draw_message_area()
        self._draw_command_prompt()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()


def launch_ui():
    """Launch the game UI."""
    engine = GameEngine()
    ui = GameUI(engine)
    ui.run()


if __name__ == "__main__":
    launch_ui()
