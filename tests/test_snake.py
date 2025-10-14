"""
Tests for snake.py - movement, growth, collision detection.
"""

import pytest
import time
from unittest.mock import Mock

from snake_of_despair.snake import Snake, Direction, Position


class TestPosition:
    """Test Position class."""
    
    def test_position_creation(self):
        """Test position creation and properties."""
        pos = Position(5, 10)
        assert pos.x == 5
        assert pos.y == 10
    
    def test_position_addition(self):
        """Test position addition."""
        pos1 = Position(3, 4)
        pos2 = Position(1, 2)
        result = pos1 + pos2
        assert result.x == 4
        assert result.y == 6
    
    def test_position_equality(self):
        """Test position equality."""
        pos1 = Position(5, 10)
        pos2 = Position(5, 10)
        pos3 = Position(5, 11)
        
        assert pos1 == pos2
        assert pos1 != pos3
    
    def test_position_hash(self):
        """Test position hashing."""
        pos1 = Position(5, 10)
        pos2 = Position(5, 10)
        pos3 = Position(5, 11)
        
        assert hash(pos1) == hash(pos2)
        assert hash(pos1) != hash(pos3)
    
    def test_distance_calculations(self):
        """Test distance calculations."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        
        # Euclidean distance: sqrt(3^2 + 4^2) = 5
        assert pos1.distance_to(pos2) == 5.0
        
        # Manhattan distance: |3| + |4| = 7
        assert pos1.manhattan_distance_to(pos2) == 7


class TestSnake:
    """Test Snake class."""
    
    def test_snake_creation(self):
        """Test snake initialization."""
        start_pos = Position(10, 10)
        snake = Snake(start_pos, 20, 20)
        
        assert snake.body == [start_pos]
        assert snake.direction == Direction.RIGHT
        assert snake.next_direction == Direction.RIGHT
        assert snake.alive
        assert snake.score == 0
        assert snake.get_length() == 1
    
    def test_direction_changes(self):
        """Test direction changes."""
        start_pos = Position(10, 10)
        snake = Snake(start_pos, 20, 20)
        
        # Valid direction change
        snake.set_direction(Direction.UP)
        assert snake.next_direction == Direction.UP
        
        # Invalid 180-degree turn
        snake.set_direction(Direction.DOWN)
        assert snake.next_direction == Direction.UP  # Should not change
    
    def test_movement(self):
        """Test snake movement."""
        start_pos = Position(10, 10)
        snake = Snake(start_pos, 20, 20)
        
        # Move right
        snake.set_direction(Direction.RIGHT)
        snake._move()
        
        assert snake.get_head().x == 11
        assert snake.get_head().y == 10
        assert len(snake.body) == 1  # No growth yet
    
    def test_growth(self):
        """Test snake growth."""
        start_pos = Position(10, 10)
        snake = Snake(start_pos, 20, 20)
        
        # Queue growth
        snake.grow(2)
        assert snake.growth_pending == 2
        
        # Move and grow
        snake._move()
        assert len(snake.body) == 2  # Grew by 1
        assert snake.growth_pending == 1
        
        # Move again
        snake._move()
        assert len(snake.body) == 3  # Grew by 1 more
        assert snake.growth_pending == 0
        
        # Move without growth
        snake._move()
        assert len(snake.body) == 3  # No more growth
    
    def test_wall_collision(self):
        """Test wall collision detection."""
        # Test left wall
        snake = Snake(Position(0, 10), 20, 20)
        snake.set_direction(Direction.LEFT)
        snake._move()
        assert not snake.alive
        
        # Test right wall
        snake = Snake(Position(19, 10), 20, 20)
        snake.set_direction(Direction.RIGHT)
        snake._move()
        assert not snake.alive
        
        # Test top wall
        snake = Snake(Position(10, 0), 20, 20)
        snake.set_direction(Direction.UP)
        snake._move()
        assert not snake.alive
        
        # Test bottom wall
        snake = Snake(Position(10, 19), 20, 20)
        snake.set_direction(Direction.DOWN)
        snake._move()
        assert not snake.alive
    
    def test_self_collision(self):
        """Test self collision detection."""
        snake = Snake(Position(10, 10), 20, 20)
        
        # Grow snake
        snake.grow(3)
        snake._move()  # Head at (11, 10)
        snake._move()  # Head at (12, 10)
        snake._move()  # Head at (13, 10)
        snake._move()  # Head at (14, 10)
        
        # Turn around and collide with body
        snake.set_direction(Direction.LEFT)
        snake._move()  # Head at (13, 10) - should collide with body
        assert not snake.alive
    
    def test_apple_consumption(self):
        """Test apple consumption."""
        snake = Snake(Position(10, 10), 20, 20)
        initial_score = snake.score
        
        snake.eat_apple()
        assert snake.score == initial_score + 10
        assert snake.growth_pending == 1
    
    def test_proximity_calculations(self):
        """Test proximity calculations."""
        snake = Snake(Position(5, 5), 20, 20)
        
        # Test wall proximity (center should be 0.0)
        wall_proximity = snake.get_proximity_to_walls()
        assert 0.0 <= wall_proximity <= 1.0
        
        # Test tail proximity (no tail yet)
        tail_proximity = snake.get_proximity_to_tail()
        assert tail_proximity == 0.0
    
    def test_speed_factor(self):
        """Test speed factor calculation."""
        snake = Snake(Position(10, 10), 20, 20)
        
        # Initial speed factor
        assert snake.get_speed_factor() == 1.0
        
        # Grow snake
        snake.grow(5)
        snake._move()
        snake._move()
        snake._move()
        snake._move()
        snake._move()
        
        # Speed should increase with length
        assert snake.get_speed_factor() > 1.0
    
    def test_cornering_factor(self):
        """Test cornering factor calculation."""
        snake = Snake(Position(10, 10), 20, 20)
        
        # No cornering initially
        assert snake.get_cornering_factor() == 0.0
    
    def test_reset(self):
        """Test snake reset."""
        snake = Snake(Position(10, 10), 20, 20)
        
        # Modify snake state
        snake.grow(2)
        snake.score = 50
        snake.alive = False
        
        # Reset
        new_start = Position(5, 5)
        snake.reset(new_start)
        
        assert snake.body == [new_start]
        assert snake.direction == Direction.RIGHT
        assert snake.next_direction == Direction.RIGHT
        assert snake.growth_pending == 0
        assert snake.alive
        assert snake.score == 0
    
    def test_update_timing(self):
        """Test update timing."""
        snake = Snake(Position(10, 10), 20, 20)
        current_time = time.time()
        move_interval = 0.1
        
        # First update should move
        result = snake.update(current_time, move_interval)
        assert result
        
        # Immediate second update should not move
        result = snake.update(current_time, move_interval)
        assert not result
        
        # Update after interval should move
        result = snake.update(current_time + move_interval, move_interval)
        assert result


class TestDirection:
    """Test Direction enum."""
    
    def test_direction_values(self):
        """Test direction values."""
        assert Direction.UP.value == (0, -1)
        assert Direction.DOWN.value == (0, 1)
        assert Direction.LEFT.value == (-1, 0)
        assert Direction.RIGHT.value == (1, 0)
    
    def test_opposite_directions(self):
        """Test opposite direction detection."""
        # Test 180-degree turn detection
        snake = Snake(Position(10, 10), 20, 20)
        
        # Set initial direction
        snake.set_direction(Direction.RIGHT)
        assert snake.next_direction == Direction.RIGHT
        
        # Try opposite direction
        snake.set_direction(Direction.LEFT)
        assert snake.next_direction == Direction.RIGHT  # Should not change
        
        # Try valid direction
        snake.set_direction(Direction.UP)
        assert snake.next_direction == Direction.UP
