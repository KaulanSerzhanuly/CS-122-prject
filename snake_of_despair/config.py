"""
Configuration constants and tunable parameters for Snake of Despair.
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
import random


@dataclass
class Config:
    """Main configuration class for the game."""
    
    # Core game settings
    seed: int = None
    reduced_scare: bool = False
    difficulty: str = "normal"
    window_size: Tuple[int, int] = (960, 720)
    mute: bool = False
    debug: bool = False
    
    # Grid and movement
    GRID_SIZE: int = 20
    GRID_WIDTH: int = 48
    GRID_HEIGHT: int = 36
    
    # Game timing
    FPS: int = 60
    BASE_SPEED: float = 0.15  # seconds per move
    SPEED_INCREASE: float = 0.01  # speed increase per apple
    
    # Tension system
    TENSION_MAX: float = 100.0
    TENSION_DECAY_RATE: float = 0.5  # per second
    TENSION_COOLDOWN: float = 3.0  # seconds after trigger
    
    # Screamer system
    SCREAMER_THRESHOLD: float = 75.0
    SCREAMER_COOLDOWN: float = 10.0  # minimum seconds between screamers
    SCREAMER_MAX_PER_MINUTE: int = 3
    SCREAMER_JITTER: float = 0.5  # ±seconds timing jitter
    
    # Audio settings
    MASTER_VOLUME: float = 0.7
    REDUCED_SCARE_VOLUME: float = 0.3
    REDUCED_SCARE_PEAK_LIMIT: float = 0.5
    
    # Visual settings
    FLASH_DURATION: float = 0.1
    REDUCED_SCARE_FLASH_DURATION: float = 0.3
    FADE_DURATION: float = 0.5
    
    def __post_init__(self):
        """Initialize derived values after object creation."""
        if self.seed is not None:
            random.seed(self.seed)
        
        # Difficulty multipliers
        self.difficulty_multipliers = {
            "easy": {"speed": 0.7, "tension": 0.5, "screamers": 0.3},
            "normal": {"speed": 1.0, "tension": 1.0, "screamers": 1.0},
            "hard": {"speed": 1.3, "tension": 1.5, "screamers": 1.5}
        }
        
        # Apply difficulty
        mult = self.difficulty_multipliers[self.difficulty]
        self.BASE_SPEED *= mult["speed"]
        self.TENSION_DECAY_RATE *= mult["tension"]
        self.SCREAMER_THRESHOLD *= (1.0 / mult["screamers"])
        
        # Reduced scare adjustments
        if self.reduced_scare:
            self.SCREAMER_THRESHOLD *= 1.5  # Higher threshold
            self.SCREAMER_COOLDOWN *= 2.0  # Longer cooldown
            self.FLASH_DURATION = self.REDUCED_SCARE_FLASH_DURATION


# Tension contribution weights
TENSION_WEIGHTS = {
    "wall_proximity": 2.0,
    "tail_proximity": 3.0,
    "speed": 1.0,
    "score_streak": 0.5,
    "time_without_apple": 0.3,
    "last_second_turn": 2.0,
    "cornering": 1.5
}

# Screamer effect types
SCREAMER_TYPES = [
    "image_flash",
    "image_sequence", 
    "video_clip",
    "audio_scream"
]

# Accessibility settings
ACCESSIBILITY_SETTINGS = {
    "reduced_motion": False,
    "high_contrast": False,
    "large_text": False,
    "screen_reader": False
}

# Asset paths
ASSET_PATHS = {
    "audio": "assets/audio/",
    "images": "assets/images/", 
    "video": "assets/video/"
}

# Default colors (reduced flash palette)
DEFAULT_COLORS = {
    "background": (20, 20, 20),
    "snake": (0, 255, 0),
    "snake_head": (0, 200, 0),
    "apple": (255, 0, 0),
    "wall": (100, 100, 100),
    "text": (255, 255, 255),
    "text_dim": (150, 150, 150),
    "overlay": (0, 0, 0, 128),
    "flash": (255, 255, 255),
    "flash_reduced": (200, 200, 200)
}

# Reduced scare color palette
REDUCED_SCARE_COLORS = {
    "flash": (150, 150, 150),
    "overlay": (50, 50, 50, 100),
    "snake": (0, 200, 0),
    "snake_head": (0, 150, 0)
}
