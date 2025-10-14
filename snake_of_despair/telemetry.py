"""
Lightweight session metrics collection and analysis.
"""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque


@dataclass
class SessionMetrics:
    """Session metrics data structure."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    score: int = 0
    deaths: int = 0
    triggers: int = 0
    tension_peaks: List[float] = None
    gameplay_events: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize lists after object creation."""
        if self.tension_peaks is None:
            self.tension_peaks = []
        if self.gameplay_events is None:
            self.gameplay_events = []


class TelemetryCollector:
    """Collects and analyzes session telemetry."""
    
    def __init__(self, session_id: str = None):
        """Initialize telemetry collector."""
        self.session_id = session_id or f"session_{int(time.time())}"
        self.metrics = SessionMetrics(
            session_id=self.session_id,
            start_time=time.time()
        )
        self.tension_history = deque(maxlen=1000)  # Keep last 1000 tension values
        self.trigger_history = deque(maxlen=100)   # Keep last 100 triggers
        self.performance_history = deque(maxlen=500)  # Keep last 500 performance samples
        
    def record_score(self, score: int) -> None:
        """Record score update."""
        self.metrics.score = score
    
    def record_death(self, cause: str, position: tuple = None) -> None:
        """Record death event."""
        self.metrics.deaths += 1
        self.metrics.gameplay_events.append({
            "type": "death",
            "timestamp": time.time(),
            "cause": cause,
            "position": position,
            "score": self.metrics.score
        })
    
    def record_trigger(self, trigger_type: str, tension: float, effect_type: str) -> None:
        """Record screamer trigger."""
        self.metrics.triggers += 1
        self.trigger_history.append({
            "timestamp": time.time(),
            "trigger_type": trigger_type,
            "tension": tension,
            "effect_type": effect_type
        })
        self.metrics.gameplay_events.append({
            "type": "trigger",
            "timestamp": time.time(),
            "trigger_type": trigger_type,
            "tension": tension,
            "effect_type": effect_type
        })
    
    def record_tension(self, tension: float) -> None:
        """Record tension value."""
        self.tension_history.append({
            "timestamp": time.time(),
            "tension": tension
        })
        
        # Track peaks
        if tension > 80:  # Consider 80+ as a peak
            self.metrics.tension_peaks.append(tension)
    
    def record_performance(self, fps: float, frame_time: float) -> None:
        """Record performance metrics."""
        self.performance_history.append({
            "timestamp": time.time(),
            "fps": fps,
            "frame_time": frame_time
        })
    
    def record_gameplay_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record general gameplay event."""
        self.metrics.gameplay_events.append({
            "type": event_type,
            "timestamp": time.time(),
            "data": data
        })
    
    def get_session_duration(self) -> float:
        """Get current session duration."""
        end_time = self.metrics.end_time or time.time()
        return end_time - self.metrics.start_time
    
    def get_tension_statistics(self) -> Dict[str, float]:
        """Get tension statistics."""
        if not self.tension_history:
            return {"mean": 0.0, "max": 0.0, "min": 0.0, "std": 0.0}
        
        tensions = [entry["tension"] for entry in self.tension_history]
        
        mean_tension = sum(tensions) / len(tensions)
        max_tension = max(tensions)
        min_tension = min(tensions)
        
        # Calculate standard deviation
        variance = sum((t - mean_tension) ** 2 for t in tensions) / len(tensions)
        std_tension = variance ** 0.5
        
        return {
            "mean": mean_tension,
            "max": max_tension,
            "min": min_tension,
            "std": std_tension
        }
    
    def get_trigger_statistics(self) -> Dict[str, Any]:
        """Get trigger statistics."""
        if not self.trigger_history:
            return {"total": 0, "rate_per_minute": 0.0, "by_type": {}}
        
        duration = self.get_session_duration()
        rate_per_minute = (len(self.trigger_history) / duration) * 60 if duration > 0 else 0
        
        # Count by type
        by_type = defaultdict(int)
        for trigger in self.trigger_history:
            by_type[trigger["trigger_type"]] += 1
        
        return {
            "total": len(self.trigger_history),
            "rate_per_minute": rate_per_minute,
            "by_type": dict(by_type)
        }
    
    def get_performance_statistics(self) -> Dict[str, float]:
        """Get performance statistics."""
        if not self.performance_history:
            return {"avg_fps": 0.0, "min_fps": 0.0, "avg_frame_time": 0.0}
        
        fps_values = [entry["fps"] for entry in self.performance_history]
        frame_times = [entry["frame_time"] for entry in self.performance_history]
        
        return {
            "avg_fps": sum(fps_values) / len(fps_values),
            "min_fps": min(fps_values),
            "avg_frame_time": sum(frame_times) / len(frame_times)
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        self.metrics.end_time = time.time()
        
        return {
            "session_id": self.session_id,
            "duration": self.get_session_duration(),
            "score": self.metrics.score,
            "deaths": self.metrics.deaths,
            "triggers": self.metrics.triggers,
            "tension_stats": self.get_tension_statistics(),
            "trigger_stats": self.get_trigger_statistics(),
            "performance_stats": self.get_performance_statistics(),
            "tension_peaks": len(self.metrics.tension_peaks),
            "total_events": len(self.metrics.gameplay_events)
        }
    
    def export_to_json(self, filename: str = None) -> str:
        """Export session data to JSON file."""
        if filename is None:
            filename = f"telemetry_{self.session_id}.json"
        
        data = {
            "session_metrics": asdict(self.metrics),
            "tension_history": list(self.tension_history),
            "trigger_history": list(self.trigger_history),
            "performance_history": list(self.performance_history),
            "summary": self.get_session_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    def reset(self) -> None:
        """Reset telemetry for new session."""
        self.session_id = f"session_{int(time.time())}"
        self.metrics = SessionMetrics(
            session_id=self.session_id,
            start_time=time.time()
        )
        self.tension_history.clear()
        self.trigger_history.clear()
        self.performance_history.clear()


class TelemetryAnalyzer:
    """Analyzes telemetry data for insights."""
    
    def __init__(self, telemetry_data: Dict[str, Any]):
        """Initialize analyzer with telemetry data."""
        self.data = telemetry_data
    
    def analyze_tension_patterns(self) -> Dict[str, Any]:
        """Analyze tension patterns."""
        tension_history = self.data.get("tension_history", [])
        if not tension_history:
            return {"analysis": "No tension data available"}
        
        tensions = [entry["tension"] for entry in tension_history]
        
        # Find tension spikes
        spikes = []
        for i in range(1, len(tensions) - 1):
            if tensions[i] > tensions[i-1] + 20 and tensions[i] > tensions[i+1] + 20:
                spikes.append({"index": i, "value": tensions[i]})
        
        # Calculate tension volatility
        mean_tension = sum(tensions) / len(tensions)
        volatility = sum((t - mean_tension) ** 2 for t in tensions) / len(tensions)
        
        return {
            "mean_tension": mean_tension,
            "max_tension": max(tensions),
            "tension_spikes": len(spikes),
            "volatility": volatility,
            "spike_details": spikes[:10]  # First 10 spikes
        }
    
    def analyze_trigger_effectiveness(self) -> Dict[str, Any]:
        """Analyze trigger effectiveness."""
        trigger_history = self.data.get("trigger_history", [])
        if not trigger_history:
            return {"analysis": "No trigger data available"}
        
        # Group triggers by type
        by_type = defaultdict(list)
        for trigger in trigger_history:
            by_type[trigger["trigger_type"]].append(trigger)
        
        # Analyze effectiveness
        effectiveness = {}
        for trigger_type, triggers in by_type.items():
            tensions = [t["tension"] for t in triggers]
            effectiveness[trigger_type] = {
                "count": len(triggers),
                "avg_tension": sum(tensions) / len(tensions),
                "max_tension": max(tensions)
            }
        
        return {
            "total_triggers": len(trigger_history),
            "by_type": dict(effectiveness),
            "most_effective": max(effectiveness.items(), key=lambda x: x[1]["avg_tension"])[0]
        }
    
    def analyze_performance_impact(self) -> Dict[str, Any]:
        """Analyze performance impact of triggers."""
        performance_history = self.data.get("performance_history", [])
        trigger_history = self.data.get("trigger_history", [])
        
        if not performance_history or not trigger_history:
            return {"analysis": "Insufficient data for performance analysis"}
        
        # Find performance drops around triggers
        performance_drops = []
        for trigger in trigger_history:
            trigger_time = trigger["timestamp"]
            
            # Find performance data around trigger time
            nearby_performance = [
                p for p in performance_history
                if abs(p["timestamp"] - trigger_time) < 5.0  # 5 seconds around trigger
            ]
            
            if nearby_performance:
                avg_fps = sum(p["fps"] for p in nearby_performance) / len(nearby_performance)
                performance_drops.append({
                    "trigger_type": trigger["trigger_type"],
                    "avg_fps": avg_fps,
                    "tension": trigger["tension"]
                })
        
        return {
            "performance_drops": performance_drops,
            "avg_fps_during_triggers": sum(p["avg_fps"] for p in performance_drops) / len(performance_drops) if performance_drops else 0
        }
    
    def generate_insights(self) -> List[str]:
        """Generate human-readable insights."""
        insights = []
        
        # Tension analysis
        tension_analysis = self.analyze_tension_patterns()
        if "mean_tension" in tension_analysis:
            mean_tension = tension_analysis["mean_tension"]
            if mean_tension > 60:
                insights.append(f"High average tension ({mean_tension:.1f}%) suggests intense gameplay")
            elif mean_tension < 20:
                insights.append(f"Low average tension ({mean_tension:.1f}%) suggests calm gameplay")
        
        # Trigger analysis
        trigger_analysis = self.analyze_trigger_effectiveness()
        if "total_triggers" in trigger_analysis:
            total_triggers = trigger_analysis["total_triggers"]
            if total_triggers > 10:
                insights.append(f"High trigger frequency ({total_triggers}) indicates intense session")
            elif total_triggers == 0:
                insights.append("No triggers occurred - consider adjusting tension thresholds")
        
        # Performance analysis
        performance_analysis = self.analyze_performance_impact()
        if "avg_fps_during_triggers" in performance_analysis:
            avg_fps = performance_analysis["avg_fps_during_triggers"]
            if avg_fps < 30:
                insights.append("Performance drops during triggers - consider optimizing effects")
        
        return insights
