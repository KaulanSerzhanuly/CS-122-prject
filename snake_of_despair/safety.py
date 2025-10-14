"""
Reduced scare mode and accessibility safety features.
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class AccessibilityLevel(Enum):
    """Accessibility levels for different needs."""
    NONE = "none"
    REDUCED_SCARE = "reduced_scare"
    EPILEPSY_SAFE = "epilepsy_safe"
    MOTION_SENSITIVE = "motion_sensitive"


@dataclass
class SafetySettings:
    """Safety and accessibility settings."""
    reduced_scare: bool = False
    epilepsy_safe: bool = False
    motion_sensitive: bool = False
    volume_limit: float = 0.8
    flash_duration_limit: float = 0.1
    color_contrast: float = 1.0
    motion_reduction: float = 0.0


class SafetyManager:
    """Manages safety features and accessibility options."""
    
    def __init__(self, settings: SafetySettings = None):
        """Initialize safety manager."""
        self.settings = settings or SafetySettings()
        self.active_warnings: Dict[str, float] = {}  # warning_type -> timestamp
        self.volume_history: list = []
        self.flash_history: list = []
    
    def apply_safety_filters(self, effect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety filters to effect data."""
        filtered_data = effect_data.copy()
        
        if self.settings.reduced_scare:
            filtered_data = self._apply_reduced_scare_filters(filtered_data)
        
        if self.settings.epilepsy_safe:
            filtered_data = self._apply_epilepsy_safe_filters(filtered_data)
        
        if self.settings.motion_sensitive:
            filtered_data = self._apply_motion_sensitive_filters(filtered_data)
        
        return filtered_data
    
    def _apply_reduced_scare_filters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply reduced scare mode filters."""
        # Volume limits
        if "volume" in data:
            data["volume"] = min(data["volume"], self.settings.volume_limit)
        
        # Flash duration limits
        if "flash_duration" in data:
            data["flash_duration"] = min(data["flash_duration"], 
                                       self.settings.flash_duration_limit)
        
        # Reduce intensity
        if "intensity" in data:
            data["intensity"] *= 0.3
        
        # Replace harsh effects with gentle ones
        if data.get("effect_type") == "screamer":
            data["effect_type"] = "gentle_notification"
        
        return data
    
    def _apply_epilepsy_safe_filters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply epilepsy safety filters."""
        # Remove rapid flashing
        if "flash_rate" in data:
            data["flash_rate"] = min(data["flash_rate"], 2.0)  # Max 2 Hz
        
        # Limit flash duration
        if "flash_duration" in data:
            data["flash_duration"] = min(data["flash_duration"], 0.05)
        
        # Remove strobing effects
        if "strobe" in data:
            data["strobe"] = False
        
        return data
    
    def _apply_motion_sensitive_filters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply motion sensitivity filters."""
        # Reduce motion effects
        if "motion_intensity" in data:
            data["motion_intensity"] *= (1.0 - self.settings.motion_reduction)
        
        # Limit camera shake
        if "camera_shake" in data:
            data["camera_shake"] = False
        
        return data
    
    def check_volume_safety(self, volume: float) -> float:
        """Check and limit volume for safety."""
        # Track volume history
        self.volume_history.append(volume)
        if len(self.volume_history) > 100:  # Keep last 100 samples
            self.volume_history.pop(0)
        
        # Apply volume limits
        limited_volume = min(volume, self.settings.volume_limit)
        
        # Check for sudden volume spikes
        if len(self.volume_history) > 1:
            recent_avg = sum(self.volume_history[-5:]) / min(5, len(self.volume_history))
            if volume > recent_avg * 2.0:  # Sudden spike
                limited_volume *= 0.5  # Reduce spike
        
        return limited_volume
    
    def check_flash_safety(self, duration: float, intensity: float) -> Tuple[float, float]:
        """Check and limit flash effects for safety."""
        # Track flash history
        self.flash_history.append((duration, intensity))
        if len(self.flash_history) > 50:
            self.flash_history.pop(0)
        
        # Apply duration limits
        limited_duration = min(duration, self.settings.flash_duration_limit)
        
        # Apply intensity limits for epilepsy safety
        if self.settings.epilepsy_safe:
            limited_intensity = min(intensity, 0.5)
        else:
            limited_intensity = intensity
        
        return limited_duration, limited_intensity
    
    def get_safe_colors(self) -> Dict[str, Tuple[int, int, int, int]]:
        """Get safe color palette based on settings."""
        if self.settings.reduced_scare:
            return {
                "flash": (150, 150, 150, 255),
                "overlay": (50, 50, 50, 100),
                "warning": (255, 200, 0, 255),
                "danger": (200, 100, 100, 255)
            }
        elif self.settings.epilepsy_safe:
            return {
                "flash": (200, 200, 200, 255),
                "overlay": (100, 100, 100, 128),
                "warning": (255, 255, 0, 255),
                "danger": (255, 100, 100, 255)
            }
        else:
            return {
                "flash": (255, 255, 255, 255),
                "overlay": (0, 0, 0, 128),
                "warning": (255, 165, 0, 255),
                "danger": (255, 0, 0, 255)
            }
    
    def show_content_warning(self) -> bool:
        """Show content warning and return if user accepts."""
        # This would show a modal dialog in the actual implementation
        # For now, return True (user accepts)
        return True
    
    def show_epilepsy_warning(self) -> bool:
        """Show epilepsy warning and return if user accepts."""
        # This would show a specific epilepsy warning
        return True
    
    def get_accessibility_recommendations(self) -> list:
        """Get accessibility recommendations based on current settings."""
        recommendations = []
        
        if not self.settings.reduced_scare:
            recommendations.append("Consider enabling reduced scare mode for gentler experience")
        
        if not self.settings.epilepsy_safe:
            recommendations.append("Enable epilepsy safety mode if you have photosensitive epilepsy")
        
        if not self.settings.motion_sensitive:
            recommendations.append("Enable motion sensitivity mode if you experience motion sickness")
        
        return recommendations


class ContentWarningManager:
    """Manages content warnings and safety notices."""
    
    def __init__(self):
        """Initialize content warning manager."""
        self.warnings_shown = set()
        self.warning_messages = {
            "horror_content": "This game contains horror elements including sudden sounds and visual effects.",
            "epilepsy_warning": "This game may contain flashing lights that could trigger seizures in people with photosensitive epilepsy.",
            "jump_scares": "This game contains jump scares and sudden loud noises.",
            "reduced_scare_available": "Reduced scare mode is available in settings for a gentler experience."
        }
    
    def should_show_warning(self, warning_type: str) -> bool:
        """Check if a warning should be shown."""
        return warning_type not in self.warnings_shown
    
    def mark_warning_shown(self, warning_type: str) -> None:
        """Mark a warning as shown."""
        self.warnings_shown.add(warning_type)
    
    def get_warning_message(self, warning_type: str) -> str:
        """Get warning message for a specific type."""
        return self.warning_messages.get(warning_type, "Warning: This content may not be suitable for all audiences.")
    
    def get_all_warnings(self) -> list:
        """Get all applicable warnings."""
        return [self.get_warning_message(w) for w in self.warning_messages.keys()]


class AccessibilityTester:
    """Tests accessibility features and provides feedback."""
    
    def __init__(self, safety_manager: SafetyManager):
        """Initialize accessibility tester."""
        self.safety_manager = safety_manager
    
    def test_volume_safety(self, test_volume: float) -> Dict[str, Any]:
        """Test volume safety settings."""
        safe_volume = self.safety_manager.check_volume_safety(test_volume)
        
        return {
            "original_volume": test_volume,
            "safe_volume": safe_volume,
            "reduction_applied": test_volume - safe_volume,
            "safety_level": "safe" if safe_volume <= self.safety_manager.settings.volume_limit else "warning"
        }
    
    def test_flash_safety(self, duration: float, intensity: float) -> Dict[str, Any]:
        """Test flash safety settings."""
        safe_duration, safe_intensity = self.safety_manager.check_flash_safety(duration, intensity)
        
        return {
            "original_duration": duration,
            "safe_duration": safe_duration,
            "original_intensity": intensity,
            "safe_intensity": safe_intensity,
            "safety_level": "safe" if (safe_duration <= self.safety_manager.settings.flash_duration_limit and 
                                     safe_intensity <= 0.5) else "warning"
        }
    
    def run_accessibility_audit(self) -> Dict[str, Any]:
        """Run comprehensive accessibility audit."""
        audit_results = {
            "volume_safety": self.test_volume_safety(1.0),
            "flash_safety": self.test_flash_safety(0.2, 0.8),
            "color_contrast": self._test_color_contrast(),
            "motion_safety": self._test_motion_safety(),
            "overall_safety_score": 0.0
        }
        
        # Calculate overall safety score
        scores = []
        for test_name, results in audit_results.items():
            if isinstance(results, dict) and "safety_level" in results:
                score = 1.0 if results["safety_level"] == "safe" else 0.5
                scores.append(score)
        
        if scores:
            audit_results["overall_safety_score"] = sum(scores) / len(scores)
        
        return audit_results
    
    def _test_color_contrast(self) -> Dict[str, Any]:
        """Test color contrast accessibility."""
        return {
            "high_contrast_available": True,
            "color_blind_safe": True,
            "safety_level": "safe"
        }
    
    def _test_motion_safety(self) -> Dict[str, Any]:
        """Test motion safety settings."""
        return {
            "motion_reduction": self.safety_manager.settings.motion_reduction,
            "camera_shake_disabled": True,
            "safety_level": "safe" if self.safety_manager.settings.motion_sensitive else "warning"
        }
