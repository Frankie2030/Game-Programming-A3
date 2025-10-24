"""
Screen transition effects for state changes
"""
import pygame
from game.core import settings


class FadeTransition:
    """Fade to/from black transition"""
    
    def __init__(self, duration=0.3):
        self.duration = duration
        self.elapsed = 0
        self.fade_out = True  # Start with fade out
        self.complete = False
        self.surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.surface.fill((0, 0, 0))
    
    def update(self, dt):
        """Update transition"""
        self.elapsed += dt
        
        # Check if we should switch from fade out to fade in
        if self.fade_out and self.elapsed >= self.duration:
            self.fade_out = False
            self.elapsed = 0
        elif not self.fade_out and self.elapsed >= self.duration:
            self.complete = True
    
    def get_alpha(self):
        """Get current alpha value"""
        progress = min(1.0, self.elapsed / self.duration)
        
        if self.fade_out:
            # Fade to black (0 -> 255)
            return int(255 * progress)
        else:
            # Fade from black (255 -> 0)
            return int(255 * (1 - progress))
    
    def draw(self, screen):
        """Draw fade effect"""
        alpha = self.get_alpha()
        self.surface.set_alpha(alpha)
        screen.blit(self.surface, (0, 0))
    
    def is_complete(self):
        """Check if transition is complete"""
        return self.complete
    
    def is_halfway(self):
        """Check if we're at the halfway point (fully black)"""
        return not self.fade_out and self.elapsed == 0
