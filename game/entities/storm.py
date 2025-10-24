"""
Storm powerup - permanent stamina boost
"""
import pygame
from game.core import settings
import math


class StormPowerup:
    """Energy powerup that permanently increases stamina capacity and regen rate"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.collected = False
        self.rotation = 0
        self.pulse = 0
        
        # Try to load energy sprite
        self.sprite = None
        try:
            sprite_path = 'game/assets/images/sprites/energy.png'
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (32, 32))
        except:
            pass  # Use fallback rendering
    
    def update(self, dt, player_rect):
        """Update storm powerup and check collection"""
        if self.collected:
            return False
        
        # Rotation and pulse animation
        self.rotation += dt * 120  # degrees per second
        self.pulse += dt * 5
        
        # Check collision with player
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Draw energy powerup"""
        if self.collected:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        center = draw_rect.center
        
        # Pulsing glow
        glow_radius = 28 + int(math.sin(self.pulse) * 6)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (100, 200, 255, 70)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (center[0] - glow_radius, center[1] - glow_radius))
        
        # Draw sprite if loaded
        if self.sprite:
            # Rotate sprite
            rotated = pygame.transform.rotate(self.sprite, self.rotation)
            rotated_rect = rotated.get_rect(center=center)
            screen.blit(rotated, rotated_rect)
        else:
            # Fallback: draw energy orb
            # Outer ring
            pygame.draw.circle(screen, (100, 200, 255), center, 14)
            # Inner ring
            pygame.draw.circle(screen, (200, 230, 255), center, 10)
            # Core
            pygame.draw.circle(screen, (255, 255, 255), center, 5)
            # Border
            pygame.draw.circle(screen, (150, 220, 255), center, 14, 2)
