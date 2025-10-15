"""
Enemy entities with gravity-aware combat
"""
import pygame
from game.core import settings, sign

def crop_surface(surface):
    """Crop a surface to its non-transparent bounding box."""
    rect = surface.get_bounding_rect()  # tight bounding box of non-transparent pixels
    return surface.subsurface(rect).copy()


class Enemy:
    """Base enemy class"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0
        self.alive = True
        self.anchor_surface = 'floor'  # 'floor' or 'ceiling'
    
    def update(self, dt, collision_system):
        """Base update"""
        pass
    
    def check_stomp(self, player):
        """Check if player stomped this enemy using proper collision detection"""
        if not self.alive:
            return False
        
        # Calculate overlap on each axis
        overlap_x = min(player.rect.right, self.rect.right) - max(player.rect.left, self.rect.left)
        overlap_y = min(player.rect.bottom, self.rect.bottom) - max(player.rect.top, self.rect.top)
        
        # Must be overlapping to stomp
        if overlap_x <= 0 or overlap_y <= 0:
            return False
        
        # Determine collision side based on which axis has LESS overlap
        # This tells us which direction the collision came from
        
        if overlap_y < overlap_x:
            # Vertical collision (top or bottom)
            if self.anchor_surface == 'floor':
                # Enemy on floor - check if player came from above
                is_from_above = player.rect.centery < self.rect.centery
                is_falling = player.vel_y > 0
                has_correct_gravity = player.gravity_dir == 1
                
                return is_from_above and is_falling and has_correct_gravity
            
            else:  # ceiling
                # Enemy on ceiling - check if player came from below
                is_from_below = player.rect.centery > self.rect.centery
                is_rising = player.vel_y < 0
                has_correct_gravity = player.gravity_dir == -1
                
                return is_from_below and is_rising and has_correct_gravity
        
        # Horizontal collision (left or right) - never a stomp
        return False
    
    def take_damage(self):
        """Defeat the enemy"""
        self.alive = False
    
    def draw(self, screen, camera):
        """Draw enemy"""
        pass


class Drone(Enemy):
    """Patrolling drone enemy"""
    
    def __init__(self, x, y, anchor_surface='floor', patrol_range=128, color='blue'):
        super().__init__(x, y, 40, 30)  # Increased from 28x20 to 48x40

        self.anchor_surface = anchor_surface
        self.patrol_start = x
        self.patrol_range = patrol_range
        self.speed = 60  # px/s
        self.direction = 1
        self.flash_timer = 0
        self.color = color
        
        # Try to load sprite
        self.sprite = None
        try:
            sprite_path = f'game/assets/images/sprites/alien{color}.png'
            self.sprite = pygame.image.load(sprite_path)
            cropped = crop_surface(self.sprite)
            # Scale to fit rect size
            self.sprite = pygame.transform.scale(cropped, (self.rect.width, self.rect.height))
        except:
            pass  # Use colored rect fallback
    
    def update(self, dt, collision_system):
        """Update drone patrol"""
        if not self.alive:
            self.flash_timer -= dt
            return
        
        # Simple patrol: move back and forth
        self.vel_x = self.direction * self.speed
        self.rect.x += self.vel_x * dt
        
        # Turn around at patrol edges
        if self.rect.x < self.patrol_start:
            self.rect.x = self.patrol_start
            self.direction = 1
        elif self.rect.x > self.patrol_start + self.patrol_range:
            self.rect.x = self.patrol_start + self.patrol_range
            self.direction = -1
    
    def take_damage(self):
        """Defeat with flash effect"""
        super().take_damage()
        self.flash_timer = 0.3
    
    def draw(self, screen, camera):
        """Draw drone"""
        if not self.alive and self.flash_timer <= 0:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        if self.sprite and self.alive:
            # Draw sprite
            sprite_to_draw = self.sprite
            
            # Flip horizontally if moving left
            if self.direction < 0:
                sprite_to_draw = pygame.transform.flip(sprite_to_draw, True, False)
            
            # Flip vertically if on ceiling
            if self.anchor_surface == 'ceiling':
                sprite_to_draw = pygame.transform.flip(sprite_to_draw, False, True)
            
            screen.blit(sprite_to_draw, draw_rect)
            
            # Draw attack direction arrow
            self._draw_attack_arrow(screen, draw_rect)
        else:
            # Fallback: colored rect
            if not self.alive:
                color = settings.COLOR_WHITE
            else:
                color = settings.COLOR_RED
            
            pygame.draw.rect(screen, color, draw_rect)
            pygame.draw.rect(screen, settings.COLOR_BLACK, draw_rect, 2)
            
            # Draw directional indicator
            indicator_x = draw_rect.right if self.direction > 0 else draw_rect.left
            indicator_y = draw_rect.centery
            size = 5
            if self.direction > 0:
                points = [(indicator_x, indicator_y), (indicator_x + size, indicator_y - size), (indicator_x + size, indicator_y + size)]
            else:
                points = [(indicator_x, indicator_y), (indicator_x - size, indicator_y - size), (indicator_x - size, indicator_y + size)]
            pygame.draw.polygon(screen, settings.COLOR_BLACK, points)
            
            # Draw anchor indicator (line showing which surface they're on)
            if self.anchor_surface == 'floor':
                pygame.draw.line(screen, settings.COLOR_BLACK,
                               (draw_rect.left, draw_rect.bottom),
                               (draw_rect.right, draw_rect.bottom), 2)
            else:
                pygame.draw.line(screen, settings.COLOR_BLACK,
                               (draw_rect.left, draw_rect.top),
                               (draw_rect.right, draw_rect.top), 2)
    
    def _draw_attack_arrow(self, screen, draw_rect):
        """Draw arrow showing where to attack from"""
        # Arrow color
        arrow_color = (255, 255, 0)  # Yellow
        
        if self.anchor_surface == 'floor':
            # Arrow pointing down (attack from above)
            arrow_x = draw_rect.centerx
            arrow_y = draw_rect.top - 10
            points = [
                (arrow_x, arrow_y - 8),
                (arrow_x - 6, arrow_y),
                (arrow_x + 6, arrow_y)
            ]
        else:  # ceiling
            # Arrow pointing up (attack from below)
            arrow_x = draw_rect.centerx
            arrow_y = draw_rect.bottom + 10
            points = [
                (arrow_x, arrow_y + 8),
                (arrow_x - 6, arrow_y),
                (arrow_x + 6, arrow_y)
            ]
        
        pygame.draw.polygon(screen, arrow_color, points)
        pygame.draw.polygon(screen, settings.COLOR_BLACK, points, 2)
