"""
Asset loading and management with fallbacks and safety defaults.
"""

import os
import pygame
import random
from typing import Dict, Optional, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import io


class AssetManager:
    """Manages loading and caching of game assets."""
    
    def __init__(self, asset_root: str = "assets", reduced_scare: bool = False):
        """Initialize asset manager."""
        self.asset_root = asset_root
        self.reduced_scare = reduced_scare
        self.cache: Dict[str, Any] = {}
        self.audio_manager: AudioManager
        self.image_manager: ImageManager
        self.video_manager: VideoManager

        # Initialize sub-managers
        self.audio_manager = AudioManager(self, reduced_scare)
        self.image_manager = ImageManager(self, reduced_scare)
        self.video_manager = VideoManager(self, reduced_scare)
    
    def get_asset_path(self, category: str, filename: str) -> str:
        """Get full path to asset file."""
        return os.path.join(self.asset_root, category, filename)
    
    def asset_exists(self, category: str, filename: str) -> bool:
        """Check if asset file exists."""
        path = self.get_asset_path(category, filename)
        return os.path.exists(path)
    
    def load_asset(self, category: str, filename: str, **kwargs) -> Any:
        """Load asset with caching."""
        cache_key = f"{category}/{filename}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Load based on category
        if category == "audio":
            asset = self.audio_manager.load_audio(filename, **kwargs)
        elif category == "images":
            asset = self.image_manager.load_image(filename, **kwargs)
        elif category == "video":
            asset = self.video_manager.load_video(filename, **kwargs)
        else:
            raise ValueError(f"Unknown asset category: {category}")
        
        self.cache[cache_key] = asset
        return asset
    
    def clear_cache(self) -> None:
        """Clear asset cache."""
        self.cache.clear()
    
    def get_available_assets(self, category: str) -> List[str]:
        """Get list of available assets in category."""
        category_path = os.path.join(self.asset_root, category)
        if not os.path.exists(category_path):
            return []
        
        return [f for f in os.listdir(category_path) 
                if os.path.isfile(os.path.join(category_path, f))]


class AudioManager:
    """Manages audio assets and playback."""
    
    def __init__(self, asset_manager: AssetManager, reduced_scare: bool = False):
        """Initialize audio manager."""
        self.asset_manager = asset_manager
        self.reduced_scare = reduced_scare
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.master_volume = 0.7
        self.volume_limits = {
            "max_volume": 0.8 if not reduced_scare else 0.3,
            "peak_limit": 0.9 if not reduced_scare else 0.5
        }
    
    def load_audio(self, filename: str, volume: float = 1.0) -> Optional[pygame.mixer.Sound]:
        """Load audio file with fallback generation."""
        if self.asset_manager.asset_exists("audio", filename):
            try:
                path = self.asset_manager.get_asset_path("audio", filename)
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume * self.master_volume)
                return sound
            except pygame.error:
                pass
        
        # Generate fallback audio
        return self._generate_fallback_audio(filename, volume)
    
    def _generate_fallback_audio(self, filename: str, volume: float) -> pygame.mixer.Sound:
        """Generate fallback audio for missing files."""
        # Generate simple sine wave tones
        sample_rate = 22050
        duration = 0.5
        
        if "scream" in filename.lower():
            # Generate a harsh tone for scream
            frequency = 800
            samples = self._generate_sine_wave(frequency, sample_rate, duration)
        elif "beep" in filename.lower():
            # Generate a simple beep
            frequency = 440
            samples = self._generate_sine_wave(frequency, sample_rate, duration)
        else:
            # Default tone
            frequency = 220
            samples = self._generate_sine_wave(frequency, sample_rate, duration)
        
        # Apply volume limits
        volume = min(volume, self.volume_limits["max_volume"])
        samples = (samples * volume).astype('int16')
        
        # Create pygame sound
        sound = pygame.sndarray.make_sound(samples)
        return sound
    
    def _generate_sine_wave(self, frequency: int, sample_rate: int, duration: float) -> 'numpy.ndarray':
        """Generate sine wave audio data."""
        import numpy as np
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope to avoid clicks
        envelope = np.exp(-t * 3)  # Exponential decay
        wave *= envelope
        
        return (wave * 32767).astype('int16')
    
    def play_sound(self, sound_name: str, volume: float = 1.0) -> None:
        """Play a sound by name."""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume * self.master_volume)
            sound.play()
    
    def stop_all_sounds(self) -> None:
        """Stop all playing sounds."""
        pygame.mixer.stop()


