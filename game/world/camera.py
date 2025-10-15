"""
Camera system with follow and clamping
"""
from game.core import settings, lerp, clamp


class Camera:
    """2D camera with horizontal follow"""
    
    def __init__(self, world_width, world_height):
        self.x = 0
        self.y = 0
        self.world_width = world_width
        self.world_height = world_height
        self.target_x = 0
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT
    
    def update(self, target_rect):
        """Update camera to follow target"""
        # Target camera position (center on target horizontally)
        self.target_x = target_rect.centerx - self.screen_width // 2
        
        # Smooth lerp
        self.x = lerp(self.x, self.target_x, settings.CAMERA_SMOOTHING)
        
        # Clamp to world bounds
        self.x = clamp(self.x, 0, max(0, self.world_width - self.screen_width))
        
        # No vertical scrolling
        self.y = 0
    
    def apply(self, rect):
        """Apply camera offset to a rect"""
        new_rect = rect.copy()
        new_rect.x -= self.x
        new_rect.y -= self.y
        return new_rect
    
    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        return x - self.x, y - self.y
    
    def screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates"""
        return x + self.x, y + self.y
