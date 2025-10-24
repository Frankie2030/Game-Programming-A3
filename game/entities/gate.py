"""
Gate entity - vertical barrier with spikes that can open/close
"""
import pygame
from game.core import settings


class Gate:
    """Gate with spikes that blocks passage when closed"""
    
    def __init__(self, x, y, height, spike_orientation='up'):
        """
        Create a gate
        x, y: Position (top-left corner when closed)
        height: Height in pixels
        spike_orientation: 'up' or 'down' - which direction spikes face
        """
        self.base_x = x
        self.base_y = y
        self.width = settings.TILE_SIZE
        self.height = height
        self.spike_orientation = spike_orientation
        
        # State
        self.open = False
        self.transition_timer = 0
        self.transition_duration = 0.3  # Seconds to open/close
        self.dealt_damage = False  # Track if we dealt damage this contact
        
        # Rectangle for collision
        self.rect = pygame.Rect(x, y, self.width, height)
    
    def toggle(self):
        """Toggle gate open/closed"""
        self.open = not self.open
        self.transition_timer = self.transition_duration
    
    def update(self, dt):
        """Update gate animation"""
        if self.transition_timer > 0:
            self.transition_timer = max(0, self.transition_timer - dt)
    
    def is_solid(self):
        """Check if gate blocks movement"""
        return not self.open and self.transition_timer == 0
    
    def get_collision_rect(self):
        """Get current collision rectangle based on animation state"""
        # Calculate current height based on open state and transition
        if self.transition_timer > 0:
            # Animating
            progress = 1.0 - (self.transition_timer / self.transition_duration)
            if self.open:
                # Opening - shrinking from full to zero
                current_height = int(self.height * (1.0 - progress))
            else:
                # Closing - growing from zero to full
                current_height = int(self.height * progress)
        else:
            # Static state
            current_height = 0 if self.open else self.height
        
        # If height is zero, no collision
        if current_height == 0:
            return pygame.Rect(0, 0, 0, 0)
        
        # Position depends on spike orientation
        if self.spike_orientation == 'down':
            # Gate hangs from top, grows downward
            return pygame.Rect(self.base_x, self.base_y, self.width, current_height)
        else:
            # Gate sits on ground, grows upward
            y_offset = self.height - current_height
            return pygame.Rect(self.base_x, self.base_y + y_offset, self.width, current_height)
    
    def check_collision(self, player_rect, player_gravity_dir, player_invulnerable):
        """Check if gate spikes hurt player"""
        if self.open:
            # Reset when gate is open
            self.dealt_damage = False
            return False
        
        collision_rect = self.get_collision_rect()
        is_touching = collision_rect.colliderect(player_rect)
        
        if not is_touching:
            # Reset when player leaves
            self.dealt_damage = False
            return False
        
        # Reset dealt_damage flag when player is no longer invulnerable
        if not player_invulnerable:
            self.dealt_damage = False
        
        # Only hurt if touching the spike face and haven't dealt damage yet
        if self.dealt_damage:
            return False
        
        # Spikes are on the edge of the gate
        spike_threshold = 8  # pixels from edge
        
        should_damage = False
        if self.spike_orientation == 'up':
            # Spikes on top
            if player_rect.bottom <= collision_rect.top + spike_threshold:
                should_damage = True
        elif self.spike_orientation == 'down':
            # Spikes on bottom
            if player_rect.top >= collision_rect.bottom - spike_threshold:
                should_damage = True
        
        if should_damage:
            self.dealt_damage = True
            return True
        
        return False
    
    def draw(self, screen, camera):
        """Draw the gate with spikes"""
        collision_rect = self.get_collision_rect()
        
        if collision_rect.width == 0 or collision_rect.height == 0:
            return  # Gate is fully open
        
        draw_rect = collision_rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Draw gate body (metallic bars)
        bar_color = (100, 100, 120)
        shadow_color = (60, 60, 80)
        
        # Draw vertical bars
        num_bars = 3
        bar_width = draw_rect.width // num_bars
        for i in range(num_bars):
            bar_x = draw_rect.x + i * bar_width
            bar_rect = pygame.Rect(bar_x, draw_rect.y, bar_width - 2, draw_rect.height)
            pygame.draw.rect(screen, bar_color, bar_rect)
            pygame.draw.rect(screen, shadow_color, bar_rect, 1)
        
        # Draw spikes
        spike_color = (200, 50, 50)
        spike_size = 8
        num_spikes = max(1, draw_rect.width // (spike_size * 2))
        
        for i in range(num_spikes):
            spike_x = draw_rect.x + (i * 2 + 1) * spike_size
            
            if self.spike_orientation == 'up':
                # Spikes pointing up from top
                spike_points = [
                    (spike_x - spike_size // 2, draw_rect.top),
                    (spike_x + spike_size // 2, draw_rect.top),
                    (spike_x, draw_rect.top - spike_size)
                ]
            else:
                # Spikes pointing down from bottom
                spike_points = [
                    (spike_x - spike_size // 2, draw_rect.bottom),
                    (spike_x + spike_size // 2, draw_rect.bottom),
                    (spike_x, draw_rect.bottom + spike_size)
                ]
            
            pygame.draw.polygon(screen, spike_color, spike_points)
            pygame.draw.polygon(screen, (150, 30, 30), spike_points, 1)
