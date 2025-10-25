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
        self.dealt_damage = False  # Track if we dealt damage this contact
    
    def check_collision(self, player_rect, player_gravity_dir, player_invulnerable):
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
        
        # Reset dealt_damage flag when player is no longer invulnerable
        if not player_invulnerable:
            self.dealt_damage = False
        
        # Deal damage if touching dangerous side and haven't dealt damage yet
        if should_damage and not self.dealt_damage:
            self.dealt_damage = True
            return True
        
        # Reset when player leaves spike completely
        if not is_touching:
            self.dealt_damage = False
        
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
        
        elif self.orientation == 'down':
            for i in range(num_spikes):
                x = draw_rect.left + i * spike_width
                points = [
                    (x, draw_rect.top),
                    (x + spike_width // 2, draw_rect.bottom),
                    (x + spike_width, draw_rect.top)
                ]
                pygame.draw.polygon(screen, spike_color, points)
        
        elif self.orientation == 'left':
            for i in range(num_spikes):
                y = draw_rect.top + i * spike_width
                points = [
                    (draw_rect.right, y),
                    (draw_rect.left, y + spike_width // 2),
                    (draw_rect.right, y + spike_width)
                ]
                pygame.draw.polygon(screen, spike_color, points)
        
        elif self.orientation == 'right':
            for i in range(num_spikes):
                y = draw_rect.top + i * spike_width
                points = [
                    (draw_rect.left, y),
                    (draw_rect.right, y + spike_width // 2),
                    (draw_rect.left, y + spike_width)
                ]
                pygame.draw.polygon(screen, spike_color, points)


class AnimatedSpike:
    """Animated spike that grows from floor/ceiling (for boss attacks)"""
    
    def __init__(self, x, y, orientation='up', telegraph_time=1, grow_time=0.5, active_time=1.5, retract_time=0.5):
        self.x = x
        self.y = y
        self.orientation = orientation  # 'up' or 'down'
        self.telegraph_time = telegraph_time  # Time warning indicator shows
        self.grow_time = grow_time  # Time to fully extend
        self.active_time = active_time  # Time spike stays extended
        self.retract_time = retract_time  # Time to retract
        
        self.total_duration = telegraph_time + grow_time + active_time + retract_time
        self.timer = 0
        self.state = 'telegraph'  # 'telegraph', 'growing', 'active', 'retracting', 'done'
        
        self.max_height = 64  # Maximum spike height in pixels
        self.width = settings.TILE_SIZE
        self.current_height = 0
        
        self.player_touching = False
    
    def update(self, dt):
        """Update spike animation"""
        self.timer += dt
        
        if self.state == 'telegraph':
            if self.timer >= self.telegraph_time:
                self.state = 'growing'
                self.timer = 0
        
        elif self.state == 'growing':
            progress = min(1.0, self.timer / self.grow_time)
            self.current_height = self.max_height * progress
            if self.timer >= self.grow_time:
                self.state = 'active'
                self.timer = 0
                self.current_height = self.max_height
        
        elif self.state == 'active':
            if self.timer >= self.active_time:
                self.state = 'retracting'
                self.timer = 0
        
        elif self.state == 'retracting':
            progress = min(1.0, self.timer / self.retract_time)
            self.current_height = self.max_height * (1.0 - progress)
            if self.timer >= self.retract_time:
                self.state = 'done'
                self.current_height = 0
    
    def is_done(self):
        return self.state == 'done'
    
    def is_dangerous(self):
        """Returns True if spike can damage player"""
        return self.state in ['growing', 'active', 'retracting']
    
    def get_hitbox(self):
        """Get current collision rectangle"""
        if self.orientation == 'up':
            return pygame.Rect(self.x, self.y - self.current_height, self.width, self.current_height)
        else:  # 'down'
            return pygame.Rect(self.x, self.y, self.width, self.current_height)
    
    def check_collision(self, player_rect, player_gravity_dir):
        """Check if player hit spike and should take damage"""
        if not self.is_dangerous():
            return False
        
        hitbox = self.get_hitbox()
        is_touching = hitbox.colliderect(player_rect)
        
        # Only damage on FIRST contact
        if is_touching and not self.player_touching:
            self.player_touching = True
            return True
        
        if not is_touching:
            self.player_touching = False
        
        return False
    
    def draw(self, screen, camera):
        """Draw animated spike"""
        draw_x = self.x - camera.x
        draw_y = self.y - camera.y
        
        # Draw telegraph indicator
        if self.state == 'telegraph':
            alpha = int(128 + 127 * (self.timer / self.telegraph_time))
            color = (255, 255, 0, alpha)  # Yellow warning
            indicator_rect = pygame.Rect(draw_x, draw_y - 10, self.width, 10)
            if self.orientation == 'down':
                indicator_rect.y = draw_y
            
            # Draw pulsing warning box
            pygame.draw.rect(screen, (255, 255, 0), indicator_rect)
            pygame.draw.rect(screen, (255, 200, 0), indicator_rect, 2)
        
        # Draw spike if it's growing/active/retracting
        if self.current_height > 0:
            spike_color = (200, 50, 50)  # Red for danger
            num_spikes = 4
            spike_width = self.width // num_spikes
            
            if self.orientation == 'up':
                base_y = draw_y
                tip_y = draw_y - self.current_height
                for i in range(num_spikes):
                    x = draw_x + i * spike_width
                    points = [
                        (x, base_y),
                        (x + spike_width // 2, tip_y),
                        (x + spike_width, base_y)
                    ]
                    pygame.draw.polygon(screen, spike_color, points)
                    pygame.draw.polygon(screen, (150, 30, 30), points, 2)
            
            else:  # 'down'
                base_y = draw_y
                tip_y = draw_y + self.current_height
                for i in range(num_spikes):
                    x = draw_x + i * spike_width
                    points = [
                        (x, base_y),
                        (x + spike_width // 2, tip_y),
                        (x + spike_width, base_y)
                    ]
                    pygame.draw.polygon(screen, spike_color, points)
                    pygame.draw.polygon(screen, (150, 30, 30), points, 2)
