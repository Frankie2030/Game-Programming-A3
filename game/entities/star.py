"""
Flux Surge power-up
"""
import pygame
from game.core import settings
import math


class FluxStar:
    """Flux Surge power-up"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.collected = False
        self.rotation = 0
        self.pulse = 0
    
    def update(self, dt, player_rect):
        """Update star and check collection"""
        if self.collected:
            return False
        
        # Rotation animation
        self.rotation += dt * 180  # degrees per second
        self.pulse += dt * 4
        
        # Check collision with player
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Draw star with glow effect"""
        if self.collected:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        center = draw_rect.center
        
        # Pulsing glow
        glow_radius = 20 + int(math.sin(self.pulse) * 5)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 100, 60), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (center[0] - glow_radius, center[1] - glow_radius))
        
        # Draw star shape (simplified as a bright square with rotation effect)
        star_size = 12
        points = []
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            px = center[0] + math.cos(angle) * star_size
            py = center[1] + math.sin(angle) * star_size
            points.append((px, py))
        
        pygame.draw.polygon(screen, settings.COLOR_YELLOW, points)
        pygame.draw.circle(screen, settings.COLOR_WHITE, center, 6)
