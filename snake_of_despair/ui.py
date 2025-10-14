"""
UI system with menus, settings, overlays, and HUD elements.
"""

import pygame
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class MenuState(Enum):
    """Menu states."""
    MAIN = "main"
    SETTINGS = "settings"
    PAUSE = "pause"
    GAME_OVER = "game_over"
    CREDITS = "credits"


@dataclass
class MenuItem:
    """Individual menu item."""
    text: str
    action: Callable
    enabled: bool = True
    selected: bool = False


class Menu:
    """Base menu class."""
    
    def __init__(self, title: str, items: List[MenuItem], font_size: int = 32):
        """Initialize menu."""
        self.title = title
        self.items = items
        self.font_size = font_size
        self.selected_index = 0
        self.font = pygame.font.Font(None, font_size)
        self.title_font = pygame.font.Font(None, font_size + 16)
    
    def handle_input(self, event: pygame.event.Event) -> Optional[Any]:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self._move_selection(1)
            elif event.key == pygame.K_RETURN:
                return self._select_item()
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None
    
    def _move_selection(self, direction: int) -> None:
        """Move selection up or down."""
        self.selected_index = (self.selected_index + direction) % len(self.items)
        # Skip disabled items
        while not self.items[self.selected_index].enabled:
            self.selected_index = (self.selected_index + direction) % len(self.items)
    
    def _select_item(self) -> Any:
        """Select current item."""
        if self.items[self.selected_index].enabled:
            return self.items[self.selected_index].action()
        return None
    
    def render(self, screen: pygame.Surface, colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Render menu to screen."""
        screen_width, screen_height = screen.get_size()
        
        # Clear screen
        screen.fill(colors.get("background", (20, 20, 20)))
        
        # Render title
        title_surface = self.title_font.render(self.title, True, colors.get("text", (255, 255, 255)))
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_surface, title_rect)
        
        # Render menu items
        start_y = screen_height // 2
        item_height = 50
        
        for i, item in enumerate(self.items):
            color = colors.get("text", (255, 255, 255))
            if i == self.selected_index:
                color = colors.get("text_highlight", (255, 255, 0))
            elif not item.enabled:
                color = colors.get("text_dim", (100, 100, 100))
            
            text_surface = self.font.render(item.text, True, color)
            text_rect = text_surface.get_rect(center=(screen_width // 2, start_y + i * item_height))
            screen.blit(text_surface, text_rect)


class MainMenu(Menu):
    """Main game menu."""
    
    def __init__(self, start_game: Callable, show_settings: Callable, show_credits: Callable, quit_game: Callable):
        """Initialize main menu."""
        items = [
            MenuItem("Start Game", start_game),
            MenuItem("Settings", show_settings),
            MenuItem("Credits", show_credits),
            MenuItem("Quit", quit_game)
        ]
        super().__init__("Snake of Despair", items)


class SettingsMenu(Menu):
    """Settings menu."""
    
    def __init__(self, back_to_main: Callable, toggle_reduced_scare: Callable, 
                 toggle_mute: Callable, change_difficulty: Callable):
        """Initialize settings menu."""
        self.reduced_scare = False
        self.muted = False
        self.difficulty = "normal"
        
        items = [
            MenuItem("Reduced Scare Mode", toggle_reduced_scare),
            MenuItem("Mute Audio", toggle_mute),
            MenuItem("Difficulty", change_difficulty),
            MenuItem("Back", back_to_main)
        ]
        super().__init__("Settings", items)
    
    def toggle_reduced_scare(self) -> None:
        """Toggle reduced scare mode."""
        self.reduced_scare = not self.reduced_scare
        self.items[0].text = f"Reduced Scare Mode: {'ON' if self.reduced_scare else 'OFF'}"
    
    def toggle_mute(self) -> None:
        """Toggle mute."""
        self.muted = not self.muted
        self.items[1].text = f"Mute Audio: {'ON' if self.muted else 'OFF'}"
    
    def change_difficulty(self) -> None:
        """Cycle through difficulties."""
        difficulties = ["easy", "normal", "hard"]
        current_index = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
        self.items[2].text = f"Difficulty: {self.difficulty.upper()}"


class PauseMenu(Menu):
    """Pause menu."""
    
    def __init__(self, resume_game: Callable, restart_game: Callable, 
                 back_to_main: Callable):
        """Initialize pause menu."""
        items = [
            MenuItem("Resume", resume_game),
            MenuItem("Restart", restart_game),
            MenuItem("Main Menu", back_to_main)
        ]
        super().__init__("Paused", items)


class GameOverMenu(Menu):
    """Game over menu."""
    
    def __init__(self, score: int, high_score: int, restart_game: Callable, back_to_main: Callable):
        """Initialize game over menu."""
        self.score = score
        self.high_score = high_score
        
        items = [
            MenuItem("Play Again", restart_game),
            MenuItem("Main Menu", back_to_main)
        ]
        super().__init__("Game Over", items)
    
    def render(self, screen: pygame.Surface, colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Render game over menu with score."""
        super().render(screen, colors)
        
        # Render score information
        screen_width, screen_height = screen.get_size()
        font = pygame.font.Font(None, 24)
        
        score_text = f"Score: {self.score}"
        high_score_text = f"High Score: {self.high_score}"
        
        score_surface = font.render(score_text, True, colors.get("text", (255, 255, 255)))
        high_score_surface = font.render(high_score_text, True, colors.get("text", (255, 255, 255)))
        
        score_rect = score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
        high_score_rect = high_score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 130))
        
        screen.blit(score_surface, score_rect)
        screen.blit(high_score_surface, high_score_rect)


