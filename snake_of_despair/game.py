"""
Main game loop, state machine, input handling, and rendering.
"""

import pygame
import sys
import time
from typing import Optional, Dict, Any, Callable
from enum import Enum

import random

from .config import Config
from .snake import Snake, Direction, Position
from .apple import AppleManager
from .walls import WallManager
from .screamers import ScreamerManager
from .ui import MainMenu, SettingsMenu, PauseMenu, GameOverMenu, HUD, CreditsScreen
from .assets import AssetManager
from .safety import SafetyManager, SafetySettings
from .colors import ColorManager
from .logging_utils import GameLogger, SeedManager, TelemetryCollector
from .telemetry import TelemetryCollector as Telemetry


class GameState(Enum):
    """Game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    CREDITS = "credits"


class Game:
    """Main game class managing the game loop and state."""
    
    def __init__(self, config: Config):
        """Initialize game with configuration."""
        self.config = config
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Set up display
        self.screen = pygame.display.set_mode(self.config.window_size)
        pygame.display.set_caption("Snake of Despair")
        
        # Initialize managers
        self.seed_manager = SeedManager(config.seed)
        self.color_manager = ColorManager(config.reduced_scare)
        self.asset_manager = AssetManager(reduced_scare=config.reduced_scare)
        self.safety_manager = SafetyManager(SafetySettings(reduced_scare=config.reduced_scare))
        self.logger = GameLogger()
        self.telemetry = Telemetry()
        
        # Initialize game objects
        self.snake = None
        self.apple_manager = None
        self.wall_manager = None
        self.screamer_manager = None
        self.hud = None
        
        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.high_score = 0
        self.current_menu = None
        
        # Initialize game systems
        self._initialize_game_systems()
        self._setup_menus()
        
    def _initialize_game_systems(self) -> None:
        """Initialize all game systems."""
        # Create HUD
        self.hud = HUD(self.config.window_size[0], self.config.window_size[1])
        
        # Initialize game objects (will be created when game starts)
        self._reset_game()
    
    def _setup_menus(self) -> None:
        """Setup game menus."""
        self.main_menu = MainMenu(
            start_game=self._start_game,
            show_settings=self._show_settings,
            show_credits=self._show_credits,
            quit_game=self._quit_game
        )
        
        self.settings_menu = SettingsMenu(
            back_to_main=self._show_main_menu,
            toggle_reduced_scare=self._toggle_reduced_scare,
            toggle_mute=self._toggle_mute,
            change_difficulty=self._change_difficulty
        )
        
        self.credits_screen = CreditsScreen(self._show_main_menu)
        
        self.current_menu = self.main_menu
    
    def _reset_game(self) -> None:
        """Reset game to initial state."""
        # Create snake
        start_pos = Position(self.config.GRID_WIDTH // 2, self.config.GRID_HEIGHT // 2)
        self.snake = Snake(start_pos, self.config.GRID_WIDTH, self.config.GRID_HEIGHT)
        
        # Create apple manager
        self.apple_manager = AppleManager(self.config.GRID_WIDTH, self.config.GRID_HEIGHT)
        
        # Spawn initial apple
        self.apple_manager.spawn_apple(time.time(), self.snake.get_body_positions())
        
        # Create wall manager
        self.wall_manager = WallManager(self.config.GRID_WIDTH, self.config.GRID_HEIGHT)
        
        # Create screamer system (4-step pipeline with images and sounds)
        self.screamer_manager = ScreamerManager(
            self.screen,
            asset_root="assets",
            reduced_scare=self.config.reduced_scare
        )
        
        # Reset score
        self.score = 0
        
        # Log game start
        self.logger.log_game_start({
            "seed": self.config.seed,
            "difficulty": self.config.difficulty,
            "reduced_scare": self.config.reduced_scare
        })
    
    def run(self) -> None:
        """Main game loop."""
        self.running = True
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_game()
                else:
                    self._handle_event(event)
            
            # Update game state
            self._update()
            
            # Render
            self._render()
            
            # Control frame rate
            self.clock.tick(self.config.FPS)
        
        # Cleanup
        pygame.quit()
        sys.exit()
    
    def _handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.state == GameState.MENU:
            self._handle_menu_input(event)
        elif self.state == GameState.PLAYING:
            self._handle_game_input(event)
        elif self.state == GameState.PAUSED:
            self._handle_pause_input(event)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over_input(event)
        elif self.state == GameState.SETTINGS:
            self._handle_settings_input(event)
        elif self.state == GameState.CREDITS:
            self._handle_credits_input(event)
    
    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if self.current_menu:
            result = self.current_menu.handle_input(event)
            if result:
                # Handle menu result
                pass
    
    def _handle_game_input(self, event: pygame.event.Event) -> None:
        """Handle game input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._pause_game()
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                self.snake.set_direction(Direction.UP)
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.snake.set_direction(Direction.DOWN)
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.snake.set_direction(Direction.LEFT)
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.snake.set_direction(Direction.RIGHT)
    
    def _handle_pause_input(self, event: pygame.event.Event) -> None:
        """Handle pause input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._resume_game()
            elif event.key == pygame.K_r:
                self._restart_game()
            elif event.key == pygame.K_m:
                self._show_main_menu()
    
    def _handle_game_over_input(self, event: pygame.event.Event) -> None:
        """Handle game over input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._restart_game()
            elif event.key == pygame.K_m:
                self._show_main_menu()
    
    def _handle_settings_input(self, event: pygame.event.Event) -> None:
        """Handle settings input."""
        if self.current_menu:
            result = self.current_menu.handle_input(event)
            if result:
                # Handle settings result
                pass
    
    def _handle_credits_input(self, event: pygame.event.Event) -> None:
        """Handle credits input."""
        if self.current_menu:
            result = self.current_menu.handle_input(event)
            if result:
                # Handle credits result
                pass
    
    def _update(self) -> None:
        """Update game state."""
        current_time = time.time()
        
        if self.state == GameState.PLAYING:
            self._update_game(current_time)
        elif self.state == GameState.MENU:
            self._update_menu()
        # Other states don't need updates
    
    def _update_game(self, current_time: float) -> None:
        """Update game logic."""
        # Random screamer check (runs every tick for rare random scares)
        self.screamer_manager.update(current_time)
        
        # Update snake
        move_interval = self.config.BASE_SPEED / self.snake.get_speed_factor()
        if self.snake.update(current_time, move_interval):
            # Snake moved, check for collisions and apples
            self._check_collisions()
            self._check_apples()
            
            # Update telemetry
            self.telemetry.record_performance(self.clock.get_fps(), self.clock.get_time())
    
    def _update_menu(self) -> None:
        """Update menu state."""
        # Menus don't need updates
        pass
    
    def _check_collisions(self) -> None:
        """Check for collisions."""
        head = self.snake.get_head()
        
        # Check spawned wall collision - shrink snake, 20% screamer chance
        if self.snake.alive and self.wall_manager.check_collision(head):
            # Shrink the snake by one cell
            if len(self.snake.body) > 1:
                self.snake.body.pop()  # Remove tail segment
                self.score = max(0, self.score - 10)  # Lose points too
                
                # 20% chance of screamer
                if random.random() < 0.20:
                    self.screamer_manager.force_trigger()
                
                # Log the event
                self.telemetry.record_gameplay_event("wall_hit", {
                    "score": self.score,
                    "snake_length": self.snake.get_length()
                })
            else:
                # Snake is only 1 cell - game over
                self.snake.alive = False
                self._game_over("wall_collision")
            return
        
        # Check border/self collision (instant death)
        if not self.snake.alive:
            # Snake died, determine cause
            if (head.x < 0 or head.x >= self.config.GRID_WIDTH or 
                head.y < 0 or head.y >= self.config.GRID_HEIGHT):
                cause = "wall_collision"
            else:
                cause = "self_collision"
            
            self._game_over(cause)
    
    def _check_apples(self) -> None:
        """Check for apple collisions."""
        head = self.snake.get_head()
        apple = self.apple_manager.check_collision(head)
        
        if apple:
            # Snake ate apple
            self.snake.eat_apple()
            self.apple_manager.remove_apple(apple)
            self.score = self.snake.score
            
            # Update telemetry
            self.telemetry.record_gameplay_event("apple_eaten", {
                "score": self.score,
                "snake_length": self.snake.get_length()
            })
            
            # Spawn a wall for harder gameplay
            self.wall_manager.spawn_wall(
                self.snake.get_body_positions(),
                self.apple_manager.get_apple_positions()
            )
            
            # Spawn new apple (avoiding walls)
            occupied = self.snake.get_body_positions()
            occupied.update(self.wall_manager.get_all_positions())
            self.apple_manager.spawn_apple(time.time(), occupied)
    

    def _render(self) -> None:
        """Render game."""
        colors = self.color_manager._colors
        
        if self.state == GameState.PLAYING:
            self._render_game(colors)
        elif self.state == GameState.MENU:
            self._render_menu(colors)
        elif self.state == GameState.PAUSED:
            self._render_pause(colors)
        elif self.state == GameState.GAME_OVER:
            self._render_game_over(colors)
        elif self.state == GameState.SETTINGS:
            self._render_settings(colors)
        elif self.state == GameState.CREDITS:
            self._render_credits(colors)
        
        pygame.display.flip()
    
    def _render_game(self, colors: Dict[str, Any]) -> None:
        """Render game screen."""
        # Clear screen
        self.screen.fill(colors.get("background", (20, 20, 20)))
        
        # Calculate grid position
        grid_width = self.config.GRID_WIDTH * self.config.GRID_SIZE
        grid_height = self.config.GRID_HEIGHT * self.config.GRID_SIZE
        grid_x = (self.config.window_size[0] - grid_width) // 2
        grid_y = (self.config.window_size[1] - grid_height) // 2
        
        # Draw grid background
        pygame.draw.rect(self.screen, (30, 30, 30), 
                        (grid_x, grid_y, grid_width, grid_height))
        
        # Draw walls
        self._draw_walls(grid_x, grid_y, colors)
        
        # Draw snake
        self._draw_snake(grid_x, grid_y, colors)
        
        # Draw apples
        self._draw_apples(grid_x, grid_y, colors)
        
        # Draw HUD
        self.hud.render(self.screen, self.score, self.high_score, 0, colors)
    
    def _draw_snake(self, grid_x: int, grid_y: int, colors: Dict[str, Any]) -> None:
        """Draw snake."""
        body_color, head_color = self.color_manager.get_snake_colors()
        
        for i, segment in enumerate(self.snake.body):
            x = grid_x + segment.x * self.config.GRID_SIZE
            y = grid_y + segment.y * self.config.GRID_SIZE
            
            color = head_color if i == 0 else body_color
            pygame.draw.rect(self.screen, color, 
                           (x, y, self.config.GRID_SIZE, self.config.GRID_SIZE))
    
    def _draw_apples(self, grid_x: int, grid_y: int, colors: Dict[str, Any]) -> None:
        """Draw apples."""
        apple_color = self.color_manager.get_apple_color()
        
        for apple in self.apple_manager.get_apples():
            x = grid_x + apple.position.x * self.config.GRID_SIZE
            y = grid_y + apple.position.y * self.config.GRID_SIZE
            
            pygame.draw.rect(self.screen, apple_color,
                           (x, y, self.config.GRID_SIZE, self.config.GRID_SIZE))
    
    def _draw_walls(self, grid_x: int, grid_y: int, colors: Dict[str, Any]) -> None:
        """Draw walls."""
        wall_color = colors.get("wall", (100, 100, 100))
        
        for wall in self.wall_manager.get_walls():
            for pos in wall.positions:
                x = grid_x + pos.x * self.config.GRID_SIZE
                y = grid_y + pos.y * self.config.GRID_SIZE
                
                pygame.draw.rect(self.screen, wall_color,
                               (x, y, self.config.GRID_SIZE, self.config.GRID_SIZE))
    

    def _render_menu(self, colors: Dict[str, Any]) -> None:
        """Render menu."""
        if self.current_menu:
            self.current_menu.render(self.screen, colors)
    
    def _render_pause(self, colors: Dict[str, Any]) -> None:
        """Render pause screen."""
        # Draw game in background
        self._render_game(colors)
        
        # Draw pause overlay
        overlay = pygame.Surface(self.config.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        font = pygame.font.Font(None, 48)
        text = font.render("PAUSED", True, colors.get("text", (255, 255, 255)))
        text_rect = text.get_rect(center=(self.config.window_size[0] // 2, 
                                         self.config.window_size[1] // 2))
        self.screen.blit(text, text_rect)
    
    def _render_game_over(self, colors: Dict[str, Any]) -> None:
        """Render game over screen."""
        if self.current_menu:
            self.current_menu.render(self.screen, colors)
    
    def _render_settings(self, colors: Dict[str, Any]) -> None:
        """Render settings screen."""
        if self.current_menu:
            self.current_menu.render(self.screen, colors)
    
    def _render_credits(self, colors: Dict[str, Any]) -> None:
        """Render credits screen."""
        if self.current_menu:
            self.current_menu.render(self.screen, colors)
    
    # Game state transitions
    def _start_game(self) -> None:
        """Start new game."""
        self._reset_game()
        self.state = GameState.PLAYING
        self.current_menu = None
    
    def _pause_game(self) -> None:
        """Pause game."""
        self.state = GameState.PAUSED
        self.current_menu = PauseMenu(
            resume_game=self._resume_game,
            restart_game=self._restart_game,
            back_to_main=self._show_main_menu
        )
    
    def _resume_game(self) -> None:
        """Resume game."""
        self.state = GameState.PLAYING
        self.current_menu = None
    
    def _restart_game(self) -> None:
        """Restart game."""
        self._start_game()
    
    def _game_over(self, cause: str) -> None:
        """Handle game over."""
        self.state = GameState.GAME_OVER
        
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Log game end
        self.logger.log_game_end(self.score, cause)
        self.telemetry.record_death(cause)
        
        # Create game over menu
        self.current_menu = GameOverMenu(
            score=self.score,
            high_score=self.high_score,
            restart_game=self._restart_game,
            back_to_main=self._show_main_menu
        )
    
    def _show_main_menu(self) -> None:
        """Show main menu."""
        self.state = GameState.MENU
        self.current_menu = self.main_menu
    
    def _show_settings(self) -> None:
        """Show settings menu."""
        self.state = GameState.SETTINGS
        self.current_menu = self.settings_menu
    
    def _show_credits(self) -> None:
        """Show credits screen."""
        self.state = GameState.CREDITS
        self.current_menu = self.credits_screen
    
    def _quit_game(self) -> None:
        """Quit game."""
        self.running = False
    
    # Settings handlers
    def _toggle_reduced_scare(self) -> None:
        """Toggle reduced scare mode."""
        self.config.reduced_scare = not self.config.reduced_scare
        self.color_manager.set_reduced_scare(self.config.reduced_scare)
        self.safety_manager.settings.reduced_scare = self.config.reduced_scare
    
    def _toggle_mute(self) -> None:
        """Toggle mute."""
        self.config.mute = not self.config.mute
        if self.config.mute:
            pygame.mixer.stop()
    
    def _change_difficulty(self) -> None:
        """Change difficulty."""
        difficulties = ["easy", "normal", "hard"]
        current_index = difficulties.index(self.config.difficulty)
        self.config.difficulty = difficulties[(current_index + 1) % len(difficulties)]
