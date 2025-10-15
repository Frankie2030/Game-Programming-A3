"""
Coin collectible (data canister)
"""
import pygame
from game.core import settings
import math


class Coin:
    """Data canister collectible"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.collected = False
        self.spawn_time = 0  # For animation
        self.bob_offset = 0
    
    def update(self, dt, player_rect):
        """Update coin and check collection"""
        if self.collected:
            return
        
        # Bobbing animation
        self.spawn_time += dt
        self.bob_offset = math.sin(self.spawn_time * 3) * 4
        
        # Check collision with player
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Draw coin"""
        if self.collected:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        draw_rect.y += self.bob_offset
        
        # Draw coin as a circle
        center = draw_rect.center
        pygame.draw.circle(screen, settings.COLOR_YELLOW, center, 8)
        pygame.draw.circle(screen, (200, 180, 0), center, 8, 2)
        
        # Draw data pattern
        pygame.draw.circle(screen, (255, 240, 100), center, 4)
