"""
Wade Space Game - Pygame UI System

Comprehensive graphical interface with 2D map, minimap, status panel, and command prompt.
"""

import pygame
import math
import sys
from typing import Optional, Tuple, List
from src.game_engine import GameEngine
from src.command_parser import CommandParser
from src.universe_objects import Star, Planet, BlackHole, Pulsar, WormHole, Starbase, AsteroidField


class Colors:
    """Color palette for the game UI."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DARK_GRAY = (32, 32, 32)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    
    # Status colors
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    
    # UI colors
    HEALTHY = (0, 200, 0)
    WARNING = (255, 200, 0)
    DANGER = (255, 0, 0)


class GameUI:
    """Main UI system for Wade Space using Pygame."""
    
    # UI Layout
    FONT_SIZE = 16
    VIEWPORT_SIZE = 20.0  # AU visible on main map
    MINIMAP_SIZE = 500.0  # AU visible on minimap
    
    def __init__(self, game_engine: GameEngine):
        """Initialize the UI system."""
        pygame.init()
        
        self.engine = game_engine
        self.parser = CommandParser()
        
        # Get screen size (use default if info unavailable)
        try:
            info = pygame.display.get_surface()
            if info is None:
                # Create dummy surface to get info
                pygame.display.set_mode((1, 1))
            info = pygame.display.get_info()
            self.screen_width = int(info.current_w * 0.66)
            self.screen_height = int(info.current_h * 0.66)
        except (AttributeError, pygame.error):
            # Default fallback
            self.screen_width = 1280
            self.screen_height = 720
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Wade Space")
        
        # Fonts
        self.font_small = pygame.font.Font(None, 14)
        self.font_normal = pygame.font.Font(None, self.FONT_SIZE)
        self.font_large = pygame.font.Font(None, 22)
        self.font_title = pygame.font.Font(None, 26)
        
        # Layout calculations
        self.map_width = int(self.screen_width * 0.6)
        self.right_panel_width = self.screen_width - self.map_width
        self.status_height = int(self.screen_height * 0.35)
        self.minimap_height = int(self.screen_height * 0.35)
        self.message_height = int(self.screen_height * 0.20)
        self.input_height = self.screen_height - self.status_height - self.minimap_height - self.message_height
        
        # UI state
        self.command_history = []
        self.history_index = -1
        self.current_input = ""
        self.messages = []
        self.minimap_zoom = 1.0  # 1.0 = 500 AU, can go 0-3 for ±300 AU
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
    
    def handle_events(self) -> bool:
        """
        Handle pygame events.
        
        Returns:
            False if user wants to quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Execute command
                    self._execute_command(self.current_input)
                    self.command_history.append(self.current_input)
                    self.history_index = -1
                    self.current_input = ""
                
                elif event.key == pygame.K_BACKSPACE:
                    self.current_input = self.current_input[:-1]
                
                elif event.key == pygame.K_UP:
                    # Navigate command history
                    if self.command_history:
                        self.history_index = min(self.history_index + 1, len(self.command_history) - 1)
                        self.current_input = self.command_history[-(self.history_index + 1)]
                
                elif event.key == pygame.K_DOWN:
                    # Navigate command history backward
                    self.history_index = max(self.history_index - 1, -1)
                    if self.history_index >= 0:
                        self.current_input = self.command_history[-(self.history_index + 1)]
                    else:
                        self.current_input = ""
                
                elif event.key == pygame.K_ESCAPE:
                    self.current_input = ""
            
            elif event.type == pygame.TEXTINPUT:
                if event.text.isprintable():
                    self.current_input += event.text
            
            elif event.type == pygame.MOUSEWHEEL:
                # Minimap zoom
                if event.y > 0:
                    self.minimap_zoom = min(3.0, self.minimap_zoom + 0.1)
                else:
                    self.minimap_zoom = max(0.0, self.minimap_zoom - 0.1)
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen_width = event.size[0]
                self.screen_height = event.size[1]
                self._recalculate_layout()
        
        return True
    
    def _recalculate_layout(self):
        """Recalculate UI layout on resize."""
        self.map_width = int(self.screen_width * 0.6)
        self.right_panel_width = self.screen_width - self.map_width
    
    def _execute_command(self, command_text: str):
        """Execute a player command."""
        if not command_text.strip():
            return
        
        cmd = self.parser.parse(command_text)
        if cmd is None:
            self.add_message("Invalid command. Type 'help' for commands.")
            return
        
        self.engine.process_turn(player_command=cmd)
        
        # Add engine messages to UI
        for msg in self.engine.messages:
            self.add_message(msg)
        
        # Check game over
        if self.engine.game_over:
            self.game_over = True
            self.add_message(f"GAME OVER: {self.engine.game_over_reason}")
    
    def add_message(self, message: str):
        """Add a message to the message log."""
        self.messages.append(message)
        # Keep only last 50 messages
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
    
    def draw(self):
        """Draw the complete UI."""
        self.screen.fill(Colors.BLACK)
        
        # Draw main map on left
        self._draw_main_map()
        
        # Draw right panel sections
        self._draw_status_panel()
        self._draw_minimap()
        self._draw_message_log()
        self._draw_command_input()
        
        pygame.display.flip()
    
    def _draw_main_map(self):
        """Draw the main 2D game map."""
        map_rect = pygame.Rect(0, 0, self.map_width, self.screen_height)
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, map_rect)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, map_rect, 2)
        
        # Calculate viewport
        player_pos = self.engine.player_ship.position
        viewport_min_x = player_pos.x - self.VIEWPORT_SIZE / 2
        viewport_max_x = player_pos.x + self.VIEWPORT_SIZE / 2
        viewport_min_y = player_pos.y - self.VIEWPORT_SIZE / 2
        viewport_max_y = player_pos.y + self.VIEWPORT_SIZE / 2
        
        # Draw universe objects
        for obj_id, obj in self.engine.universe_objects.items():
            if (viewport_min_x <= obj.position.x <= viewport_max_x and
                viewport_min_y <= obj.position.y <= viewport_max_y):
                self._draw_object(obj, map_rect, player_pos)
        
        # Draw npc ships
        for npc_id, npc in self.engine.npc_ships.items():
            if (viewport_min_x <= npc.position.x <= viewport_max_x and
                viewport_min_y <= npc.position.y <= viewport_max_y):
                self._draw_ship(npc, map_rect, player_pos, is_player=False)
        
        # Draw player ship at center
        player_screen_x = map_rect.left + map_rect.width // 2
        player_screen_y = map_rect.top + map_rect.height // 2
        self._draw_player_ship(player_screen_x, player_screen_y)
        
        # Draw crosshair at center
        pygame.draw.circle(self.screen, Colors.GREEN, (player_screen_x, player_screen_y), 3)
    
    def _draw_object(self, obj, map_rect, player_pos):
        """Draw a universe object on the map."""
        # Calculate screen position
        rel_x = obj.position.x - player_pos.x
        rel_y = obj.position.y - player_pos.y
        
        screen_x = map_rect.left + map_rect.width // 2 + int(rel_x * map_rect.width / self.VIEWPORT_SIZE)
        screen_y = map_rect.top + map_rect.height // 2 + int(rel_y * map_rect.height / self.VIEWPORT_SIZE)
        
        if not (map_rect.left <= screen_x <= map_rect.right and map_rect.top <= screen_y <= map_rect.bottom):
            return
        
        # Determine color and size based on object type
        if isinstance(obj, Star):
            color = Colors.YELLOW
            size = 4
            symbol = "★"
        elif isinstance(obj, Planet):
            color = Colors.CYAN if obj.is_inhabited else Colors.GRAY
            size = 3
            symbol = "●"
        elif isinstance(obj, BlackHole):
            color = Colors.BLACK
            size = 5
            symbol = "⊗"
        elif isinstance(obj, Pulsar):
            color = Colors.MAGENTA
            size = 3
            symbol = "◇"
        elif isinstance(obj, WormHole):
            color = Colors.CYAN
            size = 4
            symbol = "◎"
        elif isinstance(obj, Starbase):
            color = Colors.GREEN if obj.friendly_to_player else Colors.RED
            size = 4
            symbol = "⊕"
        elif isinstance(obj, AsteroidField):
            color = Colors.GRAY
            size = 2
            symbol = "✕"
        else:
            return
        
        # Draw object
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), size)
        
        # Draw label (small and offset)
        label = self.font_small.render(obj.id, True, color)
        self.screen.blit(label, (screen_x + 5, screen_y - 6))
    
    def _draw_ship(self, ship, map_rect, player_pos, is_player: bool = False):
        """Draw a ship on the map."""
        rel_x = ship.position.x - player_pos.x
        rel_y = ship.position.y - player_pos.y
        
        screen_x = map_rect.left + map_rect.width // 2 + int(rel_x * map_rect.width / self.VIEWPORT_SIZE)
        screen_y = map_rect.top + map_rect.height // 2 + int(rel_y * map_rect.height / self.VIEWPORT_SIZE)
        
        if not (map_rect.left <= screen_x <= map_rect.right and map_rect.top <= screen_y <= map_rect.bottom):
            return
        
        # Draw ship as triangle
        if is_player:
            color = Colors.GREEN
            points = [(screen_x, screen_y - 8), (screen_x - 6, screen_y + 6), (screen_x + 6, screen_y + 6)]
        else:
            color = Colors.RED
            points = [(screen_x, screen_y + 8), (screen_x - 6, screen_y - 6), (screen_x + 6, screen_y - 6)]
        
        pygame.draw.polygon(self.screen, color, points)
        
        # Draw label
        label = self.font_small.render(ship.id, True, color)
        self.screen.blit(label, (screen_x + 8, screen_y - 6))
    
    def _draw_player_ship(self, x: int, y: int):
        """Draw the player's ship at center of map."""
        # Federation starship shape (triangle pointing up)
        points = [(x, y - 10), (x - 8, y + 8), (x + 8, y + 8)]
        pygame.draw.polygon(self.screen, Colors.GREEN, points)
        pygame.draw.polygon(self.screen, Colors.WHITE, points, 2)
    
    def _draw_status_panel(self):
        """Draw ship status panel on right side."""
        panel_x = self.map_width
        panel_y = 0
        panel_w = self.right_panel_width
        panel_h = self.status_height
        
        # Panel background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (panel_x, panel_y, panel_w, panel_h), 2)
        
        # Title
        title = self.font_title.render(f"Ship: {self.engine.player_ship.id}", True, Colors.CYAN)
        self.screen.blit(title, (panel_x + 10, panel_y + 5))
        
        # Status bars
        stats_y = panel_y + 35
        bar_width = panel_w - 30
        bar_height = 12
        
        stats = [
            ("Energy", self.engine.player_ship.energy, Colors.CYAN),
            ("Shields", self.engine.player_ship.shields, Colors.BLUE),
            ("Damage", self.engine.player_ship.damage, Colors.RED),
            ("Hull", 100 - self.engine.player_ship.damage, Colors.GREEN),
        ]
        
        for label, value, color in stats:
            self._draw_status_bar(panel_x + 15, stats_y, bar_width, bar_height, label, value, color)
            stats_y += 25
        
        # Vital stats (text)
        vital_y = stats_y + 10
        vitals = [
            f"Crew: {self.engine.player_ship.crew}/1000",
            f"Cash: ${self.engine.player_ship.cash}",
            f"Torpedos: {self.engine.player_ship.weapons.torpedos}",
            f"Warp Core: {self.engine.player_ship.propulsion.warp_core_temp:.0f}°",
        ]
        
        for vital in vitals:
            text = self.font_normal.render(vital, True, Colors.WHITE)
            self.screen.blit(text, (panel_x + 15, vital_y))
            vital_y += 18
    
    def _draw_status_bar(self, x: int, y: int, width: int, height: int, 
                         label: str, value: float, color: Tuple[int, int, int]):
        """Draw a status bar (health bar style)."""
        # Label
        label_text = self.font_normal.render(f"{label}: {value:.1f}%", True, Colors.WHITE)
        self.screen.blit(label_text, (x, y))
        
        # Background bar
        bar_y = y + 15
        pygame.draw.rect(self.screen, Colors.GRAY, (x, bar_y, width, height))
        pygame.draw.rect(self.screen, Colors.WHITE, (x, bar_y, width, height), 1)
        
        # Filled portion
        fill_width = int(width * (value / 100.0))
        pygame.draw.rect(self.screen, color, (x, bar_y, fill_width, height))
    
    def _draw_minimap(self):
        """Draw the minimap on the right side."""
        minimap_x = self.map_width
        minimap_y = self.status_height
        minimap_w = self.right_panel_width
        minimap_h = self.minimap_height
        
        # Panel background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (minimap_x, minimap_y, minimap_w, minimap_h))
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (minimap_x, minimap_y, minimap_w, minimap_h), 2)
        
        # Title
        zoom_level = f"{self.MINIMAP_SIZE * (1.0 - self.minimap_zoom):.0f}-{self.MINIMAP_SIZE * (1.0 + self.minimap_zoom):.0f} AU"
        title = self.font_normal.render(f"Minimap [{zoom_level}]", True, Colors.CYAN)
        self.screen.blit(title, (minimap_x + 10, minimap_y + 5))
        
        # Calculate viewport for minimap
        visible_au = self.MINIMAP_SIZE * (1.0 + self.minimap_zoom)
        player_pos = self.engine.player_ship.position
        viewport_min_x = player_pos.x - visible_au / 2
        viewport_max_x = player_pos.x + visible_au / 2
        viewport_min_y = player_pos.y - visible_au / 2
        viewport_max_y = player_pos.y + visible_au / 2
        
        # Draw universe objects (smaller)
        for obj_id, obj in list(self.engine.universe_objects.items())[:200]:  # Limit for performance
            if (viewport_min_x <= obj.position.x <= viewport_max_x and
                viewport_min_y <= obj.position.y <= viewport_max_y):
                rel_x = obj.position.x - player_pos.x
                rel_y = obj.position.y - player_pos.y
                
                screen_x = minimap_x + minimap_w // 2 + int(rel_x * (minimap_w - 20) / visible_au)
                screen_y = minimap_y + 25 + int(rel_y * (minimap_h - 40) / visible_au)
                
                if minimap_x + 10 <= screen_x <= minimap_x + minimap_w - 10:
                    if minimap_y + 25 <= screen_y <= minimap_y + minimap_h - 10:
                        color = Colors.YELLOW if isinstance(obj, Star) else Colors.GRAY
                        pygame.draw.circle(self.screen, color, (screen_x, screen_y), 1)
        
        # Draw player at center
        player_x = minimap_x + minimap_w // 2
        player_y = minimap_y + 25 + (minimap_h - 40) // 2
        pygame.draw.circle(self.screen, Colors.GREEN, (player_x, player_y), 2)
    
    def _draw_message_log(self):
        """Draw message log on right side."""
        msg_x = self.map_width
        msg_y = self.status_height + self.minimap_height
        msg_w = self.right_panel_width
        msg_h = self.message_height
        
        # Panel background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (msg_x, msg_y, msg_w, msg_h))
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (msg_x, msg_y, msg_w, msg_h), 2)
        
        # Title
        title = self.font_normal.render("Messages", True, Colors.CYAN)
        self.screen.blit(title, (msg_x + 10, msg_y + 5))
        
        # Display recent messages
        max_messages = (msg_h - 30) // 15
        start_idx = max(0, len(self.messages) - max_messages)
        
        draw_y = msg_y + 25
        for msg in self.messages[start_idx:]:
            # Truncate long messages
            if len(msg) > 60:
                msg = msg[:57] + "..."
            text = self.font_small.render(msg, True, Colors.WHITE)
            self.screen.blit(text, (msg_x + 10, draw_y))
            draw_y += 14
    
    def _draw_command_input(self):
        """Draw command input prompt at bottom right."""
        inp_x = self.map_width
        inp_y = self.status_height + self.minimap_height + self.message_height
        inp_w = self.right_panel_width
        inp_h = self.input_height
        
        # Panel background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (inp_x, inp_y, inp_w, inp_h))
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (inp_x, inp_y, inp_w, inp_h), 2)
        
        # Title
        title = self.font_normal.render("Command Prompt", True, Colors.CYAN)
        self.screen.blit(title, (inp_x + 10, inp_y + 5))
        
        # Input field
        input_text = self.current_input + ("_" if int(pygame.time.get_ticks() / 500) % 2 else "")
        input_display = self.font_normal.render(input_text, True, Colors.WHITE)
        self.screen.blit(input_display, (inp_x + 15, inp_y + 30))
        
        # Help text
        help_text = self.font_small.render(
            "Commands: warp, impulse, heading, shields, scan, lock, fire, torpedo, status, nav, stop, skip",
            True, Colors.LIGHT_GRAY
        )
        self.screen.blit(help_text, (inp_x + 10, inp_y + 60))
        
        help_text2 = self.font_small.render(
            "↑/↓: history | ESC: clear | ENTER: execute",
            True, Colors.LIGHT_GRAY
        )
        self.screen.blit(help_text2, (inp_x + 10, inp_y + 78))
    
    def update(self):
        """Update game state for one frame."""
        self.clock.tick(60)  # 60 FPS
    
    def run(self):
        """Main UI loop."""
        while self.running:
            if not self.handle_events():
                break
            
            self.draw()
            self.update()
            
            if self.game_over:
                # Wait for user input before closing
                pygame.time.wait(1000)
                break
        
        pygame.quit()


def launch_ui():
    """Launch the Wade Space UI."""
    engine = GameEngine(universe_seed=None)
    ui = GameUI(engine)
    ui.run()


if __name__ == '__main__':
    launch_ui()
