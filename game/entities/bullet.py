"""
Player bullet/projectile
"""
import pygame
from game.core import settings


class Bullet:
    """Player projectile"""
    
    def __init__(self, x, y, direction, sprite_frames):
        """
        Args:
            x, y: Starting position
            direction: 1 for right, -1 for left
            sprite_frames: List of bullet animation frames
        """
        self.rect = pygame.Rect(x, y, 12, 8)  # Bullet hitbox
        self.direction = direction
        self.speed = 400  # Pixels per second
        self.alive = True
        
        # Animation
        self.sprite_frames = sprite_frames
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_duration = 0.05  # 50ms per frame
    
    def update(self, dt, collision_system):
        """Update bullet position and check collisions"""
        # Move bullet
        self.rect.x += self.speed * self.direction * dt
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
        
        # Check tile collisions
        collisions = collision_system.get_tile_collisions(self.rect, 1)
        if collisions:
            self.alive = False
        
        # Despawn if off-screen (far enough)
        # You can add camera bounds check here if needed
    
    def draw(self, screen, camera):
        """Draw bullet sprite"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        if len(self.sprite_frames) > 0:
            sprite = self.sprite_frames[self.current_frame]
            # Scale to bullet size
            sprite_scaled = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))
            
            # Flip if going left
            if self.direction == -1:
                sprite_scaled = pygame.transform.flip(sprite_scaled, True, False)
            
            screen.blit(sprite_scaled, draw_rect)
        else:
            # Fallback: yellow rectangle
            pygame.draw.rect(screen, (255, 255, 0), draw_rect)
