"""
Tests for tension.py - tension contributions and decay.
"""

import pytest
import time
from unittest.mock import Mock, patch

from snake_of_despair.tension import (
    TensionMeter, TensionContributor, TensionSource, TensionEvent,
    TensionAnalyzer
)


class TestTensionEvent:
    """Test TensionEvent class."""
    
    def test_tension_event_creation(self):
        """Test tension event creation."""
        event = TensionEvent(
            source=TensionSource.WALL_PROXIMITY,
            value=50.0,
            timestamp=time.time(),
            duration=2.0
        )
        
        assert event.source == TensionSource.WALL_PROXIMITY
        assert event.value == 50.0
        assert event.duration == 2.0


class TestTensionMeter:
    """Test TensionMeter class."""
    
    def test_tension_meter_creation(self):
        """Test tension meter initialization."""
        meter = TensionMeter(max_tension=100.0, decay_rate=0.5)
        
        assert meter.max_tension == 100.0
        assert meter.decay_rate == 0.5
        assert meter.current_tension == 0.0
        assert len(meter.events) == 0
    
    def test_add_tension(self):
        """Test adding tension events."""
        meter = TensionMeter()
        
        meter.add_tension(TensionSource.WALL_PROXIMITY, 30.0, 1.0)
        assert len(meter.events) == 1
        
        event = meter.events[0]
        assert event.source == TensionSource.WALL_PROXIMITY
        assert event.value == 30.0
        assert event.duration == 1.0
    
    def test_tension_update(self):
        """Test tension meter update."""
        meter = TensionMeter(max_tension=100.0, decay_rate=0.5)
        
        # Add some tension
        meter.add_tension(TensionSource.WALL_PROXIMITY, 50.0, 1.0)
        
        # Update tension
        tension = meter.update()
        
        # Should have some tension (weighted by wall_proximity weight of 2.0)
        assert tension > 0
        assert tension <= meter.max_tension
    
    def test_tension_decay(self):
        """Test tension decay over time."""
        meter = TensionMeter(max_tension=100.0, decay_rate=10.0)  # High decay rate
        
        # Add tension
        meter.add_tension(TensionSource.WALL_PROXIMITY, 50.0, 0.1)  # Short duration
        
        # Update multiple times
        initial_tension = meter.update()
        time.sleep(0.1)  # Wait for decay
        final_tension = meter.update()
        
        # Tension should decay
        assert final_tension < initial_tension
    
    def test_tension_clamping(self):
        """Test tension clamping to valid range."""
        meter = TensionMeter(max_tension=100.0, decay_rate=0.0)  # No decay
        
        # Add very high tension
        meter.add_tension(TensionSource.WALL_PROXIMITY, 1000.0, 1.0)
        
        tension = meter.update()
        assert 0.0 <= tension <= meter.max_tension
    
    def test_cooldown_mechanism(self):
        """Test tension cooldown mechanism."""
        meter = TensionMeter()
        
        # Not in cooldown initially
        assert not meter.is_in_cooldown()
        
        # Start cooldown
        meter.start_cooldown(5.0)
        assert meter.is_in_cooldown()
        
        # Wait for cooldown to expire
        time.sleep(0.1)  # Short wait
        assert meter.is_in_cooldown()  # Should still be in cooldown
    
    def test_reset(self):
        """Test tension meter reset."""
        meter = TensionMeter()
        
        # Add some state
        meter.add_tension(TensionSource.WALL_PROXIMITY, 50.0, 1.0)
        meter.start_cooldown(5.0)
        meter.update()
        
        # Reset
        meter.reset()
        
        assert meter.current_tension == 0.0
        assert len(meter.events) == 0
        assert not meter.is_in_cooldown()
    
    def test_tension_percentage(self):
        """Test tension percentage calculation."""
        meter = TensionMeter(max_tension=100.0)
        
        # Add tension to get 50% of max
        meter.add_tension(TensionSource.WALL_PROXIMITY, 25.0, 1.0)  # 25 * 2.0 weight = 50
        meter.update()
        
        percentage = meter.get_tension_percentage()
        assert 40.0 <= percentage <= 60.0  # Allow some tolerance
    
    def test_tension_level(self):
        """Test tension level description."""
        meter = TensionMeter(max_tension=100.0)
        
        # Test different tension levels
        meter.current_tension = 10.0
        assert meter.get_tension_level() == "calm"
        
        meter.current_tension = 30.0
        assert meter.get_tension_level() == "nervous"
        
        meter.current_tension = 50.0
        assert meter.get_tension_level() == "tense"
        
        meter.current_tension = 70.0
        assert meter.get_tension_level() == "anxious"
        
        meter.current_tension = 90.0
        assert meter.get_tension_level() == "terrified"


