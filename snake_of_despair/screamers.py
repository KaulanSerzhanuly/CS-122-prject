"""
Fear injection system with screamer effects and scheduling.
"""

import random
import time
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class ScreamerType(Enum):
    """Types of screamer effects."""
    IMAGE_FLASH = "image_flash"
    IMAGE_SEQUENCE = "image_sequence"
    VIDEO_CLIP = "video_clip"
    AUDIO_SCREAM = "audio_scream"


@dataclass
class ScreamerEffect:
    """Individual screamer effect configuration."""
    effect_type: ScreamerType
    duration: float
    intensity: float  # 0.0 to 1.0
    asset_path: Optional[str] = None
    audio_volume: float = 0.8
    visual_intensity: float = 0.8


class ScreamerPolicy(ABC):
    """Abstract base class for screamer trigger policies."""
    
    @abstractmethod
    def should_trigger(self, tension: float, current_time: float, 
                      last_trigger_time: float, cooldown_duration: float) -> bool:
        """Determine if a screamer should trigger."""
        pass


class ThresholdScreamerPolicy(ScreamerPolicy):
    """Screamer policy based on tension threshold."""
    
    def __init__(self, threshold: float = 75.0, jitter: float = 0.5):
        """Initialize threshold policy."""
        self.threshold = threshold
        self.jitter = jitter
    
    def should_trigger(self, tension: float, current_time: float,
                      last_trigger_time: float, cooldown_duration: float) -> bool:
        """Check if tension exceeds threshold and cooldown has passed."""
        if current_time - last_trigger_time < cooldown_duration:
            return False
        
        # Add jitter to threshold
        effective_threshold = self.threshold + random.uniform(-self.jitter * 10, self.jitter * 10)
        
        return tension >= effective_threshold


class StochasticScreamerPolicy(ScreamerPolicy):
    """Screamer policy with stochastic triggering."""
    
    def __init__(self, base_threshold: float = 60.0, probability_scale: float = 0.1):
        """Initialize stochastic policy."""
        self.base_threshold = base_threshold
        self.probability_scale = probability_scale
    
    def should_trigger(self, tension: float, current_time: float,
                      last_trigger_time: float, cooldown_duration: float) -> bool:
        """Check if screamer should trigger based on probability."""
        if current_time - last_trigger_time < cooldown_duration:
            return False
        
        if tension < self.base_threshold:
            return False
        
        # Calculate probability based on tension
        excess_tension = tension - self.base_threshold
        probability = min(0.5, excess_tension * self.probability_scale)
        
        return random.random() < probability


class ScreamerScheduler:
    """Manages screamer scheduling and cooldowns."""
    
    def __init__(self, policy: ScreamerPolicy, cooldown_duration: float = 10.0,
                 max_per_minute: int = 3):
        """Initialize screamer scheduler."""
        self.policy = policy
        self.cooldown_duration = cooldown_duration
        self.max_per_minute = max_per_minute
        self.last_trigger_time = 0.0
        self.trigger_times: List[float] = []
        self.effects: List[ScreamerEffect] = []
        self._setup_default_effects()
    
    def _setup_default_effects(self) -> None:
        """Setup default screamer effects."""
        self.effects = [
            ScreamerEffect(
                ScreamerType.IMAGE_FLASH,
                duration=0.1,
                intensity=0.8,
                visual_intensity=0.9
            ),
            ScreamerEffect(
                ScreamerType.AUDIO_SCREAM,
                duration=0.5,
                intensity=0.7,
                audio_volume=0.8
            ),
            ScreamerEffect(
                ScreamerType.IMAGE_SEQUENCE,
                duration=1.0,
                intensity=0.6,
                visual_intensity=0.7
            )
        ]
    
    def should_trigger_screamer(self, tension: float, current_time: float) -> bool:
        """Check if a screamer should trigger."""
        # Clean old trigger times
        self.trigger_times = [t for t in self.trigger_times if current_time - t < 60.0]
        
        # Check rate limit
        if len(self.trigger_times) >= self.max_per_minute:
            return False
        
        # Check policy
        return self.policy.should_trigger(
            tension, current_time, self.last_trigger_time, self.cooldown_duration
        )
    
    def trigger_screamer(self, current_time: float) -> Optional[ScreamerEffect]:
        """Trigger a screamer and return the effect."""
        if not self.should_trigger_screamer(0.0, current_time):  # We already checked tension
            return None
        
        # Select random effect
        effect = random.choice(self.effects)
        
        # Update tracking
        self.last_trigger_time = current_time
        self.trigger_times.append(current_time)
        
        return effect
    
    def get_cooldown_remaining(self, current_time: float) -> float:
        """Get remaining cooldown time."""
        elapsed = current_time - self.last_trigger_time
        return max(0.0, self.cooldown_duration - elapsed)


class ScreamerEffectPlayer(ABC):
    """Abstract base class for playing screamer effects."""
    
    @abstractmethod
    def play_effect(self, effect: ScreamerEffect) -> None:
        """Play a screamer effect."""
        pass
    
    @abstractmethod
    def stop_all_effects(self) -> None:
        """Stop all currently playing effects."""
        pass


