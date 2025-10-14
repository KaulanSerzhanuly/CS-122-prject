"""
Centralized color management for Snake of Despair.
Includes both normal and reduced flash palettes for accessibility.
"""

from typing import Dict, Tuple, Any
from .config import DEFAULT_COLORS, REDUCED_SCARE_COLORS


class ColorManager:
    """Manages color schemes and accessibility options."""
    
    def __init__(self, reduced_scare: bool = False):
        """Initialize color manager with accessibility settings."""
        self.reduced_scare = reduced_scare
        self._colors = self._get_color_scheme()
    
    def _get_color_scheme(self) -> Dict[str, Any]:
        """Get appropriate color scheme based on accessibility settings."""
        if self.reduced_scare:
            # Merge default colors with reduced scare overrides
            colors = DEFAULT_COLORS.copy()
            colors.update(REDUCED_SCARE_COLORS)
            return colors
        return DEFAULT_COLORS.copy()
    
    def get_color(self, name: str) -> Tuple[int, int, int, int]:
        """Get color by name, with alpha channel support."""
        color = self._colors.get(name, (255, 255, 255, 255))
        
        # Ensure alpha channel
        if len(color) == 3:
            return (*color, 255)
        return color
    
    def get_rgb(self, name: str) -> Tuple[int, int, int]:
        """Get RGB color without alpha channel."""
        r, g, b, a = self.get_color(name)
        return (r, g, b)
    
    def get_rgba(self, name: str) -> Tuple[int, int, int, int]:
        """Get RGBA color with alpha channel."""
        return self.get_color(name)
    
    def set_reduced_scare(self, enabled: bool) -> None:
        """Toggle reduced scare mode and update colors."""
        if self.reduced_scare != enabled:
            self.reduced_scare = enabled
            self._colors = self._get_color_scheme()
    
    def get_flash_color(self) -> Tuple[int, int, int, int]:
        """Get appropriate flash color based on accessibility settings."""
        return self.get_color("flash")
    
    def get_overlay_color(self) -> Tuple[int, int, int, int]:
        """Get overlay color for effects."""
        return self.get_color("overlay")
    
    def get_snake_colors(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Get snake body and head colors."""
        body = self.get_rgb("snake")
        head = self.get_rgb("snake_head")
        return body, head
    
    def get_apple_color(self) -> Tuple[int, int, int]:
        """Get apple color."""
        return self.get_rgb("apple")
    
    def get_background_color(self) -> Tuple[int, int, int]:
        """Get background color."""
        return self.get_rgb("background")
    
    def get_text_color(self, dim: bool = False) -> Tuple[int, int, int]:
        """Get text color, optionally dimmed."""
        return self.get_rgb("text_dim" if dim else "text")
    
    def get_wall_color(self) -> Tuple[int, int, int]:
        """Get wall color."""
        return self.get_rgb("wall")


# Predefined color schemes for different moods
MOOD_COLORS = {
    "normal": {
        "snake": (0, 255, 0),
        "apple": (255, 0, 0),
        "background": (20, 20, 20)
    },
    "tense": {
        "snake": (255, 255, 0),
        "apple": (255, 100, 0),
        "background": (30, 10, 10)
    },
    "scared": {
        "snake": (255, 0, 0),
        "apple": (255, 0, 100),
        "background": (40, 0, 0)
    }
}


def get_mood_colors(mood: str, reduced_scare: bool = False) -> Dict[str, Tuple[int, int, int]]:
    """Get color scheme for specific mood."""
    colors = MOOD_COLORS.get(mood, MOOD_COLORS["normal"])
    
    if reduced_scare:
        # Mute colors for reduced scare mode
        muted = {}
        for key, (r, g, b) in colors.items():
            muted[key] = (r // 2, g // 2, b // 2)
        return muted
    
    return colors