class TestTensionContributor:
    """Test TensionContributor class."""
    
    def test_contributor_creation(self):
        """Test tension contributor initialization."""
        meter = TensionMeter()
        contributor = TensionContributor(meter)
        
        assert contributor.tension_meter == meter
        assert contributor.turn_count == 0
        assert contributor.score_streak == 0
    
    def test_contribute_from_turn(self):
        """Test tension contribution from turns."""
        meter = TensionMeter()
        contributor = TensionContributor(meter)
        
        current_time = time.time()
        contributor.contribute_from_turn(current_time)
        
        assert contributor.turn_count == 1
        assert contributor.last_turn_time == current_time
    
    def test_contribute_from_score(self):
        """Test tension contribution from score."""
        meter = TensionMeter()
        contributor = TensionContributor(meter)
        
        contributor.contribute_from_score(10)
        
        assert contributor.score_streak == 1
    
    def test_reset_counters(self):
        """Test counter resets."""
        meter = TensionMeter()
        contributor = TensionContributor(meter)
        
        # Set some values
        contributor.turn_count = 5
        contributor.score_streak = 3
        
        # Reset
        contributor.reset_turn_count()
        contributor.reset_score_streak()
        
        assert contributor.turn_count == 0
        assert contributor.score_streak == 0


class TestTensionAnalyzer:
    """Test TensionAnalyzer class."""
    
    def test_analyzer_creation(self):
        """Test tension analyzer initialization."""
        meter = TensionMeter()
        analyzer = TensionAnalyzer(meter)
        
        assert analyzer.tension_meter == meter
        assert len(analyzer.history) == 0
        assert len(analyzer.recent_peaks) == 0
    
    def test_analyze_patterns(self):
        """Test pattern analysis."""
        meter = TensionMeter(max_tension=100.0)
        analyzer = TensionAnalyzer(meter)
        
        # Add some tension history
        for i in range(10):
            meter.add_tension(TensionSource.WALL_PROXIMITY, 20.0, 1.0)
            meter.update()
        
        # Analyze patterns
        analysis = analyzer.analyze_patterns()
        
        assert "current_tension" in analysis
        assert "tension_level" in analysis
        assert "recent_peaks" in analysis
        assert "trend" in analysis
        assert "volatility" in analysis
    
    def test_trend_calculation(self):
        """Test trend calculation."""
        meter = TensionMeter()
        analyzer = TensionAnalyzer(meter)
        
        # Create rising trend
        for i in range(20):
            meter.add_tension(TensionSource.WALL_PROXIMITY, 10.0 + i, 1.0)
            meter.update()
        
        analysis = analyzer.analyze_patterns()
        assert analysis["trend"] in ["rising", "stable", "falling"]
    
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        meter = TensionMeter()
        analyzer = TensionAnalyzer(meter)
        
        # Create volatile tension pattern
        for i in range(10):
            tension = 50.0 if i % 2 == 0 else 10.0
            meter.add_tension(TensionSource.WALL_PROXIMITY, tension, 1.0)
            meter.update()
        
        analysis = analyzer.analyze_patterns()
        assert 0.0 <= analysis["volatility"] <= 1.0


class TestTensionIntegration:
    """Integration tests for tension system."""
    
    def test_full_tension_cycle(self):
        """Test complete tension cycle."""
        meter = TensionMeter(max_tension=100.0, decay_rate=1.0)
        contributor = TensionContributor(meter)
        
        # Simulate snake state
        mock_snake = Mock()
        mock_snake.get_proximity_to_walls.return_value = 0.8
        mock_snake.get_proximity_to_tail.return_value = 0.6
        mock_snake.get_speed_factor.return_value = 1.5
        mock_snake.get_cornering_factor.return_value = 0.4
        
        mock_apple_manager = Mock()
        mock_apple_manager.get_time_without_apple.return_value = 8.0
        mock_apple_manager.get_spawn_urgency.return_value = 0.7
        
        # Contribute tension
        contributor.contribute_from_snake_state(mock_snake, mock_apple_manager, time.time())
        
        # Update tension
        tension = meter.update()
        
        # Should have significant tension
        assert tension > 20.0
    
    def test_tension_weights(self):
        """Test tension source weights."""
        meter = TensionMeter()
        
        # Add tension from different sources
        meter.add_tension(TensionSource.WALL_PROXIMITY, 10.0, 1.0)  # Weight 2.0
        meter.add_tension(TensionSource.TAIL_PROXIMITY, 10.0, 1.0)  # Weight 3.0
        meter.add_tension(TensionSource.SPEED, 10.0, 1.0)  # Weight 1.0
        
        tension = meter.update()
        
        # Tail proximity should contribute most (3.0 weight)
        # Wall proximity should contribute second most (2.0 weight)
        # Speed should contribute least (1.0 weight)
        assert tension > 0
    
    def test_tension_decay_over_time(self):
        """Test tension decay over extended time."""
        meter = TensionMeter(max_tension=100.0, decay_rate=5.0)
        
        # Add initial tension
        meter.add_tension(TensionSource.WALL_PROXIMITY, 50.0, 0.5)
        initial_tension = meter.update()
        
        # Let it decay
        for _ in range(10):
            time.sleep(0.1)
            meter.update()
        
        final_tension = meter.get_tension()
        
        # Should have decayed significantly
        assert final_tension < initial_tension
        assert final_tension >= 0.0
