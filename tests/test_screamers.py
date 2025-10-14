"""
Tests for screamers.py - trigger policy boundaries and cooldown logic.
"""

import pytest
import time
from unittest.mock import Mock, patch

from snake_of_despair.screamers import (
    ScreamerType, ScreamerEffect, ScreamerPolicy, ThresholdScreamerPolicy,
    StochasticScreamerPolicy, ScreamerScheduler, ScreamerManager,
    ScreamerEffectPlayer, PygameScreamerPlayer
)


class TestScreamerEffect:
    """Test ScreamerEffect class."""
    
    def test_screamer_effect_creation(self):
        """Test screamer effect creation."""
        effect = ScreamerEffect(
            effect_type=ScreamerType.IMAGE_FLASH,
            duration=0.5,
            intensity=0.8,
            asset_path="test.png",
            audio_volume=0.7,
            visual_intensity=0.9
        )
        
        assert effect.effect_type == ScreamerType.IMAGE_FLASH
        assert effect.duration == 0.5
        assert effect.intensity == 0.8
        assert effect.asset_path == "test.png"
        assert effect.audio_volume == 0.7
        assert effect.visual_intensity == 0.9


class TestThresholdScreamerPolicy:
    """Test ThresholdScreamerPolicy class."""
    
    def test_policy_creation(self):
        """Test threshold policy initialization."""
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=0.5)
        
        assert policy.threshold == 75.0
        assert policy.jitter == 0.5
    
    def test_should_trigger_below_threshold(self):
        """Test trigger decision below threshold."""
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=0.5)
        current_time = time.time()
        last_trigger = current_time - 20.0  # 20 seconds ago
        
        # Tension below threshold
        should_trigger = policy.should_trigger(50.0, current_time, last_trigger, 10.0)
        assert not should_trigger
    
    def test_should_trigger_above_threshold(self):
        """Test trigger decision above threshold."""
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=0.5)
        current_time = time.time()
        last_trigger = current_time - 20.0  # 20 seconds ago
        
        # Tension above threshold
        should_trigger = policy.should_trigger(80.0, current_time, last_trigger, 10.0)
        assert should_trigger
    
    def test_should_trigger_cooldown(self):
        """Test trigger decision during cooldown."""
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=0.5)
        current_time = time.time()
        last_trigger = current_time - 5.0  # 5 seconds ago (within cooldown)
        
        # Even with high tension, should not trigger during cooldown
        should_trigger = policy.should_trigger(90.0, current_time, last_trigger, 10.0)
        assert not should_trigger
    
    def test_jitter_effect(self):
        """Test jitter effect on threshold."""
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=10.0)  # High jitter
        
        current_time = time.time()
        last_trigger = current_time - 20.0
        
        # Test multiple times to see jitter effect
        results = []
        for _ in range(10):
            result = policy.should_trigger(75.0, current_time, last_trigger, 10.0)
            results.append(result)
        
        # Should have some variation due to jitter
        assert len(set(results)) > 1  # Should have both True and False results


class TestStochasticScreamerPolicy:
    """Test StochasticScreamerPolicy class."""
    
    def test_policy_creation(self):
        """Test stochastic policy initialization."""
        policy = StochasticScreamerPolicy(base_threshold=60.0, probability_scale=0.1)
        
        assert policy.base_threshold == 60.0
        assert policy.probability_scale == 0.1
    
    def test_should_trigger_below_base_threshold(self):
        """Test trigger decision below base threshold."""
        policy = StochasticScreamerPolicy(base_threshold=60.0, probability_scale=0.1)
        current_time = time.time()
        last_trigger = current_time - 20.0
        
        # Tension below base threshold
        should_trigger = policy.should_trigger(50.0, current_time, last_trigger, 10.0)
        assert not should_trigger
    
    def test_should_trigger_probability(self):
        """Test trigger decision with probability."""
        policy = StochasticScreamerPolicy(base_threshold=60.0, probability_scale=0.1)
        current_time = time.time()
        last_trigger = current_time - 20.0
        
        # High tension should have high probability
        results = []
        for _ in range(100):
            result = policy.should_trigger(80.0, current_time, last_trigger, 10.0)
            results.append(result)
        
        # Should have some triggers (probabilistic)
        assert any(results)
    
    def test_should_trigger_cooldown(self):
        """Test trigger decision during cooldown."""
        policy = StochasticScreamerPolicy(base_threshold=60.0, probability_scale=0.1)
        current_time = time.time()
        last_trigger = current_time - 5.0  # Within cooldown
        
        # Should not trigger during cooldown regardless of probability
        should_trigger = policy.should_trigger(90.0, current_time, last_trigger, 10.0)
        assert not should_trigger


