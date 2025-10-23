"""
Spike hazards
"""
import pygame
from game.core import settings


class Spikes:
    """Deadly spikes that hurt on contact"""
    
    def __init__(self, x, y, orientation='up'):
        self.rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
        self.orientation = orientation  # 'up', 'down', 'left', 'right'
        self.player_touching = False  # Track if player is currently touching
        self.last_damage_time = 0  # Track when last damage was dealt
    
    def check_collision(self, player_rect, player_gravity_dir, current_time):
        """Check if player touched spikes from dangerous side and should take damage"""
        is_touching = self.rect.colliderect(player_rect)
        
        # Check if player is touching from dangerous direction
        should_damage = False
        if is_touching:
            epsilon = 4
            
            if self.orientation == 'up':
                # Hurt when player lands on top (gravity down, coming from above)
                if player_gravity_dir == 1 and player_rect.bottom >= self.rect.top - epsilon:
                    should_damage = True
            elif self.orientation == 'down':
                # Hurt when player hits from below (gravity up, coming from below)
                if player_gravity_dir == -1 and player_rect.top <= self.rect.bottom + epsilon:
                    should_damage = True
            elif self.orientation == 'left':
                # Hurt from left side
                if player_rect.right >= self.rect.left - epsilon:
                    should_damage = True
            elif self.orientation == 'right':
                # Hurt from right side
                if player_rect.left <= self.rect.right + epsilon:
                    should_damage = True
        
        # Only damage on FIRST contact - player must leave and re-enter to take damage again
        if should_damage and not self.player_touching:
            self.player_touching = True
            return True
        
        # Update touching state - reset when player leaves
        if not is_touching:
            self.player_touching = False
        
        return False
    
    def is_player_stuck(self, player_rect, player_gravity_dir):
        """Check if player is stuck on spikes (should prevent easy movement away)"""
        if not self.rect.colliderect(player_rect):
            return False
        
        # Player is stuck if touching from dangerous direction
        epsilon = 4
        
        if self.orientation == 'up':
            # Stuck when player is on top (gravity down)
            return player_gravity_dir == 1 and player_rect.bottom >= self.rect.top - epsilon
        elif self.orientation == 'down':
            # Stuck when player is below (gravity up)
            return player_gravity_dir == -1 and player_rect.top <= self.rect.bottom + epsilon
        elif self.orientation == 'left':
            # Stuck when player is to the right
            return player_rect.right >= self.rect.left - epsilon
        elif self.orientation == 'right':
            # Stuck when player is to the left
            return player_rect.left <= self.rect.right + epsilon
        
        return False
    
    def draw(self, screen, camera):
        """Draw spikes"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Base
        pygame.draw.rect(screen, settings.COLOR_DARK_GRAY, draw_rect)
        
        # Draw spike triangles
        spike_color = (180, 50, 50)  # Dark red
        num_spikes = 4
        spike_width = settings.TILE_SIZE // num_spikes
        
        if self.orientation == 'up':
            for i in range(num_spikes):
                x = draw_rect.left + i * spike_width
                points = [
                    (x, draw_rect.bottom),
                    (x + spike_width // 2, draw_rect.top),
                    (x + spike_width, draw_rect.bottom)
                ]
                pygame.draw.polygon(screen, spike_color, points)
                pygame.draw.polygon(screen, settings.COLOR_BLACK, points, 1)
        
        elif self.orientation == 'down':
            for i in range(num_spikes):
                x = draw_rect.left + i * spike_width
                points = [
                    (x, draw_rect.top),
                    (x + spike_width // 2, draw_rect.bottom),
                    (x + spike_width, draw_rect.top)
                ]
                pygame.draw.polygon(screen, spike_color, points)
                pygame.draw.polygon(screen, settings.COLOR_BLACK, points, 1)
        
        elif self.orientation == 'left':
            for i in range(num_spikes):
                y = draw_rect.top + i * spike_width
                points = [
                    (draw_rect.right, y),
                    (draw_rect.left, y + spike_width // 2),
                    (draw_rect.right, y + spike_width)
                ]
                pygame.draw.polygon(screen, spike_color, points)
                pygame.draw.polygon(screen, settings.COLOR_BLACK, points, 1)
        
        elif self.orientation == 'right':
            for i in range(num_spikes):
                y = draw_rect.top + i * spike_width
                points = [
                    (draw_rect.left, y),
                    (draw_rect.right, y + spike_width // 2),
                    (draw_rect.left, y + spike_width)
                ]
                pygame.draw.polygon(screen, spike_color, points)
                pygame.draw.polygon(screen, settings.COLOR_BLACK, points, 1)
