"""
Event logging and deterministic seed handling.
"""

import csv
import time
import random
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GameEvent:
    """Individual game event for logging."""
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    seed: Optional[int] = None
    session_id: str = ""


class GameLogger:
    """Logs game events to CSV file."""
    
    def __init__(self, log_file: str = "game_log.csv", session_id: str = None):
        """Initialize game logger."""
        self.log_file = log_file
        self.session_id = session_id or self._generate_session_id()
        self.events: List[GameEvent] = []
        self.start_time = time.time()
        
        # Initialize log file with headers
        self._initialize_log_file()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"session_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _initialize_log_file(self) -> None:
        """Initialize log file with headers."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'session_id', 'event_type', 'data', 'seed'
                ])
    
    def log_event(self, event_type: str, data: Dict[str, Any], seed: int = None) -> None:
        """Log a game event."""
        event = GameEvent(
            timestamp=time.time(),
            event_type=event_type,
            data=data,
            seed=seed,
            session_id=self.session_id
        )
        
        self.events.append(event)
        self._write_event_to_file(event)
    
    def _write_event_to_file(self, event: GameEvent) -> None:
        """Write event to CSV file."""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                event.timestamp,
                event.session_id,
                event.event_type,
                str(event.data),
                event.seed
            ])
    
    def log_game_start(self, config: Dict[str, Any]) -> None:
        """Log game start event."""
        self.log_event("game_start", {
            "config": config,
            "session_duration": 0.0
        })
    
    def log_game_end(self, final_score: int, cause_of_death: str) -> None:
        """Log game end event."""
        session_duration = time.time() - self.start_time
        self.log_event("game_end", {
            "final_score": final_score,
            "cause_of_death": cause_of_death,
            "session_duration": session_duration
        })
    
    def log_tension_peak(self, tension: float, trigger_type: str) -> None:
        """Log tension peak event."""
        self.log_event("tension_peak", {
            "tension_level": tension,
            "trigger_type": trigger_type
        })
    
    def log_screamer_trigger(self, screamer_type: str, tension: float) -> None:
        """Log screamer trigger event."""
        self.log_event("screamer_trigger", {
            "screamer_type": screamer_type,
            "tension_level": tension
        })
    
    def log_apple_eaten(self, score: int, snake_length: int) -> None:
        """Log apple eaten event."""
        self.log_event("apple_eaten", {
            "score": score,
            "snake_length": snake_length
        })
    
    def log_collision(self, collision_type: str, position: tuple) -> None:
        """Log collision event."""
        self.log_event("collision", {
            "collision_type": collision_type,
            "position": position
        })
    
    def log_settings_change(self, setting: str, old_value: Any, new_value: Any) -> None:
        """Log settings change event."""
        self.log_event("settings_change", {
            "setting": setting,
            "old_value": str(old_value),
            "new_value": str(new_value)
        })
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        session_duration = time.time() - self.start_time
        
        # Count events by type
        event_counts = {}
        for event in self.events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "session_duration": session_duration,
            "total_events": len(self.events),
            "event_counts": event_counts,
            "start_time": self.start_time
        }


class SeedManager:
    """Manages deterministic random seeds."""
    
    def __init__(self, seed: int = None):
        """Initialize seed manager."""
        self.seed = seed
        self.original_seed = seed
        self.random_state = None
        
        if seed is not None:
            self.set_seed(seed)
    
    def set_seed(self, seed: int) -> None:
        """Set random seed for deterministic behavior."""
        self.seed = seed
        random.seed(seed)
        self.random_state = random.getstate()
    
    def reset_to_seed(self) -> None:
        """Reset random state to original seed."""
        if self.seed is not None:
            random.seed(self.seed)
            self.random_state = random.getstate()
    
    def save_state(self) -> None:
        """Save current random state."""
        self.random_state = random.getstate()
    
    def restore_state(self) -> None:
        """Restore saved random state."""
        if self.random_state is not None:
            random.setstate(self.random_state)
    
    def get_deterministic_value(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Get deterministic random value."""
        return random.uniform(min_val, max_val)
    
    def get_deterministic_int(self, min_val: int, max_val: int) -> int:
        """Get deterministic random integer."""
        return random.randint(min_val, max_val)
    
    def get_deterministic_choice(self, choices: List[Any]) -> Any:
        """Get deterministic random choice."""
        return random.choice(choices)


