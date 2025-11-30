"""
WannaCry-style ransomware screen event.
Triggers at a certain score and requires a key combination to unlock.
"""

import pygame
import random, time
from typing import Callable, List

from .ui import render_multiline_text


class WannaCryScreen:
    """
    A full-screen event that mimics a ransomware screen and requires a
    specific arrow key combination to be entered.
    """

    def __init__(self, screen: pygame.Surface, on_complete: Callable[[], None]):
        """
        Initialize the WannaCry screen.

        Args:
            screen: The main pygame screen surface.
            on_complete: A callback function to call when the sequence is correctly entered.
        """
        self.screen = screen
        self.on_complete = on_complete
        self.screen_width, self.screen_height = screen.get_size()

        # --- Font Loading with Fallbacks for Arrow Symbols ---
        # Try to find a font that supports the arrow characters.
        font_candidates = [
            'segoeuisymbol', # Best for Windows
            'arialunicodems',
            'dejavusans',
            None # Default pygame font as a last resort
        ]
        symbol_font_path = None
        for font_name in font_candidates:
            try:
                symbol_font_path = pygame.font.match_font(font_name)
                if symbol_font_path:
                    break
            except (FileNotFoundError, pygame.error):
                continue

        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 22)
        self.font_mono = pygame.font.Font(pygame.font.match_font('consolas', 'couriernew'), 28)
        self.font_symbols = pygame.font.Font(symbol_font_path, 48) # Font for the arrows

        # Colors
        self.background_color = (139, 0, 0)  # Dark Red
        self.text_color = (255, 255, 255)
        self.red_text_color = (255, 50, 50)
        self.highlight_color = (0, 255, 0)  # Green for correct input

        # Key sequence logic
        self.sequence: List[int] = []
        self.current_input_index = 0
        self.is_complete = False
        self.start_time = time.time()
        self._generate_sequence()

    def _generate_sequence(self, length: int = 6):
        """Generate a random sequence of arrow keys."""
        keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        self.sequence = [random.choice(keys) for _ in range(length)]

    def _get_key_str(self, key: int) -> str:
        """Convert a key constant to a display string."""
        return {
            pygame.K_UP: "↑",
            pygame.K_DOWN: "↓",
            pygame.K_LEFT: "←",
            pygame.K_RIGHT: "→"
        }.get(key, "?")

    def handle_input(self, event: pygame.event.Event):
        """Handle user input to check against the key sequence."""
        if self.is_complete or event.type != pygame.KEYDOWN:
            return

        # Check if the pressed key is the next one in the sequence
        if event.key == self.sequence[self.current_input_index]:
            self.current_input_index += 1
            # Check for completion
            if self.current_input_index == len(self.sequence):
                self.is_complete = True
                self.on_complete()
        # If an incorrect arrow key is pressed, reset progress
        elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            self.current_input_index = 0

    def render(self):
        """Render the WannaCry screen."""
        self.screen.fill(self.background_color)
        
        # --- Left Column (Text) ---
        left_col_x = self.screen_width // 4
        
        # Title
        title_surf = self.font_large.render("Ooops, your files are encrypted!", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title_surf, title_rect)

        # Main Text
        main_text = (
            "What Happened to My Computer?\n"
            "Your important files have been corrupted by the Snake of Despair. Photos, videos, documents - all gone.\n"
            "Don't worry, there is a way to undo the damage. But you must prove your worth.\n\n"
            "Can I Recover My Files?\n"
            "Yes. The system requires a decryption key. To generate this key, you must enter the correct sequence of commands.\n"
            "If you fail, the corruption may become permanent. Do not try to restart your computer."
        )
        render_multiline_text(
            self.screen, main_text, self.font_small, self.text_color,
            left_col_x, 200, align='left'
        )

        # --- Right Column (Action) ---
        right_col_x = self.screen_width * 3 // 4

        # Countdown Timer
        elapsed = time.time() - self.start_time
        payment_due = max(0, 3 * 3600 * 24 - elapsed) # 3 days in seconds
        time_str = time.strftime('%H:%M:%S', time.gmtime(payment_due))
        
        render_multiline_text(self.screen, "Payment will be raised on", self.font_medium, self.red_text_color, right_col_x, 250)
        timer_surf = self.font_mono.render(time_str, True, self.red_text_color)
        timer_rect = timer_surf.get_rect(center=(right_col_x, 300))
        pygame.draw.rect(self.screen, (0,0,0), timer_rect.inflate(20, 10))
        self.screen.blit(timer_surf, timer_rect)

        # Sequence Display
        self._render_sequence_display(right_col_x, self.screen_height // 2 + 100)

    def _render_sequence_display(self, center_x: int, center_y: int):
        """Render the visual representation of the key sequence and user progress."""
        # Instruction text
        instr_surf = self.font_medium.render("Enter Decryption Key:", True, self.text_color)
        instr_rect = instr_surf.get_rect(center=(center_x, center_y - 80))
        self.screen.blit(instr_surf, instr_rect)

        # Sequence boxes
        box_size = 60
        total_width = len(self.sequence) * (box_size + 10)
        start_x = center_x - total_width // 2

        for i, key in enumerate(self.sequence):
            x = start_x + i * (box_size + 10)
            box_rect = pygame.Rect(x, center_y - box_size // 2, box_size, box_size)

            key_str = self._get_key_str(key)
            
            # Determine color based on user progress
            if i < self.current_input_index:
                # Correctly entered part of the sequence
                color = self.highlight_color
                box_color = (10, 40, 10)
            else:
                # Remaining part of the sequence
                color = self.text_color
                box_color = (0, 0, 0)

            # Draw box
            pygame.draw.rect(self.screen, box_color, box_rect)
            pygame.draw.rect(self.screen, self.text_color, box_rect, 2)

            # Draw arrow symbol using the special font
            key_surf = self.font_symbols.render(key_str, True, color)
            key_rect = key_surf.get_rect(center=box_rect.center)
            self.screen.blit(key_surf, key_rect)