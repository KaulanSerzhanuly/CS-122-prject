"""
Snake model, grid logic, collisions, and growth mechanics.
"""

import random
from typing import List, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass


class Direction(Enum):
    """Snake movement directions."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class Position:
    """Grid position with x, y coordinates."""
    x: int
    y: int
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other: 'Position') -> bool:
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def manhattan_distance_to(self, other: 'Position') -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)


class Snake:
    """Snake game entity with movement, growth, and collision detection."""
    
    def __init__(self, start_pos: Position, grid_width: int, grid_height: int):
        """Initialize snake at starting position."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.body = [start_pos]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.growth_pending = 0
        self.alive = True
        self.score = 0
        self.last_move_time = 0.0
        
    def set_direction(self, new_direction: Direction) -> None:
        """Set next direction, preventing 180-degree turns."""
        if self._is_valid_direction(new_direction):
            self.next_direction = new_direction
    
    def _is_valid_direction(self, new_direction: Direction) -> bool:
        """Check if direction change is valid (not 180-degree turn)."""
        if len(self.body) == 1:
            return True
        
        current_dx, current_dy = self.direction.value
        new_dx, new_dy = new_direction.value
        
        # Prevent 180-degree turns
        return not (current_dx == -new_dx and current_dy == -new_dy)
    
    def update(self, current_time: float, move_interval: float) -> bool:
        """Update snake position if enough time has passed."""
        if not self.alive:
            return False
        
        if current_time - self.last_move_time >= move_interval:
            self._move()
            self.last_move_time = current_time
            return True
        return False
    
    def _move(self) -> None:
        """Move snake one step in current direction."""
        if not self.alive:
            return
        
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.body[0]
        dx, dy = self.direction.value
        new_head = Position(head.x + dx, head.y + dy)
        
        # Check for collisions
        if self._check_collision(new_head):
            self.alive = False
            return
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Handle growth
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            # Remove tail if not growing
            self.body.pop()
    
    def _check_collision(self, pos: Position) -> bool:
        """Check if position would cause collision."""
        # Wall collision
        if (pos.x < 0 or pos.x >= self.grid_width or 
            pos.y < 0 or pos.y >= self.grid_height):
            return True
        
        # Self collision (check all body segments except head)
        for segment in self.body[:-1]:
            if pos == segment:
                return True
        
        return False
    
    def grow(self, amount: int = 1) -> None:
        """Queue snake growth for next move."""
        self.growth_pending += amount
    
    def eat_apple(self) -> None:
        """Handle apple consumption."""
        self.grow()
        self.score += 10
    
    def get_head(self) -> Position:
        """Get snake head position."""
        return self.body[0] if self.body else Position(0, 0)
    
    def get_tail(self) -> Position:
        """Get snake tail position."""
        return self.body[-1] if self.body else Position(0, 0)
    
    def get_body_positions(self) -> Set[Position]:
        """Get set of all body positions for collision detection."""
        return set(self.body)
    
    def get_length(self) -> int:
        """Get current snake length."""
        return len(self.body)
    
    def get_proximity_to_walls(self) -> float:
        """Calculate proximity to walls (0.0 = center, 1.0 = edge)."""
        head = self.get_head()
        center_x = self.grid_width / 2
        center_y = self.grid_height / 2
        
        # Distance to nearest wall
        dist_to_wall = min(
            head.x, head.y,
            self.grid_width - 1 - head.x,
            self.grid_height - 1 - head.y
        )
        
        # Normalize to 0-1 scale
        max_dist = min(center_x, center_y)
        return 1.0 - (dist_to_wall / max_dist)
    
    def get_proximity_to_tail(self) -> float:
        """Calculate proximity to tail (0.0 = far, 1.0 = touching)."""
        if len(self.body) < 2:
            return 0.0
        
        head = self.get_head()
        min_distance = float('inf')
        
        # Check distance to all tail segments
        for segment in self.body[1:]:
            distance = head.manhattan_distance_to(segment)
            min_distance = min(min_distance, distance)
        
        # Normalize to 0-1 scale (1 = touching, 0 = far)
        return max(0.0, 1.0 - (min_distance / 5.0))
    
    def get_speed_factor(self) -> float:
        """Get current speed factor based on length."""
        # Speed increases with length
        return 1.0 + (len(self.body) * 0.1)
    
    def get_cornering_factor(self) -> float:
        """Calculate how much snake is cornering (turning frequently)."""
        if len(self.body) < 3:
            return 0.0
        
        # Check if last few moves were turns
        recent_turns = 0
        for i in range(min(3, len(self.body) - 1)):
            if i < len(self.body) - 1:
                # This is a simplified check - in real implementation,
                # we'd track direction changes
                recent_turns += 0.1
        
        return min(1.0, recent_turns)
    
    def reset(self, start_pos: Position) -> None:
        """Reset snake to initial state."""
        self.body = [start_pos]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.growth_pending = 0
        self.alive = True
        self.score = 0
        self.last_move_time = 0.0