class PygameScreamerPlayer(ScreamerEffectPlayer):
    """Pygame-based screamer effect player."""
    
    def __init__(self, screen, audio_manager, reduced_scare: bool = False):
        """Initialize pygame screamer player."""
        self.screen = screen
        self.audio_manager = audio_manager
        self.reduced_scare = reduced_scare
        self.active_effects: List[ScreamerEffect] = []
        self.effect_start_times: Dict[ScreamerEffect, float] = {}
    
    def play_effect(self, effect: ScreamerEffect) -> None:
        """Play a screamer effect."""
        if self.reduced_scare:
            effect = self._modify_for_reduced_scare(effect)
        
        self.active_effects.append(effect)
        self.effect_start_times[effect] = time.time()
        
        # Play effect based on type
        if effect.effect_type == ScreamerType.IMAGE_FLASH:
            self._play_image_flash(effect)
        elif effect.effect_type == ScreamerType.AUDIO_SCREAM:
            self._play_audio_scream(effect)
        elif effect.effect_type == ScreamerType.IMAGE_SEQUENCE:
            self._play_image_sequence(effect)
        elif effect.effect_type == ScreamerType.VIDEO_CLIP:
            self._play_video_clip(effect)
    
    def _modify_for_reduced_scare(self, effect: ScreamerEffect) -> ScreamerEffect:
        """Modify effect for reduced scare mode."""
        modified = ScreamerEffect(
            effect_type=effect.effect_type,
            duration=effect.duration * 2.0,  # Longer, gentler
            intensity=effect.intensity * 0.3,  # Much lower intensity
            asset_path=effect.asset_path,
            audio_volume=min(0.3, effect.audio_volume * 0.5),  # Lower volume
            visual_intensity=effect.visual_intensity * 0.4  # Much gentler visuals
        )
        return modified
    
    def _play_image_flash(self, effect: ScreamerEffect) -> None:
        """Play image flash effect."""
        # This would be implemented with pygame surface overlays
        pass
    
    def _play_audio_scream(self, effect: ScreamerEffect) -> None:
        """Play audio scream effect."""
        if self.audio_manager:
            self.audio_manager.play_sound("scream", effect.audio_volume)
    
    def _play_image_sequence(self, effect: ScreamerEffect) -> None:
        """Play image sequence effect."""
        # This would cycle through images rapidly
        pass
    
    def _play_video_clip(self, effect: ScreamerEffect) -> None:
        """Play video clip effect."""
        # This would play a short video overlay
        pass
    
    def update(self, current_time: float) -> None:
        """Update active effects and remove expired ones."""
        expired_effects = []
        
        for effect in self.active_effects:
            start_time = self.effect_start_times.get(effect, current_time)
            elapsed = current_time - start_time
            
            if elapsed >= effect.duration:
                expired_effects.append(effect)
        
        # Remove expired effects
        for effect in expired_effects:
            self.active_effects.remove(effect)
            if effect in self.effect_start_times:
                del self.effect_start_times[effect]
    
    def stop_all_effects(self) -> None:
        """Stop all currently playing effects."""
        self.active_effects.clear()
        self.effect_start_times.clear()
        if self.audio_manager:
            self.audio_manager.stop_all_sounds()


class ScreamerManager:
    """Main screamer management system."""
    
    def __init__(self, effect_player: ScreamerEffectPlayer, 
                 policy: ScreamerPolicy = None):
        """Initialize screamer manager."""
        self.effect_player = effect_player
        self.scheduler = ScreamerScheduler(
            policy or ThresholdScreamerPolicy(),
            cooldown_duration=10.0,
            max_per_minute=3
        )
        self.last_tension_check = 0.0
        self.tension_check_interval = 0.1  # Check every 100ms
    
    def update(self, tension: float, current_time: float) -> None:
        """Update screamer system."""
        # Update effect player
        self.effect_player.update(current_time)
        
        # Check if we should trigger a screamer
        if (current_time - self.last_tension_check >= self.tension_check_interval):
            if self.scheduler.should_trigger_screamer(tension, current_time):
                effect = self.scheduler.trigger_screamer(current_time)
                if effect:
                    self.effect_player.play_effect(effect)
            
            self.last_tension_check = current_time
    
    def get_cooldown_remaining(self, current_time: float) -> float:
        """Get remaining cooldown time."""
        return self.scheduler.get_cooldown_remaining(current_time)
    
    def force_trigger(self, effect_type: ScreamerType = None) -> None:
        """Force trigger a screamer (for testing)."""
        if effect_type:
            effect = ScreamerEffect(effect_type, 1.0, 1.0)
        else:
            effect = random.choice(self.scheduler.effects)
        
        self.effect_player.play_effect(effect)
    
    def stop_all(self) -> None:
        """Stop all screamer effects."""
        self.effect_player.stop_all_effects()
