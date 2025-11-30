"""
Screamer pipeline system - optimized for psychological impact.

4-Step Pipeline:
1. Glitch (80-120ms) - visual distortion to alert the brain
2. Freeze (20-40ms) - pause creates vulnerability  
3. Fullscreen screamer (200-350ms) - image + sound shock
4. Instant return - no fade, surreal confusion
"""

import pygame
import random
import os
from typing import List, Optional, Tuple


class ScreamerPipeline:
    """
    Handles the complete screamer effect with proper psychological timing.
    """
    
    def __init__(self, screen: pygame.Surface, asset_root: str = "assets", 
                 reduced_scare: bool = False):
        """Initialize the screamer pipeline."""
        self.screen = screen
        self.asset_root = asset_root
        self.reduced_scare = reduced_scare
        self.screen_width, self.screen_height = screen.get_size()
        
        # Load assets
        self.screamer_images: List[pygame.Surface] = []
        self.screamer_sounds: List[pygame.mixer.Sound] = []
        self._load_assets()
        
        # Timing settings (in milliseconds)
        if reduced_scare:
            self.glitch_duration = (40, 60)      # Shorter glitch
            self.freeze_duration = (10, 20)      # Shorter freeze
            self.screamer_duration = (150, 200)  # Shorter screamer
            self.volume = 0.3
        else:
            self.glitch_duration = (80, 120)     # Standard glitch
            self.freeze_duration = (20, 40)      # Standard freeze
            self.screamer_duration = (200, 350)  # Standard screamer
            self.volume = 0.8
    
    def _load_assets(self) -> None:
        """Load screamer images and sounds."""
        # Load images (1.webp through 8.webp)
        images_path = os.path.join(self.asset_root, "images")
        for i in range(1, 9):
            img_file = os.path.join(images_path, f"{i}.webp")
            if os.path.exists(img_file):
                try:
                    img = pygame.image.load(img_file).convert()
                    # Scale to screen size with slight zoom (1.05x for impact)
                    zoom = 1.05
                    scaled_size = (int(self.screen_width * zoom), 
                                   int(self.screen_height * zoom))
                    img = pygame.transform.scale(img, scaled_size)
                    self.screamer_images.append(img)
                except pygame.error as e:
                    print(f"Could not load {img_file}: {e}")
        
        # Load sounds (1.ogg through 8.ogg)
        audio_path = os.path.join(self.asset_root, "audio")
        for i in range(1, 9):
            snd_file = os.path.join(audio_path, f"{i}.ogg")
            if os.path.exists(snd_file):
                try:
                    snd = pygame.mixer.Sound(snd_file)
                    self.screamer_sounds.append(snd)
                except pygame.error as e:
                    print(f"Could not load {snd_file}: {e}")
        
        print(f"Loaded {len(self.screamer_images)} screamer images, {len(self.screamer_sounds)} sounds")
    
    def trigger(self) -> None:
        """
        Execute the full 4-step screamer pipeline.
        This blocks the game loop momentarily for maximum impact.
        """
        if not self.screamer_images or not self.screamer_sounds:
            return
        
        # Select random image and sound
        image = random.choice(self.screamer_images)
        sound = random.choice(self.screamer_sounds)
        sound.set_volume(self.volume)
        
        # Capture current screen for glitch effects
        current_screen = self.screen.copy()
        
        # === STEP 1: GLITCH (80-120ms) ===
        self._do_glitch(current_screen)
        
        # === STEP 2: FREEZE (20-40ms) ===
        self._do_freeze()
        
        # === STEP 3: FULLSCREEN SCREAMER (200-350ms) ===
        self._do_screamer(image, sound)
        
        # === STEP 4: INSTANT RETURN ===
        # Just return - the game loop will redraw normally
    
    def _do_glitch(self, current_screen: pygame.Surface) -> None:
        """Step 1: Visual glitch to alert the brain."""
        glitch_time = random.randint(*self.glitch_duration)
        glitch_type = random.choice(["invert", "shift", "flicker", "shake"])
        
        if glitch_type == "invert":
            # Invert colors
            inverted = current_screen.copy()
            pixels = pygame.surfarray.pixels3d(inverted)
            pixels[:] = 255 - pixels
            del pixels
            self.screen.blit(inverted, (0, 0))
            
        elif glitch_type == "shift":
            # Shift screen sideways
            shift = random.choice([-5, -3, 3, 5])
            self.screen.fill((0, 0, 0))
            self.screen.blit(current_screen, (shift, 0))
            
        elif glitch_type == "flicker":
            # Flash between red and current
            red_overlay = pygame.Surface(self.screen.get_size())
            red_overlay.fill((255, 0, 0))
            red_overlay.set_alpha(100)
            self.screen.blit(current_screen, (0, 0))
            self.screen.blit(red_overlay, (0, 0))
            
        elif glitch_type == "shake":
            # Camera shake
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            self.screen.fill((0, 0, 0))
            self.screen.blit(current_screen, (offset_x, offset_y))
        
        pygame.display.flip()
        pygame.time.delay(glitch_time)
    
    def _do_freeze(self) -> None:
        """Step 2: Brief freeze to create vulnerability."""
        freeze_time = random.randint(*self.freeze_duration)
        pygame.time.delay(freeze_time)
    
    def _do_screamer(self, image: pygame.Surface, sound: pygame.mixer.Sound) -> None:
        """Step 3: The actual screamer - fullscreen image + sound."""
        screamer_time = random.randint(*self.screamer_duration)
        
        # Center the slightly zoomed image (creates zoom-in effect)
        img_width, img_height = image.get_size()
        x = (self.screen_width - img_width) // 2
        y = (self.screen_height - img_height) // 2
        
        # Show image
        self.screen.blit(image, (x, y))
        pygame.display.flip()
        
        # Micro delay before sound (30ms) - boosts shock
        pygame.time.delay(30)
        
        # Play sound
        sound.play()
        
        # Hold the screamer
        pygame.time.delay(screamer_time - 30)


