"""
Wall and danger zone spawning system for increasing difficulty.
"""

import random
from typing import List, Set, Optional
from dataclasses import dataclass
from .snake import Position


@dataclass
class Wall:
    """Wall obstacle entity."""
    positions: List[Position]
    
    def __init__(self, positions: List[Position]):
        self.positions = positions
    
    def get_positions(self) -> Set[Position]:
        """Get set of all wall positions."""
        return set(self.positions)


@dataclass  
class DangerZone:
    """2x2 danger zone that triggers a screamer when entered."""
    position: Position  # Top-left corner of the 2x2 zone
    
    def __init__(self, position: Position):
        self.position = position
    
    def get_positions(self) -> Set[Position]:
        """Get all 4 positions of the 2x2 zone."""
        x, y = self.position.x, self.position.y
        return {
            Position(x, y),
            Position(x + 1, y),
            Position(x, y + 1),
            Position(x + 1, y + 1)
        }
    
    def contains(self, pos: Position) -> bool:
        """Check if a position is within this danger zone."""
        return pos in self.get_positions()


class WallManager:
    """Manages wall spawning and collision detection."""
    
    def __init__(self, grid_width: int, grid_height: int):
        """Initialize wall manager."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.walls: List[Wall] = []
        self.min_wall_length = 2
        self.max_wall_length = 4
        # Keep walls away from edges to give player some room
        self.edge_margin = 3
    
    def spawn_wall(self, snake_positions: Set[Position], apple_positions: Set[Position]) -> Optional[Wall]:
        """Spawn a new random wall, avoiding snake and apples."""
        # Get all occupied positions
        occupied = snake_positions.copy()
        occupied.update(apple_positions)
        for wall in self.walls:
            occupied.update(wall.get_positions())
        
        # Try to find a valid wall placement
        for _ in range(50):  # Max attempts
            wall = self._generate_random_wall(occupied)
            if wall:
                self.walls.append(wall)
                return wall
        
        return None
    
    def _generate_random_wall(self, occupied: Set[Position]) -> Optional[Wall]:
        """Generate a random wall that doesn't overlap with occupied positions."""
        # Random wall length
        length = random.randint(self.min_wall_length, self.max_wall_length)
        
        # Random orientation (horizontal or vertical)
        horizontal = random.choice([True, False])
        
        # Random starting position (within margins)
        if horizontal:
            start_x = random.randint(self.edge_margin, self.grid_width - self.edge_margin - length)
            start_y = random.randint(self.edge_margin, self.grid_height - self.edge_margin - 1)
        else:
            start_x = random.randint(self.edge_margin, self.grid_width - self.edge_margin - 1)
            start_y = random.randint(self.edge_margin, self.grid_height - self.edge_margin - length)
        
        # Generate wall positions
        positions = []
        for i in range(length):
            if horizontal:
                pos = Position(start_x + i, start_y)
            else:
                pos = Position(start_x, start_y + i)
            
            # Check if position is valid
            if pos in occupied:
                return None
            
            # Also check adjacent positions to avoid blocking paths too much
            # Give some buffer around snake
            for snake_pos in occupied:
                if pos.manhattan_distance_to(snake_pos) < 2:
                    return None
            
            positions.append(pos)
        
        return Wall(positions)
    
    def check_collision(self, position: Position) -> bool:
        """Check if a position collides with any wall."""
        for wall in self.walls:
            if position in wall.get_positions():
                return True
        return False
    
    def get_all_positions(self) -> Set[Position]:
        """Get all wall positions."""
        positions = set()
        for wall in self.walls:
            positions.update(wall.get_positions())
        return positions
    
    def get_walls(self) -> List[Wall]:
        """Get list of all walls."""
        return self.walls.copy()
    
    def reset(self) -> None:
        """Reset all walls."""
        self.walls.clear()


class DangerZoneManager:
    """Manages danger zone spawning and collision detection."""
    
    def __init__(self, grid_width: int, grid_height: int):
        """Initialize danger zone manager."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.danger_zones: List[DangerZone] = []
        # Keep zones away from edges
        self.edge_margin = 3
    
    def spawn_danger_zone(self, snake_positions: Set[Position], 
                          apple_positions: Set[Position],
                          wall_positions: Set[Position]) -> Optional[DangerZone]:
        """Spawn a new 2x2 danger zone, avoiding obstacles."""
        # Get all occupied positions
        occupied = snake_positions.copy()
        occupied.update(apple_positions)
        occupied.update(wall_positions)
        for zone in self.danger_zones:
            occupied.update(zone.get_positions())
        
        # Try to find a valid placement
        for _ in range(50):  # Max attempts
            zone = self._generate_random_zone(occupied)
            if zone:
                self.danger_zones.append(zone)
                return zone
        
        return None
    
    def _generate_random_zone(self, occupied: Set[Position]) -> Optional[DangerZone]:
        """Generate a random 2x2 danger zone that doesn't overlap with occupied positions."""
        # Random top-left position (needs room for 2x2)
        x = random.randint(self.edge_margin, self.grid_width - self.edge_margin - 2)
        y = random.randint(self.edge_margin, self.grid_height - self.edge_margin - 2)
        
        zone = DangerZone(Position(x, y))
        zone_positions = zone.get_positions()
        
        # Check if any position overlaps with occupied
        for pos in zone_positions:
            if pos in occupied:
                return None
            # Also give buffer around snake
            for occ_pos in occupied:
                if pos.manhattan_distance_to(occ_pos) < 2:
                    return None
        
        return zone
    
    def check_collision(self, position: Position) -> Optional[DangerZone]:
        """Check if a position collides with any danger zone. Returns the zone if collision."""
        for zone in self.danger_zones:
            if zone.contains(position):
                return zone
        return None
    
    def remove_zone(self, zone: DangerZone) -> None:
        """Remove a danger zone after it's triggered."""
        if zone in self.danger_zones:
            self.danger_zones.remove(zone)
    
    def get_all_positions(self) -> Set[Position]:
        """Get all danger zone positions."""
        positions = set()
        for zone in self.danger_zones:
            positions.update(zone.get_positions())
        return positions
    
    def get_zones(self) -> List[DangerZone]:
        """Get list of all danger zones."""
        return self.danger_zones.copy()
    
    def reset(self) -> None:
        """Reset all danger zones."""
        self.danger_zones.clear()