class ImageManager:
    """Manages image assets and generation."""
    
    def __init__(self, asset_manager: AssetManager, reduced_scare: bool = False):
        """Initialize image manager."""
        self.asset_manager = asset_manager
        self.reduced_scare = reduced_scare
        self.images: Dict[str, pygame.Surface] = {}
        self.safe_colors = {
            "flash": (200, 200, 200) if reduced_scare else (255, 255, 255),
            "overlay": (50, 50, 50, 100) if reduced_scare else (0, 0, 0, 128)
        }
    
    def load_image(self, filename: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """Load image with fallback generation."""
        if self.asset_manager.asset_exists("images", filename):
            try:
                path = self.asset_manager.get_asset_path("images", filename)
                image = pygame.image.load(path)
                if size:
                    image = pygame.transform.scale(image, size)
                return image
            except pygame.error:
                pass
        
        # Generate fallback image
        return self._generate_fallback_image(filename, size)
    
    def _generate_fallback_image(self, filename: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """Generate fallback image for missing files."""
        if size is None:
            size = (100, 100)
        
        # Create surface
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        if "flash" in filename.lower():
            # Generate flash overlay
            color = self.safe_colors["flash"]
            surface.fill(color)
        elif "overlay" in filename.lower():
            # Generate overlay
            color = self.safe_colors["overlay"]
            surface.fill(color)
        elif "screamer" in filename.lower():
            # Generate screamer image
            self._draw_screamer_image(surface)
        else:
            # Default placeholder
            self._draw_placeholder_image(surface)
        
        return surface
    
    def _draw_screamer_image(self, surface: pygame.Surface) -> None:
        """Draw a simple screamer image."""
        width, height = surface.get_size()
        
        # Draw simple pattern
        for i in range(0, width, 20):
            for j in range(0, height, 20):
                color = (255, 0, 0) if (i + j) % 40 == 0 else (0, 0, 0)
                pygame.draw.rect(surface, color, (i, j, 20, 20))
    
    def _draw_placeholder_image(self, surface: pygame.Surface) -> None:
        """Draw placeholder image."""
        width, height = surface.get_size()
        
        # Draw simple border
        pygame.draw.rect(surface, (100, 100, 100), (0, 0, width, height), 2)
        
        # Draw placeholder text
        font = pygame.font.Font(None, 24)
        text = font.render("PLACEHOLDER", True, (150, 150, 150))
        text_rect = text.get_rect(center=(width//2, height//2))
        surface.blit(text, text_rect)


class VideoManager:
    """Manages video assets and playback."""
    
    def __init__(self, asset_manager: AssetManager, reduced_scare: bool = False):
        """Initialize video manager."""
        self.asset_manager = asset_manager
        self.reduced_scare = reduced_scare
        self.videos: Dict[str, Any] = {}
    
    def load_video(self, filename: str) -> Optional[Any]:
        """Load video file with fallback generation."""
        if self.asset_manager.asset_exists("video", filename):
            try:
                path = self.asset_manager.get_asset_path("video", filename)
                # This would use moviepy or similar for video loading
                # For now, return None as we're using placeholders
                return None
            except Exception:
                pass
        
        # Generate fallback video (static image sequence)
        return self._generate_fallback_video(filename)
    
    def _generate_fallback_video(self, filename: str) -> List[pygame.Surface]:
        """Generate fallback video as image sequence."""
        # Create a simple animation as image sequence
        frames = []
        for i in range(10):  # 10 frames
            surface = pygame.Surface((200, 200))
            # Simple pulsing effect
            intensity = int(128 + 127 * (i / 10))
            color = (intensity, 0, 0)
            surface.fill(color)
            frames.append(surface)
        
        return frames


class AssetFallbackGenerator:
    """Generates fallback assets when originals are missing."""
    
    @staticmethod
    def generate_audio_beep(frequency: int = 440, duration: float = 0.5) -> pygame.mixer.Sound:
        """Generate a simple beep sound."""
        import numpy as np
        
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope
        envelope = np.exp(-t * 2)
        wave *= envelope
        
        samples = (wave * 32767).astype('int16')
        return pygame.sndarray.make_sound(samples)
    
    @staticmethod
    def generate_flash_image(size: Tuple[int, int] = (100, 100), 
                           color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
        """Generate a flash overlay image."""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        return surface
    
    @staticmethod
    def generate_overlay_image(size: Optional[Tuple[int, int]] = (100, 100),
                             color: Tuple[int, int, int, int] = (0, 0, 0, 128)) -> pygame.Surface:
        """Generate an overlay image."""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        return surface
