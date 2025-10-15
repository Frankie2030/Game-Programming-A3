"""
Collision detection with tilegrid
"""
import pygame
from game.core import settings


class CollisionSystem:
    """Manages tile-based collision detection"""
    
    def __init__(self, tile_map):
        self.tile_map = tile_map  # 2D list of Tile objects
        self.width = len(tile_map[0]) if tile_map else 0
        self.height = len(tile_map)
    
    def get_tile_collisions(self, rect, gravity_dir):
        """Get all solid tiles colliding with rect for given gravity"""
        collisions = []
        
        # Get tile range to check
        start_col = max(0, rect.left // settings.TILE_SIZE)
        end_col = min(self.width - 1, rect.right // settings.TILE_SIZE)
        start_row = max(0, rect.top // settings.TILE_SIZE)
        end_row = min(self.height - 1, rect.bottom // settings.TILE_SIZE)
        
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                tile = self.tile_map[row][col]
                if tile and tile.is_solid_for_gravity(gravity_dir):
                    if rect.colliderect(tile.rect):
                        collisions.append(tile.rect)
        
        return collisions
    
    def get_tile_at(self, x, y):
        """Get tile at world position"""
        col = x // settings.TILE_SIZE
        row = y // settings.TILE_SIZE
        
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.tile_map[row][col]
        return None
    
    def get_tile_by_grid(self, col, row):
        """Get tile by grid coordinates"""
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.tile_map[row][col]
        return None
    
    def break_tile_at(self, x, y, side):
        """Break tile at position if conditions met"""
        tile = self.get_tile_at(x, y)
        if tile and tile.can_break_from_side(side):
            tile.break_tile()
            return True
        return False
    
    def check_breakable_collision(self, rect, velocity):
        """Check if rect is hitting a breakable tile and break it"""
        # Determine which side we're hitting from based on velocity
        if abs(velocity[0]) > abs(velocity[1]):
            # Horizontal collision
            if velocity[0] > 0:
                side = 'right'
                check_x = rect.right
                check_y = rect.centery
            else:
                side = 'left'
                check_x = rect.left
                check_y = rect.centery
        else:
            # Vertical collision
            if velocity[1] > 0:
                side = 'down'
                check_x = rect.centerx
                check_y = rect.bottom
            else:
                side = 'up'
                check_x = rect.centerx
                check_y = rect.top
        
        return self.break_tile_at(check_x, check_y, side)
    
    def get_nearby_tiles(self, rect, radius_tiles=2):
        """Get all tiles within radius of rect"""
        tiles = []
        
        center_col = rect.centerx // settings.TILE_SIZE
        center_row = rect.centery // settings.TILE_SIZE
        
        for row in range(max(0, center_row - radius_tiles), 
                        min(self.height, center_row + radius_tiles + 1)):
            for col in range(max(0, center_col - radius_tiles),
                            min(self.width, center_col + radius_tiles + 1)):
                tile = self.tile_map[row][col]
                if tile:
                    tiles.append(tile)
        
        return tiles
