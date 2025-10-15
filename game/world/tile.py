"""
Tile representation with solidity masks
"""
import pygame
from game.core import settings


class Tile:
    """Individual tile with gravity-aware collision"""
    
    def __init__(self, tile_id, x, y, solid_up=True, solid_down=True, breakable=False, charged_face=None):
        self.tile_id = tile_id
        self.rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
        
        # Collision properties
        self.solid_up = solid_up  # Solid when approached from below
        self.solid_down = solid_down  # Solid when approached from above
        self.breakable = breakable
        self.charged_face = charged_face  # 'up', 'down', 'left', 'right' for breakable panels
        self.broken = False
        
        # Visual
        self.color = self._get_color_from_id(tile_id)
    
    def _get_color_from_id(self, tile_id):
        """Get color based on tile ID (placeholder)"""
        if tile_id == 0:
            return None  # Empty
        elif tile_id == 1:
            return settings.COLOR_GRAY  # Standard solid
        elif tile_id == 2:
            return settings.COLOR_DARK_GRAY  # Platform
        elif tile_id == 3:
            return settings.COLOR_RED  # Breakable crate
        elif tile_id == 4:
            return settings.COLOR_YELLOW  # Electro-panel
        else:
            return settings.COLOR_WHITE
    
    def is_solid_for_gravity(self, gravity_dir):
        """Check if tile is solid for the given gravity direction"""
        if self.broken:
            return False
        
        if gravity_dir == 1:  # Normal gravity (falling down)
            return self.solid_down
        else:  # Inverted gravity (falling up)
            return self.solid_up
    
    def can_break_from_side(self, side):
        """Check if tile can be broken from given side"""
        if not self.breakable or self.broken:
            return False
        
        # If no charged face specified, can break from any side
        if self.charged_face is None:
            return True
        
        return self.charged_face == side
    
    def break_tile(self):
        """Break the tile"""
        self.broken = True
        self.solid_up = False
        self.solid_down = False
    
    def draw(self, screen, camera):
        """Draw tile"""
        if self.broken or self.color is None:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        pygame.draw.rect(screen, self.color, draw_rect)
        
        # Draw border
        pygame.draw.rect(screen, settings.COLOR_BLACK, draw_rect, 1)
        
        # Draw charged face indicator for breakable panels
        if self.breakable and self.charged_face:
            self._draw_charged_indicator(screen, draw_rect)
    
    def _draw_charged_indicator(self, screen, draw_rect):
        """Draw chevron showing charged face"""
        cx, cy = draw_rect.centerx, draw_rect.centery
        size = 6
        
        if self.charged_face == 'up':
            points = [(cx, cy - size), (cx - size, cy), (cx + size, cy)]
        elif self.charged_face == 'down':
            points = [(cx, cy + size), (cx - size, cy), (cx + size, cy)]
        elif self.charged_face == 'left':
            points = [(cx - size, cy), (cx, cy - size), (cx, cy + size)]
        elif self.charged_face == 'right':
            points = [(cx + size, cy), (cx, cy - size), (cx, cy + size)]
        else:
            return
        
        pygame.draw.polygon(screen, settings.COLOR_YELLOW, points)