class TelemetryCollector:
    """Collects lightweight session metrics."""
    
    def __init__(self, logger: GameLogger):
        """Initialize telemetry collector."""
        self.logger = logger
        self.metrics: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def record_metric(self, name: str, value: Any) -> None:
        """Record a metric value."""
        self.metrics[name] = value
    
    def increment_counter(self, name: str, amount: int = 1) -> None:
        """Increment a counter metric."""
        self.metrics[name] = self.metrics.get(name, 0) + amount
    
    def record_tension_metrics(self, tension: float, peak_tension: float) -> None:
        """Record tension-related metrics."""
        self.record_metric("current_tension", tension)
        self.record_metric("peak_tension", peak_tension)
        self.record_metric("tension_level", self._get_tension_level(tension))
    
    def record_performance_metrics(self, fps: float, frame_time: float) -> None:
        """Record performance metrics."""
        self.record_metric("fps", fps)
        self.record_metric("frame_time_ms", frame_time * 1000)
    
    def record_gameplay_metrics(self, score: int, snake_length: int, apples_eaten: int) -> None:
        """Record gameplay metrics."""
        self.record_metric("score", score)
        self.record_metric("snake_length", snake_length)
        self.record_metric("apples_eaten", apples_eaten)
    
    def _get_tension_level(self, tension: float) -> str:
        """Get tension level description."""
        if tension < 20:
            return "calm"
        elif tension < 40:
            return "nervous"
        elif tension < 60:
            return "tense"
        elif tension < 80:
            return "anxious"
        else:
            return "terrified"
    
    def get_session_report(self) -> Dict[str, Any]:
        """Get comprehensive session report."""
        session_duration = time.time() - self.start_time
        
        report = {
            "session_id": self.logger.session_id,
            "session_duration": session_duration,
            "metrics": self.metrics.copy(),
            "timestamp": time.time()
        }
        
        # Add derived metrics
        if "score" in self.metrics and session_duration > 0:
            report["score_per_minute"] = (self.metrics["score"] / session_duration) * 60
        
        if "apples_eaten" in self.metrics and session_duration > 0:
            report["apples_per_minute"] = (self.metrics["apples_eaten"] / session_duration) * 60
        
        return report
    
    def log_session_report(self) -> None:
        """Log session report to file."""
        report = self.get_session_report()
        self.logger.log_event("session_report", report)


class DebugLogger:
    """Debug logging for development."""
    
    def __init__(self, enabled: bool = False):
        """Initialize debug logger."""
        self.enabled = enabled
        self.debug_file = "debug.log"
        self.debug_entries: List[str] = []
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log debug message."""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{timestamp}] [{level}] {message}"
        self.debug_entries.append(entry)
        
        # Write to file
        with open(self.debug_file, 'a') as f:
            f.write(entry + "\n")
    
    def log_tension_calculation(self, sources: Dict[str, float], total: float) -> None:
        """Log tension calculation details."""
        if not self.enabled:
            return
        
        sources_str = ", ".join([f"{k}: {v:.2f}" for k, v in sources.items()])
        self.log(f"Tension calculation - Sources: {sources_str}, Total: {total:.2f}")
    
    def log_screamer_decision(self, tension: float, threshold: float, cooldown: bool) -> None:
        """Log screamer trigger decision."""
        if not self.enabled:
            return
        
        decision = "TRIGGER" if tension >= threshold and not cooldown else "NO TRIGGER"
        self.log(f"Screamer decision - Tension: {tension:.2f}, Threshold: {threshold:.2f}, "
                f"Cooldown: {cooldown}, Decision: {decision}")
    
    def clear_log(self) -> None:
        """Clear debug log."""
        self.debug_entries.clear()
        if os.path.exists(self.debug_file):
            os.remove(self.debug_file)
