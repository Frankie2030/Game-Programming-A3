"""
Checkpoint system for respawn
"""
import pygame
from game.core import settings


class Checkpoint:
    """Respawn checkpoint flag"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 48)
        self.activated = False
        self.animation_time = 0
    
    def update(self, dt, player_rect):
        """Check if player touches checkpoint"""
        if not self.activated and self.rect.colliderect(player_rect):
            self.activated = True
            return True
        
        if self.activated:
            self.animation_time += dt
        
        return False
    
    def draw(self, screen, camera):
        """Draw checkpoint flag"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Pole
        pole_rect = pygame.Rect(draw_rect.left + 4, draw_rect.top, 4, draw_rect.height)
        pygame.draw.rect(screen, settings.COLOR_GRAY, pole_rect)
        
        # Flag
        flag_color = settings.COLOR_GREEN if self.activated else settings.COLOR_DARK_GRAY
        flag_points = [
            (draw_rect.left + 8, draw_rect.top + 4),
            (draw_rect.right, draw_rect.top + 12),
            (draw_rect.left + 8, draw_rect.top + 20)
        ]
        pygame.draw.polygon(screen, flag_color, flag_points)
        
        # Checkmark if activated
        if self.activated:
            check_x = draw_rect.left + 14
            check_y = draw_rect.top + 12
            pygame.draw.line(screen, settings.COLOR_WHITE,
                           (check_x, check_y),
                           (check_x + 3, check_y + 3), 2)
            pygame.draw.line(screen, settings.COLOR_WHITE,
                           (check_x + 3, check_y + 3),
                           (check_x + 8, check_y - 4), 2)
