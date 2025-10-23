"""
Storm powerup - clears enemies in large radius
"""
import pygame
from game.core import settings
import math


class StormPowerup:
    """Unique storm powerup that clears enemies in a large radius"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.collected = False
        self.rotation = 0
        self.pulse = 0
        self.lightning_time = 0
    
    def update(self, dt, player_rect):
        """Update storm powerup and check collection"""
        if self.collected:
            return False
        
        # Rotation animation
        self.rotation += dt * 90  # degrees per second
        self.pulse += dt * 6
        self.lightning_time += dt * 8
        
        # Check collision with player
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Draw storm powerup with lightning effects"""
        if self.collected:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        center = draw_rect.center
        
        # Pulsing glow with lightning effect
        glow_radius = 25 + int(math.sin(self.pulse) * 8)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        
        # Lightning effect - flickering colors
        lightning_intensity = int(math.sin(self.lightning_time) * 50 + 50)
        glow_color = (lightning_intensity, lightning_intensity, 255, 80)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (center[0] - glow_radius, center[1] - glow_radius))
        
        # Draw storm cloud shape
        cloud_points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            radius = 8 + int(math.sin(self.pulse + i) * 3)
            px = center[0] + math.cos(angle) * radius
            py = center[1] + math.sin(angle) * radius
            cloud_points.append((px, py))
        
        pygame.draw.polygon(screen, (100, 100, 150), cloud_points)
        pygame.draw.polygon(screen, (150, 150, 200), cloud_points, 2)
        
        # Lightning bolt in center
        lightning_color = (255, 255, lightning_intensity)
        pygame.draw.line(screen, lightning_color, 
                        (center[0], center[1] - 8), 
                        (center[0], center[1] + 8), 3)
        pygame.draw.line(screen, lightning_color, 
                        (center[0] - 4, center[1] - 4), 
                        (center[0] + 4, center[1] + 4), 2)
        
        # Debug: Draw a simple rectangle to make sure it's visible
        pygame.draw.rect(screen, (255, 0, 0), draw_rect, 2)  # Red border for debugging
