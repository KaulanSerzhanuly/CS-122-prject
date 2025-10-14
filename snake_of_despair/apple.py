"""
Apple spawn and re-spawn logic for Snake of Despair.
"""

import random
from typing import Optional, Set, List
from dataclasses import dataclass
from .snake import Position


@dataclass
class Apple:
    """Apple game entity."""
    position: Position
    spawn_time: float
    value: int = 10
    special: bool = False  # For future special apple types
    
    def __init__(self, position: Position, spawn_time: float, value: int = 10, special: bool = False):
        self.position = position
        self.spawn_time = spawn_time
        self.value = value
        self.special = special


class AppleManager:
    """Manages apple spawning, positioning, and special effects."""
    
    def __init__(self, grid_width: int, grid_height: int):
        """Initialize apple manager."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.apples: List[Apple] = []
        self.last_spawn_time = 0.0
        self.spawn_interval = 0.0  # No automatic spawning initially
        self.max_apples = 1  # Only one apple at a time for classic Snake
        
    def spawn_apple(self, current_time: float, snake_positions: Set[Position]) -> Optional[Apple]:
        """Spawn a new apple if conditions are met."""
        # Only spawn if no apples exist
        if self.apples:
            return None
        
        # Find valid spawn position
        position = self._find_valid_position(snake_positions)
        if position is None:
            return None
        
        # Create apple
        apple = Apple(position, current_time)
        self.apples.append(apple)
        self.last_spawn_time = current_time
        
        return apple
    
    def _find_valid_position(self, snake_positions: Set[Position]) -> Optional[Position]:
        """Find a valid position for apple spawn."""
        # Get all occupied positions
        occupied = snake_positions.copy()
        
        # Add existing apple positions
        for apple in self.apples:
            occupied.add(apple.position)
        
        # Find all valid positions
        valid_positions = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                pos = Position(x, y)
                if pos not in occupied:
                    valid_positions.append(pos)
        
        if not valid_positions:
            return None
        
        # Randomly select from valid positions
        return random.choice(valid_positions)
    
    def check_collision(self, snake_head: Position) -> Optional[Apple]:
        """Check if snake head collides with any apple."""
        for apple in self.apples:
            if apple.position == snake_head:
                return apple
        return None
    
    def remove_apple(self, apple: Apple) -> None:
        """Remove apple from the game."""
        if apple in self.apples:
            self.apples.remove(apple)
    
    def get_apples(self) -> List[Apple]:
        """Get list of all current apples."""
        return self.apples.copy()
    
    def get_apple_positions(self) -> Set[Position]:
        """Get set of all apple positions."""
        return {apple.position for apple in self.apples}
    
    def get_time_without_apple(self, current_time: float) -> float:
        """Get time elapsed since last apple was eaten."""
        if not self.apples:
            return current_time - self.last_spawn_time
        return 0.0
    
    def should_spawn_apple(self, current_time: float) -> bool:
        """Check if conditions are met to spawn a new apple."""
        # Always spawn if no apples exist
        return len(self.apples) == 0
    
    def get_spawn_urgency(self, current_time: float) -> float:
        """Get urgency factor for apple spawning (0.0 = no urgency, 1.0 = very urgent)."""
        if self.apples:
            return 0.0
        
        time_without = self.get_time_without_apple(current_time)
        
        # Urgency increases over time
        if time_without < 5.0:
            return 0.0
        elif time_without < 10.0:
            return (time_without - 5.0) / 5.0
        else:
            return 1.0
    
    def get_apple_value(self, base_value: int = 10) -> int:
        """Get value for new apple (can be modified for special apples)."""
        return base_value
    
    def reset(self) -> None:
        """Reset apple manager state."""
        self.apples.clear()
        self.last_spawn_time = 0.0


class SpecialAppleManager(AppleManager):
    """Extended apple manager with special apple types."""
    
    def __init__(self, grid_width: int, grid_height: int):
        """Initialize special apple manager."""
        super().__init__(grid_width, grid_height)
        self.special_apple_chance = 0.1  # 10% chance for special apple
        self.special_apple_types = ["golden", "poison", "speed_boost"]
    
    def spawn_apple(self, current_time: float, snake_positions: Set[Position]) -> Optional[Apple]:
        """Spawn apple with chance for special type."""
        apple = super().spawn_apple(current_time, snake_positions)
        
        if apple and random.random() < self.special_apple_chance:
            # Make it a special apple
            apple.special = True
            apple.value = self._get_special_value()
        
        return apple
    
    def _get_special_value(self) -> int:
        """Get value for special apple."""
        return random.choice([20, -10, 15])  # Golden, poison, speed boost
    
    def get_apple_effect(self, apple: Apple) -> str:
        """Get effect type for special apple."""
        if not apple.special:
            return "normal"
        
        if apple.value > 15:
            return "golden"
        elif apple.value < 0:
            return "poison"
        else:
            return "speed_boost"
