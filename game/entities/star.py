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
        
        # Try to load star sprite sheet and extract frames
        self.frames = []
        self.current_frame = 0
        self.animation_time = 0
        self.frame_duration = 0.08  # seconds per frame
        
        try:
            sprite_path = 'game/assets/images/sprites/Star.png'
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
            
            # Extract frames from sprite sheet (assuming horizontal layout)
            sheet_width = sprite_sheet.get_width()
            sheet_height = sprite_sheet.get_height()
            frame_width = sheet_height  # Assuming frames are square
            num_frames = sheet_width // frame_width
            
            for i in range(num_frames):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
                frame = sprite_sheet.subsurface(frame_rect).copy()
                # Scale to desired size
                frame_scaled = pygame.transform.scale(frame, (24, 24))
                self.frames.append(frame_scaled)
        except Exception as e:
            print(f"Failed to load star sprite: {e}")
            pass  # Use fallback rendering
    
    def update(self, dt, player_rect):
        """Update star and check collection"""
        if self.collected:
            return False
        
        # Update animation
        if len(self.frames) > 0:
            self.animation_time += dt
            if self.animation_time >= self.frame_duration:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # Rotation animation (for fallback)
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
        
        # Draw animated sprite if loaded, otherwise fallback
        if len(self.frames) > 0:
            # Draw current animation frame
            frame = self.frames[self.current_frame]
            frame_rect = frame.get_rect(center=center)
            screen.blit(frame, frame_rect)
        else:
            # Fallback: Draw star shape
            star_size = 12
            points = []
            for i in range(4):
                angle = math.radians(self.rotation + i * 90)
                px = center[0] + math.cos(angle) * star_size
                py = center[1] + math.sin(angle) * star_size
                points.append((px, py))
            
            pygame.draw.polygon(screen, settings.COLOR_YELLOW, points)
            pygame.draw.circle(screen, settings.COLOR_WHITE, center, 6)
