"""
Interactive tile entities (crates, coin boxes, etc.)
"""
import pygame
from game.core import settings


class Crate:
    """Breakable crate that spawns items"""
    
    def __init__(self, x, y, contents='coin'):
        self.rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
        self.contents = contents  # 'coin', 'star', or None
        self.broken = False
        self.solid = True
    
    def hit(self, side):
        """Hit the crate from a side"""
        if not self.broken:
            self.broken = True
            self.solid = False
            return self.contents
        return None
    
    def is_solid(self):
        """Check if crate blocks movement"""
        return self.solid and not self.broken
    
    def draw(self, screen, camera):
        """Draw crate"""
        if self.broken:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Draw crate
        pygame.draw.rect(screen, (139, 69, 19), draw_rect)  # Brown
        pygame.draw.rect(screen, settings.COLOR_BLACK, draw_rect, 2)
        
        # Draw wood grain lines
        for i in range(3):
            y_offset = (i + 1) * settings.TILE_SIZE // 4
            pygame.draw.line(screen, (101, 50, 15),
                           (draw_rect.left, draw_rect.top + y_offset),
                           (draw_rect.right, draw_rect.top + y_offset), 1)


class CoinBox:
    """Question box that spawns a coin when hit"""
    
    def __init__(self, x, y, coin_count=1):
        self.rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
        self.coins_left = coin_count
        self.solid = True
        self.hit_cooldown = 0
    
    def hit(self, side):
        """Hit the box from a side"""
        if self.coins_left > 0 and self.hit_cooldown <= 0:
            self.coins_left -= 1
            self.hit_cooldown = 0.5  # Prevent spam
            return 'coin'
        return None
    
    def update(self, dt):
        """Update cooldown"""
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt
    
    def is_solid(self):
        """Check if box blocks movement"""
        return self.solid
    
    def draw(self, screen, camera):
        """Draw coin box"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Choose color based on state
        if self.coins_left > 0:
            color = settings.COLOR_YELLOW
        else:
            color = settings.COLOR_GRAY
        
        pygame.draw.rect(screen, color, draw_rect)
        pygame.draw.rect(screen, settings.COLOR_BLACK, draw_rect, 2)
        
        # Draw question mark if has coins
        if self.coins_left > 0:
            font = pygame.font.Font(None, 24)
            text = font.render('?', True, settings.COLOR_BLACK)
            text_rect = text.get_rect(center=draw_rect.center)
            screen.blit(text, text_rect)


class CoinBrick:
    """Brick with embedded coins"""
    
    def __init__(self, x, y, coin_count=5):
        self.rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
        self.coins_left = coin_count
        self.solid = True
        self.hit_cooldown = 0
    
    def hit(self, side):
        """Hit the brick"""
        if self.coins_left > 0 and self.hit_cooldown <= 0:
            self.coins_left -= 1
            self.hit_cooldown = 0.3
            return 'coin'
        return None
    
    def update(self, dt):
        """Update cooldown"""
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt
    
    def is_solid(self):
        """Check if brick blocks movement"""
        return self.solid
    
    def draw(self, screen, camera):
        """Draw brick"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Color changes as coins depleted
        if self.coins_left > 3:
            color = (180, 100, 50)  # Rich brick
        elif self.coins_left > 0:
            color = (150, 80, 40)  # Depleting
        else:
            color = (100, 60, 30)  # Empty
        
        pygame.draw.rect(screen, color, draw_rect)
        pygame.draw.rect(screen, settings.COLOR_BLACK, draw_rect, 1)
        
        # Draw brick pattern
        mid_x = draw_rect.centerx
        mid_y = draw_rect.centery
        pygame.draw.line(screen, settings.COLOR_BLACK,
                        (draw_rect.left, mid_y), (draw_rect.right, mid_y), 1)
