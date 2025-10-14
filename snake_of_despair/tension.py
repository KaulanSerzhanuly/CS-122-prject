"""
Tension meter system with adaptive contributions and decay.
"""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class TensionSource(Enum):
    """Sources of tension in the game."""
    WALL_PROXIMITY = "wall_proximity"
    TAIL_PROXIMITY = "tail_proximity"
    SPEED = "speed"
    SCORE_STREAK = "score_streak"
    TIME_WITHOUT_APPLE = "time_without_apple"
    LAST_SECOND_TURN = "last_second_turn"
    CORNERING = "cornering"


@dataclass
class TensionEvent:
    """Individual tension contribution event."""
    source: TensionSource
    value: float
    timestamp: float
    duration: float = 1.0  # How long this contribution lasts


class TensionMeter:
    """Manages tension calculation and decay."""
    
    def __init__(self, max_tension: float = 100.0, decay_rate: float = 0.5):
        """Initialize tension meter."""
        self.max_tension = max_tension
        self.decay_rate = decay_rate
        self.current_tension = 0.0
        self.last_update_time = time.time()
        self.events: List[TensionEvent] = []
        self.cooldown_until = 0.0
        self.weights = {
            TensionSource.WALL_PROXIMITY: 2.0,
            TensionSource.TAIL_PROXIMITY: 3.0,
            TensionSource.SPEED: 1.0,
            TensionSource.SCORE_STREAK: 0.5,
            TensionSource.TIME_WITHOUT_APPLE: 0.3,
            TensionSource.LAST_SECOND_TURN: 2.0,
            TensionSource.CORNERING: 1.5
        }
    
    def add_tension(self, source: TensionSource, value: float, duration: float = 1.0) -> None:
        """Add tension from a specific source."""
        current_time = time.time()
        event = TensionEvent(source, value, current_time, duration)
        self.events.append(event)
    
    def update(self) -> float:
        """Update tension meter and return current value."""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        
        # Calculate total tension from active events
        total_contribution = 0.0
        active_events = []
        
        for event in self.events:
            age = current_time - event.timestamp
            
            if age < event.duration:
                # Event is still active
                weight = self.weights.get(event.source, 1.0)
                # Apply decay over time within the event
                decay_factor = 1.0 - (age / event.duration)
                contribution = event.value * weight * decay_factor
                total_contribution += contribution
                active_events.append(event)
        
        # Update events list
        self.events = active_events
        
        # Apply tension contribution
        self.current_tension += total_contribution
        
        # Apply natural decay
        self.current_tension -= self.decay_rate * delta_time
        
        # Clamp to valid range
        self.current_tension = max(0.0, min(self.max_tension, self.current_tension))
        
        # Update timestamp
        self.last_update_time = current_time
        
        return self.current_tension
    
    def get_tension(self) -> float:
        """Get current tension level."""
        return self.current_tension
    
    def get_tension_percentage(self) -> float:
        """Get tension as percentage of maximum."""
        return (self.current_tension / self.max_tension) * 100.0
    
    def is_in_cooldown(self) -> bool:
        """Check if tension system is in cooldown."""
        return time.time() < self.cooldown_until
    
    def start_cooldown(self, duration: float) -> None:
        """Start cooldown period."""
        self.cooldown_until = time.time() + duration
    
    def reset(self) -> None:
        """Reset tension meter."""
        self.current_tension = 0.0
        self.events.clear()
        self.cooldown_until = 0.0
        self.last_update_time = time.time()
    
    def get_tension_level(self) -> str:
        """Get descriptive tension level."""
        percentage = self.get_tension_percentage()
        
        if percentage < 20:
            return "calm"
        elif percentage < 40:
            return "nervous"
        elif percentage < 60:
            return "tense"
        elif percentage < 80:
            return "anxious"
        else:
            return "terrified"