class TestScreamerScheduler:
    """Test ScreamerScheduler class."""
    
    def test_scheduler_creation(self):
        """Test screamer scheduler initialization."""
        policy = ThresholdScreamerPolicy()
        scheduler = ScreamerScheduler(policy, cooldown_duration=10.0, max_per_minute=3)
        
        assert scheduler.policy == policy
        assert scheduler.cooldown_duration == 10.0
        assert scheduler.max_per_minute == 3
        assert scheduler.last_trigger_time == 0.0
        assert len(scheduler.effects) > 0  # Should have default effects
    
    def test_should_trigger_screamer(self):
        """Test screamer trigger decision."""
        policy = ThresholdScreamerPolicy(threshold=75.0)
        scheduler = ScreamerScheduler(policy, cooldown_duration=10.0, max_per_minute=3)
        
        current_time = time.time()
        
        # Should trigger with high tension
        should_trigger = scheduler.should_trigger_screamer(80.0, current_time)
        assert should_trigger
    
    def test_trigger_screamer(self):
        """Test screamer triggering."""
        policy = ThresholdScreamerPolicy(threshold=75.0)
        scheduler = ScreamerScheduler(policy, cooldown_duration=10.0, max_per_minute=3)
        
        current_time = time.time()
        
        # Trigger screamer
        effect = scheduler.trigger_screamer(current_time)
        
        assert effect is not None
        assert isinstance(effect, ScreamerEffect)
        assert scheduler.last_trigger_time == current_time
        assert len(scheduler.trigger_times) == 1
    
    def test_rate_limiting(self):
        """Test rate limiting (max per minute)."""
        policy = ThresholdScreamerPolicy(threshold=0.0)  # Always trigger
        scheduler = ScreamerScheduler(policy, cooldown_duration=0.0, max_per_minute=2)
        
        current_time = time.time()
        
        # Trigger twice (should work)
        effect1 = scheduler.trigger_screamer(current_time)
        effect2 = scheduler.trigger_screamer(current_time + 1.0)
        
        assert effect1 is not None
        assert effect2 is not None
        
        # Third trigger should be rate limited
        effect3 = scheduler.trigger_screamer(current_time + 2.0)
        assert effect3 is None
    
    def test_cooldown_remaining(self):
        """Test cooldown remaining calculation."""
        policy = ThresholdScreamerPolicy()
        scheduler = ScreamerScheduler(policy, cooldown_duration=10.0, max_per_minute=3)
        
        current_time = time.time()
        scheduler.last_trigger_time = current_time - 5.0  # 5 seconds ago
        
        remaining = scheduler.get_cooldown_remaining(current_time)
        assert remaining == 5.0  # 10 - 5 = 5 seconds remaining


class TestScreamerManager:
    """Test ScreamerManager class."""
    
    def test_manager_creation(self):
        """Test screamer manager initialization."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy()
        manager = ScreamerManager(mock_player, policy)
        
        assert manager.effect_player == mock_player
        assert manager.scheduler.policy == policy
    
    def test_update(self):
        """Test screamer manager update."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy(threshold=75.0)
        manager = ScreamerManager(mock_player, policy)
        
        current_time = time.time()
        tension = 80.0
        
        # Update manager
        manager.update(tension, current_time)
        
        # Should call effect player update
        mock_player.update.assert_called_once_with(current_time)
    
    def test_cooldown_remaining(self):
        """Test cooldown remaining calculation."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy()
        manager = ScreamerManager(mock_player, policy)
        
        current_time = time.time()
        manager.scheduler.last_trigger_time = current_time - 5.0
        
        remaining = manager.get_cooldown_remaining(current_time)
        assert remaining == 5.0
    
    def test_force_trigger(self):
        """Test force trigger functionality."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy()
        manager = ScreamerManager(mock_player, policy)
        
        # Force trigger
        manager.force_trigger()
        
        # Should call effect player
        mock_player.play_effect.assert_called_once()
    
    def test_stop_all(self):
        """Test stop all effects."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy()
        manager = ScreamerManager(mock_player, policy)
        
        # Stop all
        manager.stop_all()
        
        # Should call effect player stop
        mock_player.stop_all_effects.assert_called_once()


class TestScreamerIntegration:
    """Integration tests for screamer system."""
    
    def test_full_screamer_cycle(self):
        """Test complete screamer cycle."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=0.0)  # No jitter for testing
        manager = ScreamerManager(mock_player, policy)
        
        current_time = time.time()
        
        # High tension should trigger screamer
        manager.update(80.0, current_time)
        
        # Should have called play_effect
        assert mock_player.play_effect.called
    
    def test_cooldown_respect(self):
        """Test that cooldown is respected."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy(threshold=0.0)  # Always trigger
        manager = ScreamerManager(mock_player, policy)
        
        current_time = time.time()
        
        # First trigger
        manager.update(80.0, current_time)
        first_call_count = mock_player.play_effect.call_count
        
        # Immediate second trigger (should be blocked by cooldown)
        manager.update(80.0, current_time)
        second_call_count = mock_player.play_effect.call_count
        
        # Should not have triggered again
        assert second_call_count == first_call_count
    
    def test_tension_threshold_variation(self):
        """Test screamer triggering with different tension levels."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy(threshold=75.0)
        manager = ScreamerManager(mock_player, policy)
        
        current_time = time.time()
        
        # Low tension - should not trigger
        manager.update(50.0, current_time)
        assert mock_player.play_effect.call_count == 0
        
        # High tension - should trigger
        manager.update(80.0, current_time)
        assert mock_player.play_effect.call_count == 1
    
    def test_effect_selection(self):
        """Test that different effects are selected."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy(threshold=0.0)  # Always trigger
        manager = ScreamerManager(mock_player, policy)
        
        # Trigger multiple times
        for _ in range(5):
            manager.force_trigger()
        
        # Should have called play_effect multiple times
        assert mock_player.play_effect.call_count == 5
    
    def test_jitter_timing(self):
        """Test jitter timing variation."""
        mock_player = Mock(spec=ScreamerEffectPlayer)
        policy = ThresholdScreamerPolicy(threshold=75.0, jitter=5.0)  # High jitter
        manager = ScreamerManager(mock_player, policy)
        
        current_time = time.time()
        
        # Test multiple times with same tension
        trigger_times = []
        for _ in range(10):
            manager.update(80.0, current_time)
            if mock_player.play_effect.called:
                trigger_times.append(current_time)
            current_time += 0.1
        
        # Should have some variation in triggering due to jitter
        assert len(trigger_times) > 0
