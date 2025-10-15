"""
Power-up collectible
"""
import pygame
from game.core import settings
import math


class PowerUp:
    """Power-up that gives player a boost"""
    
    def __init__(self, x, y, powerup_type='speed'):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.powerup_type = powerup_type  # 'speed', 'double_jump', etc.
        self.collected = False
        self.float_offset = 0
        self.float_time = 0
        
        # Try to load sprite
        self.sprite = None
        try:
            sprite_path = f'game/assets/images/sprites/powerup_{powerup_type}.png'
            self.sprite = pygame.image.load(sprite_path)
            self.sprite = pygame.transform.scale(self.sprite, (24, 24))
        except:
            pass  # Use colored rect fallback
    
    def update(self, dt, player_rect):
        """Update and check collection"""
        if self.collected:
            return False
        
        # Floating animation
        self.float_time += dt * 3
        self.float_offset = math.sin(self.float_time) * 6
        
        # Check collision
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Draw power-up"""
        if self.collected:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        draw_rect.y += self.float_offset
        
        if self.sprite:
            screen.blit(self.sprite, draw_rect)
        else:
            # Fallback: glowing box
            glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 100, 100), (16, 16), 16)
            screen.blit(glow_surf, (draw_rect.centerx - 16, draw_rect.centery - 16))
            
            pygame.draw.rect(screen, (255, 200, 0), draw_rect)
            pygame.draw.rect(screen, settings.COLOR_WHITE, draw_rect, 2)
            
            # Draw "P"
            font = pygame.font.Font(None, 20)
            text = font.render('P', True, settings.COLOR_BLACK)
            text_rect = text.get_rect(center=draw_rect.center)
            screen.blit(text, text_rect)