class ScreamerManager:
    """
    Manages screamer triggering with random chance and cooldowns.
    """
    
    def __init__(self, screen: pygame.Surface, asset_root: str = "assets",
                 reduced_scare: bool = False):
        """Initialize screamer manager."""
        self.pipeline = ScreamerPipeline(screen, asset_root, reduced_scare)
        self.reduced_scare = reduced_scare
        
        # Random trigger settings
        # ~0.0004 = roughly once every few minutes at 60fps
        self.random_trigger_chance = 0.0002 if not reduced_scare else 0.0001
        
        # Cooldown to prevent spam (in seconds)
        self.cooldown_duration = 30.0 if not reduced_scare else 60.0
        self.last_trigger_time = 0.0
    
    def update(self, current_time: float) -> bool:
        """
        Check for random screamer trigger.
        Call this every game tick.
        Returns True if screamer was triggered.
        """
        # Check cooldown
        if current_time - self.last_trigger_time < self.cooldown_duration:
            return False
        
        # Random trigger check
        if random.random() < self.random_trigger_chance:
            self.force_trigger()
            self.last_trigger_time = current_time
            return True
        
        return False
    
    def force_trigger(self) -> None:
        """Force trigger a screamer immediately (for danger zones)."""
        self.pipeline.trigger()
    
    def trigger_from_danger_zone(self, current_time: float) -> None:
        """Trigger screamer from danger zone - always triggers, updates cooldown."""
        self.pipeline.trigger()
        self.last_trigger_time = current_time


# Legacy compatibility classes (kept for any old code that might reference them)
class ScreamerType:
    IMAGE_FLASH = "image_flash"
    AUDIO_SCREAM = "audio_scream"

class ThresholdScreamerPolicy:
    def __init__(self, threshold: float = 0, jitter: float = 0):
        pass

class PygameScreamerPlayer:
    def __init__(self, screen, audio_manager, reduced_scare: bool = False):
        pass