class HUD:
    """Heads-up display for game information."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize HUD."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
    def render(self, screen: pygame.Surface, score: int, high_score: int, 
               tension: float, colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Render HUD elements."""
        # Score
        score_text = f"Score: {score}"
        score_surface = self.font.render(score_text, True, colors.get("text", (255, 255, 255)))
        screen.blit(score_surface, (10, 10))
        
        # High score
        high_score_text = f"High: {high_score}"
        high_score_surface = self.font.render(high_score_text, True, colors.get("text", (255, 255, 255)))
        screen.blit(high_score_surface, (10, 40))
        
        # Tension meter
        self._render_tension_meter(screen, tension, colors)
    
    def _render_tension_meter(self, screen: pygame.Surface, tension: float, 
                            colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Render tension meter."""
        meter_width = 200
        meter_height = 20
        meter_x = self.screen_width - meter_width - 10
        meter_y = 10
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))
        
        # Tension bar
        tension_width = int(meter_width * (tension / 100.0))
        tension_color = self._get_tension_color(tension)
        pygame.draw.rect(screen, tension_color, (meter_x, meter_y, tension_width, meter_height))
        
        # Border
        pygame.draw.rect(screen, colors.get("text", (255, 255, 255)), 
                        (meter_x, meter_y, meter_width, meter_height), 2)
        
        # Label
        label_text = f"Tension: {tension:.1f}%"
        label_surface = self.small_font.render(label_text, True, colors.get("text", (255, 255, 255)))
        screen.blit(label_surface, (meter_x, meter_y - 25))
    
    def _get_tension_color(self, tension: float) -> Tuple[int, int, int]:
        """Get color for tension level."""
        if tension < 20:
            return (0, 255, 0)  # Green
        elif tension < 40:
            return (255, 255, 0)  # Yellow
        elif tension < 60:
            return (255, 165, 0)  # Orange
        elif tension < 80:
            return (255, 0, 0)  # Red
        else:
            return (128, 0, 128)  # Purple


class TimedChoicePrompt:
    """Timed choice prompt with countdown."""
    
    def __init__(self, question: str, choices: List[str], default_choice: int = 0, 
                 timeout: float = 5.0):
        """Initialize timed choice prompt."""
        self.question = question
        self.choices = choices
        self.default_choice = default_choice
        self.timeout = timeout
        self.start_time = time.time()
        self.selected_choice = default_choice
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
    
    def handle_input(self, event: pygame.event.Event) -> Optional[int]:
        """Handle input for choice selection."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_choice = (self.selected_choice - 1) % len(self.choices)
            elif event.key == pygame.K_RIGHT:
                self.selected_choice = (self.selected_choice + 1) % len(self.choices)
            elif event.key == pygame.K_RETURN:
                return self.selected_choice
        
        return None
    
    def update(self) -> Optional[int]:
        """Update prompt and return choice if timeout or selection."""
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.timeout:
            return self.default_choice
        
        return None
    
    def render(self, screen: pygame.Surface, colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Render timed choice prompt."""
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Prompt box
        box_width = 400
        box_height = 200
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        
        pygame.draw.rect(screen, (50, 50, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, colors.get("text", (255, 255, 255)), 
                        (box_x, box_y, box_width, box_height), 2)
        
        # Question
        question_surface = self.title_font.render(self.question, True, colors.get("text", (255, 255, 255)))
        question_rect = question_surface.get_rect(center=(screen_width // 2, box_y + 50))
        screen.blit(question_surface, question_rect)
        
        # Choices
        choice_x = box_x + 50
        choice_y = box_y + 100
        choice_spacing = 100
        
        for i, choice in enumerate(self.choices):
            color = colors.get("text_highlight", (255, 255, 0)) if i == self.selected_choice else colors.get("text", (255, 255, 255))
            choice_surface = self.font.render(choice, True, color)
            screen.blit(choice_surface, (choice_x + i * choice_spacing, choice_y))
        
        # Countdown
        remaining = self.timeout - (time.time() - self.start_time)
        countdown_text = f"Time: {remaining:.1f}s"
        countdown_surface = self.font.render(countdown_text, True, colors.get("text", (255, 255, 255)))
        screen.blit(countdown_surface, (box_x + 50, box_y + 150))


class CreditsScreen:
    """Credits screen."""
    
    def __init__(self, back_to_main: Callable):
        """Initialize credits screen."""
        self.back_to_main = back_to_main
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        self.credits = [
            "Snake of Despair",
            "",
            "Developed by:",
            "Kaulan Serzhanuly",
            "Danila Kharitonenkov",
            "",
            "CS 122 - Fall 2025",
            "San Jose State University",
            "",
            "Special Thanks:",
            "Pygame Community",
            "Open Source Contributors",
            "",
            "Press ESC to return to main menu"
        ]
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self.back_to_main()
        return None
    
    def render(self, screen: pygame.Surface, colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Render credits screen."""
        screen_width, screen_height = screen.get_size()
        screen.fill(colors.get("background", (20, 20, 20)))
        
        # Render credits
        start_y = screen_height // 4
        line_height = 30
        
        for i, line in enumerate(self.credits):
            if line == "":
                continue
            
            if i == 0:  # Title
                surface = self.title_font.render(line, True, colors.get("text", (255, 255, 255)))
            else:
                surface = self.font.render(line, True, colors.get("text", (255, 255, 255)))
            
            rect = surface.get_rect(center=(screen_width // 2, start_y + i * line_height))
            screen.blit(surface, rect)
