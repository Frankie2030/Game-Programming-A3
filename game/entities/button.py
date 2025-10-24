"""
Button entity - can be stomped or shot to toggle gates
"""
import pygame
from game.core import settings


class Button:
    """Button that can be activated by stomping or shooting"""
    
    def __init__(self, x, y, color='red', facing='up'):
        # Make button bigger (1.5x tile size)
        button_width = int(settings.TILE_SIZE * 2)
        button_height = int(settings.TILE_SIZE * 1)
        self.rect = pygame.Rect(x, y, button_width, button_height)
        self.color = color
        self.facing = facing  # 'up', 'down', 'left', 'right'
        self.pressed = False
        self.press_timer = 0
        self.activation_cooldown = 0  # Prevent double-activation from multiple bullets
        self.on_toggle = None  # Callback function when button is toggled
        
        # Visual properties
        self.base_y = y
        self.press_depth = 4  # How far button sinks when pressed
    
    def check_stomp(self, player_rect, player_vel_y, player_gravity_dir):
        """Check if player stomped the button"""
        if not self.rect.colliderect(player_rect):
            return False
        
        # Check if player is moving towards button
        if player_gravity_dir == 1 and player_vel_y > 0:  # Normal gravity, falling
            # Player must be above button
            if player_rect.bottom <= self.rect.centery:
                return True
        elif player_gravity_dir == -1 and player_vel_y < 0:  # Inverted gravity
            # Player must be below button
            if player_rect.top >= self.rect.centery:
                return True
        
        return False
    
    def check_bullet_hit(self, bullet_rect):
        """Check if bullet hit the button (only if not on cooldown)"""
        if self.activation_cooldown > 0:
            return False
        return self.rect.colliderect(bullet_rect)
    
    def activate(self):
        """Activate the button (toggle state)"""
        if self.activation_cooldown > 0:
            return  # Still on cooldown, ignore activation
        
        self.pressed = not self.pressed
        self.press_timer = 0.2  # Visual feedback duration
        self.activation_cooldown = 0.3  # Cooldown to prevent rapid toggling
        
        # Call the callback if set
        if self.on_toggle:
            self.on_toggle()
    
    def update(self, dt):
        """Update button state"""
        if self.press_timer > 0:
            self.press_timer -= dt
        if self.activation_cooldown > 0:
            self.activation_cooldown -= dt
    
    def draw(self, screen, camera):
        """Draw the button"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Apply press animation
        if self.press_timer > 0:
            draw_rect.y += self.press_depth
        
        # Choose color based on state
        if self.pressed:
            button_color = (100, 200, 100) if self.color == 'green' else (200, 50, 50)
        else:
            button_color = (80, 180, 80) if self.color == 'green' else (150, 30, 30)
        
        # Create button surface
        button_surf = pygame.Surface((self.rect.width, self.rect.height))
        button_surf.fill(button_color)
        
        # Draw border
        pygame.draw.rect(button_surf, settings.COLOR_BLACK, button_surf.get_rect(), 2)
        
        # Draw highlight
        highlight_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height // 3)
        highlight_color = tuple(min(255, c + 40) for c in button_color)
        pygame.draw.rect(button_surf, highlight_color, highlight_rect)
        
        # Draw arrow (always pointing up on surface)
        arrow_color = (255, 255, 255)
        center_x = self.rect.width // 2
        center_y = self.rect.height // 2
        arrow_size = 8
        arrow_points = [
            (center_x, center_y - arrow_size),
            (center_x - arrow_size // 2, center_y),
            (center_x + arrow_size // 2, center_y)
        ]
        pygame.draw.polygon(button_surf, arrow_color, arrow_points)
        
        # Rotate surface based on facing
        if self.facing == 'down':
            button_surf = pygame.transform.rotate(button_surf, 180)
        elif self.facing == 'left':
            button_surf = pygame.transform.rotate(button_surf, 90)
        elif self.facing == 'right':
            button_surf = pygame.transform.rotate(button_surf, -90)
        
        # Blit rotated surface
        rotated_rect = button_surf.get_rect(center=(draw_rect.centerx, draw_rect.centery))
        screen.blit(button_surf, rotated_rect)
