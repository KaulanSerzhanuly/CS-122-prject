#!/usr/bin/env python3
"""
Test script to verify package structure and imports.
This can be run to test the package without pygame dependencies.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    try:
        # Test core imports
        from snake_of_despair.config import Config
        from snake_of_despair.snake import Snake, Direction, Position
        from snake_of_despair.apple import AppleManager
        from snake_of_despair.tension import TensionMeter, TensionContributor
        from snake_of_despair.colors import ColorManager
        from snake_of_despair.safety import SafetyManager, SafetySettings
        from snake_of_despair.logging_utils import GameLogger, SeedManager
        from snake_of_despair.telemetry import TelemetryCollector
        
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration creation."""
    try:
        from snake_of_despair.config import Config
        
        config = Config(
            seed=42,
            reduced_scare=True,
            difficulty="normal",
            window_size=(960, 720),
            mute=False,
            debug=True
        )
        
        assert config.seed == 42
        assert config.reduced_scare == True
        assert config.difficulty == "normal"
        assert config.window_size == (960, 720)
        
        print("✅ Configuration creation successful")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_snake_logic():
    """Test snake logic without pygame."""
    try:
        from snake_of_despair.snake import Snake, Position, Direction
        
        # Create snake
        start_pos = Position(10, 10)
        snake = Snake(start_pos, 20, 20)
        
        # Test basic properties
        assert snake.get_length() == 1
        assert snake.alive == True
        assert snake.score == 0
        
        # Test direction changes
        snake.set_direction(Direction.UP)
        assert snake.next_direction == Direction.UP
        
        # Test growth
        snake.grow(2)
        assert snake.growth_pending == 2
        
        print("✅ Snake logic tests passed")
        return True
    except Exception as e:
        print(f"❌ Snake logic error: {e}")
        return False

def test_tension_system():
    """Test tension system."""
    try:
        from snake_of_despair.tension import TensionMeter, TensionSource, TensionContributor
        
        # Test tension meter
        meter = TensionMeter(max_tension=100.0, decay_rate=0.5)
        assert meter.current_tension == 0.0
        
        # Test adding tension
        meter.add_tension(TensionSource.WALL_PROXIMITY, 30.0, 1.0)
        assert len(meter.events) == 1
        
        # Test tension update
        tension = meter.update()
        assert tension >= 0.0
        assert tension <= 100.0
        
        print("✅ Tension system tests passed")
        return True
    except Exception as e:
        print(f"❌ Tension system error: {e}")
        return False

def test_safety_system():
    """Test safety and accessibility system."""
    try:
        from snake_of_despair.safety import SafetyManager, SafetySettings
        
        settings = SafetySettings(
            reduced_scare=True,
            epilepsy_safe=True,
            motion_sensitive=False
        )
        
        manager = SafetyManager(settings)
        
        # Test safety filters
        effect_data = {"volume": 0.9, "flash_duration": 0.2, "intensity": 0.8}
        filtered = manager.apply_safety_filters(effect_data)
        
        assert filtered["volume"] <= 0.8  # Should be limited
        assert filtered["flash_duration"] <= 0.1  # Should be limited
        assert filtered["intensity"] < 0.8  # Should be reduced
        
        print("✅ Safety system tests passed")
        return True
    except Exception as e:
        print(f"❌ Safety system error: {e}")
        return False

def test_logging_system():
    """Test logging and telemetry system."""
    try:
        from snake_of_despair.logging_utils import GameLogger, SeedManager
        from snake_of_despair.telemetry import TelemetryCollector
        
        # Test seed manager
        seed_manager = SeedManager(42)
        assert seed_manager.seed == 42
        
        # Test telemetry
        telemetry = TelemetryCollector("test_session")
        telemetry.record_score(100)
        telemetry.record_tension(75.0)
        
        assert telemetry.metrics.score == 100
        
        print("✅ Logging system tests passed")
        return True
    except Exception as e:
        print(f"❌ Logging system error: {e}")
        return False

def test_cli_parsing():
    """Test CLI argument parsing."""
    try:
        from snake_of_despair.__main__ import parse_args
        
        # Test with various argument combinations
        test_cases = [
            ["--seed", "42", "--reduced-scare"],
            ["--difficulty", "hard", "--window", "1280x720"],
            ["--mute", "--debug"],
            []  # No arguments
        ]
        
        for args in test_cases:
            # Mock sys.argv
            original_argv = sys.argv
            sys.argv = ["snake_of_despair"] + args
            
            try:
                parsed_args = parse_args()
                assert parsed_args is not None
            finally:
                sys.argv = original_argv
        
        print("✅ CLI parsing tests passed")
        return True
    except Exception as e:
        print(f"❌ CLI parsing error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Snake of Despair Package Structure")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_snake_logic,
        test_tension_system,
        test_safety_system,
        test_logging_system,
        test_cli_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package structure is correct.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
