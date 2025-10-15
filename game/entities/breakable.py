"""
Breakable blocks
"""
import pygame
from game.core import settings


class BreakableBlock:
    """Block that breaks when hit, may contain items"""
    
    def __init__(self, x, y, contents=None):
        self.rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
        self.contents = contents  # 'coin', 'powerup', or None
        self.broken = False
        self.break_animation_timer = 0
        self.particle_offsets = []  # For break animation
    
    def hit(self, side):
        """Break the block"""
        if not self.broken:
            self.broken = True
            self.break_animation_timer = 0.3
            # Create particle offsets for animation
            self.particle_offsets = [
                (-4, -4), (4, -4), (-4, 4), (4, 4),
                (0, -6), (0, 6), (-6, 0), (6, 0)
            ]
            return self.contents
        return None
    
    def update(self, dt):
        """Update animation"""
        if self.break_animation_timer > 0:
            self.break_animation_timer -= dt
    
    def is_solid(self):
        """Check if block is solid"""
        return not self.broken
    
    def draw(self, screen, camera):
        """Draw block"""
        if self.broken and self.break_animation_timer <= 0:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        if self.broken:
            # Draw break particles
            alpha = int(255 * (self.break_animation_timer / 0.3))
            for offset in self.particle_offsets:
                particle_rect = pygame.Rect(
                    draw_rect.centerx + offset[0] * (1 + (1 - self.break_animation_timer / 0.3)),
                    draw_rect.centery + offset[1] * (1 + (1 - self.break_animation_timer / 0.3)),
                    6, 6
                )
                pygame.draw.rect(screen, (139, 90, 43), particle_rect)
        else:
            # Draw intact block
            # Brownish brick color
            pygame.draw.rect(screen, (139, 90, 43), draw_rect)
            
            # Brick pattern
            pygame.draw.rect(screen, (120, 75, 35), draw_rect, 3)
            
            # Mortar lines
            mid_y = draw_rect.centery
            pygame.draw.line(screen, (100, 65, 30),
                           (draw_rect.left, mid_y),
                           (draw_rect.right, mid_y), 2)
            
            # Draw content hint
            if self.contents == 'coin':
                # Small coin icon
                pygame.draw.circle(screen, settings.COLOR_YELLOW,
                                 (draw_rect.centerx, draw_rect.centery), 4)
            elif self.contents == 'powerup':
                # Small star icon
                pygame.draw.circle(screen, (255, 200, 0),
                                 (draw_rect.centerx, draw_rect.centery), 5)
                pygame.draw.circle(screen, settings.COLOR_WHITE,
                                 (draw_rect.centerx, draw_rect.centery), 3)