class TensionAnalyzer:
    """Analyzes tension patterns and provides insights."""
    
    def __init__(self, tension_meter: TensionMeter):
        """Initialize tension analyzer."""
        self.tension_meter = tension_meter
        self.history: List[float] = []
        self.peak_threshold = 0.8  # 80% of max tension
        self.recent_peaks: List[float] = []
    
    def analyze_patterns(self) -> Dict[str, any]:
        """Analyze tension patterns and return insights."""
        current_tension = self.tension_meter.get_tension()
        self.history.append(current_tension)
        
        # Keep only recent history (last 60 seconds at 60 FPS)
        if len(self.history) > 3600:
            self.history = self.history[-3600:]
        
        # Detect peaks
        if current_tension > self.tension_meter.max_tension * self.peak_threshold:
            self.recent_peaks.append(time.time())
            # Keep only recent peaks (last 60 seconds)
            self.recent_peaks = [p for p in self.recent_peaks if time.time() - p < 60.0]
        
        return {
            "current_tension": current_tension,
            "tension_level": self.tension_meter.get_tension_level(),
            "recent_peaks": len(self.recent_peaks),
            "trend": self._calculate_trend(),
            "volatility": self._calculate_volatility()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate tension trend over recent history."""
        if len(self.history) < 10:
            return "stable"
        
        recent = self.history[-10:]
        older = self.history[-20:-10] if len(self.history) >= 20 else self.history[:-10]
        
        if not older:
            return "stable"
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        if recent_avg > older_avg * 1.1:
            return "rising"
        elif recent_avg < older_avg * 0.9:
            return "falling"
        else:
            return "stable"
    
    def _calculate_volatility(self) -> float:
        """Calculate tension volatility (0.0 = stable, 1.0 = very volatile)."""
        if len(self.history) < 10:
            return 0.0
        
        recent = self.history[-10:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        volatility = (variance ** 0.5) / self.tension_meter.max_tension
        
        return min(1.0, volatility)


class TensionContributor:
    """Helper class to calculate tension contributions from game state."""
    
    def __init__(self, tension_meter: TensionMeter):
        """Initialize tension contributor."""
        self.tension_meter = tension_meter
        self.last_turn_time = 0.0
        self.turn_count = 0
        self.score_streak = 0
    
    def contribute_from_snake_state(self, snake, apple_manager, current_time: float) -> None:
        """Calculate and add tension contributions from snake state."""
        # Wall proximity
        wall_proximity = snake.get_proximity_to_walls()
        if wall_proximity > 0.3:
            self.tension_meter.add_tension(
                TensionSource.WALL_PROXIMITY,
                wall_proximity * 20.0,
                duration=2.0
            )
        
        # Tail proximity
        tail_proximity = snake.get_proximity_to_tail()
        if tail_proximity > 0.2:
            self.tension_meter.add_tension(
                TensionSource.TAIL_PROXIMITY,
                tail_proximity * 30.0,
                duration=1.5
            )
        
        # Speed factor
        speed_factor = snake.get_speed_factor()
        if speed_factor > 1.2:
            self.tension_meter.add_tension(
                TensionSource.SPEED,
                (speed_factor - 1.0) * 10.0,
                duration=1.0
            )
        
        # Time without apple
        time_without = apple_manager.get_time_without_apple(current_time)
        if time_without > 5.0:
            urgency = apple_manager.get_spawn_urgency(current_time)
            self.tension_meter.add_tension(
                TensionSource.TIME_WITHOUT_APPLE,
                urgency * 15.0,
                duration=2.0
            )
        
        # Cornering detection
        cornering = snake.get_cornering_factor()
        if cornering > 0.3:
            self.tension_meter.add_tension(
                TensionSource.CORNERING,
                cornering * 25.0,
                duration=1.0
            )
    
    def contribute_from_turn(self, current_time: float) -> None:
        """Add tension from recent turn."""
        self.turn_count += 1
        self.last_turn_time = current_time
        
        # Add tension for rapid turning
        if self.turn_count > 3:
            self.tension_meter.add_tension(
                TensionSource.LAST_SECOND_TURN,
                min(20.0, self.turn_count * 5.0),
                duration=0.5
            )
    
    def contribute_from_score(self, score_increase: int) -> None:
        """Add tension from score increase."""
        self.score_streak += 1
        self.tension_meter.add_tension(
            TensionSource.SCORE_STREAK,
            min(15.0, self.score_streak * 2.0),
            duration=1.0
        )
    
    def reset_turn_count(self) -> None:
        """Reset turn counter."""
        self.turn_count = 0
    
    def reset_score_streak(self) -> None:
        """Reset score streak."""
        self.score_streak = 0
