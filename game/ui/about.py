"""
About/Credits screen with improved UX design
"""
import pygame
import math
from game.core import GameState, settings


class AboutState(GameState):
    """About screen with enhanced visual design"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.title_font = pygame.font.Font(None, 48)
        self.section_font = pygame.font.Font(None, 32)
        self.body_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Animation variables
        self.time = 0
        self.pulse_alpha = 255
        
        # Create decorative elements
        self.create_decorative_elements()
    
    def create_decorative_elements(self):
        """Create visual elements for better design"""
        # Create gradient background
        self.bg_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        for y in range(settings.SCREEN_HEIGHT):
            alpha = int(20 + (y / settings.SCREEN_HEIGHT) * 30)
            color = (alpha, alpha, alpha + 20)
            pygame.draw.line(self.bg_surface, color, (0, y), (settings.SCREEN_WIDTH, y))
        
        # Create section dividers
        self.divider = pygame.Surface((400, 2))
        self.divider.fill(settings.COLOR_YELLOW)
        
        # Create icon surfaces (simple geometric shapes as placeholders)
        self.icons = {
            'coin': self.create_coin_icon(),
            'star': self.create_star_icon(),
            'boss': self.create_boss_icon(),
            'gravity': self.create_gravity_icon()
        }
    
    def create_coin_icon(self):
        """Create a simple coin icon"""
        icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(icon, settings.COLOR_YELLOW, (12, 12), 10)
        pygame.draw.circle(icon, (200, 150, 0), (12, 12), 8)
        return icon
    
    def create_star_icon(self):
        """Create a simple star icon"""
        icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        points = []
        for i in range(10):
            angle = i * 3.14159 / 5
            if i % 2 == 0:
                radius = 12
            else:
                radius = 6
            x = 12 + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            y = 12 + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            points.append((x, y))
        pygame.draw.polygon(icon, settings.COLOR_YELLOW, points)
        return icon
    
    def create_boss_icon(self):
        """Create a simple boss icon"""
        icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(icon, settings.COLOR_RED, (12, 12), 10)
        pygame.draw.circle(icon, (150, 0, 0), (12, 12), 7)
        return icon
    
    def create_gravity_icon(self):
        """Create a simple gravity flip icon"""
        icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.arc(icon, settings.COLOR_BLUE, (2, 2, 20, 20), 0, 3.14159, 3)
        pygame.draw.arc(icon, settings.COLOR_BLUE, (2, 2, 20, 20), 3.14159, 6.28318, 3)
        return icon
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE or event.key == pygame.K_RETURN:
                self.stack.pop()
    
    def update(self, dt, events):
        """Update animations"""
        self.time += dt
        # Pulse effect for return instruction
        self.pulse_alpha = int(180 + 75 * abs(math.sin(self.time * 3)))
    
    def draw_section(self, screen, title, items, y_start, icon_key=None):
        """Draw a section with title and items"""
        y = y_start
        
        # Section title with icon
        if icon_key and icon_key in self.icons:
            icon = self.icons[icon_key]
            screen.blit(icon, (settings.SCREEN_WIDTH // 2 - 200, y - 2))
        
        title_text = self.section_font.render(title, True, settings.COLOR_YELLOW)
        title_rect = title_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y)
        screen.blit(title_text, title_rect)
        y += 40
        
        # Divider
        divider_rect = self.divider.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y)
        screen.blit(self.divider, divider_rect)
        y += 20
        
        # Items
        for item in items:
            if item.startswith('-'):
                # Bullet point with indentation
                text = self.body_font.render(item, True, settings.COLOR_WHITE)
                rect = text.get_rect(x=settings.SCREEN_WIDTH // 2 - 180, y=y)
            else:
                # Regular text
                text = self.body_font.render(item, True, settings.COLOR_WHITE)
                rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y)
            screen.blit(text, rect)
            y += 30
        
        return y
    
    def draw(self, screen):
        """Draw about screen with enhanced design"""
        # Background with gradient
        screen.blit(self.bg_surface, (0, 0))
        
        # Add some subtle animated stars in background
        for i in range(20):
            x = (i * 67) % settings.SCREEN_WIDTH
            y = (i * 43 + self.time * 50) % settings.SCREEN_HEIGHT
            alpha = int(50 + 30 * abs(math.sin(self.time + i)))
            star_color = (alpha, alpha, alpha)
            pygame.draw.circle(screen, star_color, (int(x), int(y)), 1)
        
        # Main title with glow effect
        title_text = self.title_font.render("ABOUT GRAVITY COURIER", True, settings.COLOR_YELLOW)
        title_rect = title_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=60)
        
        # Title glow
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            glow_text = self.title_font.render("ABOUT GRAVITY COURIER", True, (100, 100, 0))
            screen.blit(glow_text, glow_rect)
        
        screen.blit(title_text, title_rect)
        
        # Game description
        desc_text = self.body_font.render("You're a bike courier inside a rotating space station.", True, settings.COLOR_WHITE)
        desc_rect = desc_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=120)
        screen.blit(desc_text, desc_rect)
        
        desc2_text = self.body_font.render("Deliver data canisters and reach the terminal.", True, settings.COLOR_WHITE)
        desc2_rect = desc2_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=150)
        screen.blit(desc2_text, desc2_rect)
        
        # Power description with icon
        power_text = self.body_font.render("Your power: flip gravity at will.", True, settings.COLOR_BLUE)
        power_rect = power_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=180)
        screen.blit(self.icons['gravity'], (power_rect.x - 30, power_rect.y - 2))
        screen.blit(power_text, power_rect)
        
        # Controls section
        controls_items = [
            "Arrow Keys / WASD - Move",
            "Space / W / Up - Jump", 
            "E / Shift - Flip Gravity",
            "ESC - Pause"
        ]
        y = self.draw_section(screen, "CONTROLS", controls_items, 220, 'gravity')
        
        # Gameplay section
        gameplay_items = [
            "- Collect coins (data canisters)",
            "- Flip gravity to navigate ceiling and floor",
            "- Stomp enemies from opposite gravity",
            "- Break crates and panels from correct side",
            "- Grab Flux Surge (star) for invincibility",
            "- Defeat Gyro-Core boss to win"
        ]
        y = self.draw_section(screen, "GAMEPLAY", gameplay_items, y + 20, 'coin')
        
        # Return instruction with pulse effect
        return_text = self.small_font.render("Press ESC or ENTER to return", True, (self.pulse_alpha, self.pulse_alpha, self.pulse_alpha))
        return_rect = return_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 30)
        screen.blit(return_text, return_rect)
        
        # Add some decorative corner elements
        corner_size = 20
        corner_color = (100, 100, 100)
        # Top-left corner
        pygame.draw.lines(screen, corner_color, False, [(20, 20), (20, 20 + corner_size), (20 + corner_size, 20)], 2)
        # Top-right corner
        pygame.draw.lines(screen, corner_color, False, [(settings.SCREEN_WIDTH - 20, 20), (settings.SCREEN_WIDTH - 20, 20 + corner_size), (settings.SCREEN_WIDTH - 20 - corner_size, 20)], 2)
        # Bottom-left corner
        pygame.draw.lines(screen, corner_color, False, [(20, settings.SCREEN_HEIGHT - 20), (20, settings.SCREEN_HEIGHT - 20 - corner_size), (20 + corner_size, settings.SCREEN_HEIGHT - 20)], 2)
        # Bottom-right corner
        pygame.draw.lines(screen, corner_color, False, [(settings.SCREEN_WIDTH - 20, settings.SCREEN_HEIGHT - 20), (settings.SCREEN_WIDTH - 20, settings.SCREEN_HEIGHT - 20 - corner_size), (settings.SCREEN_WIDTH - 20 - corner_size, settings.SCREEN_HEIGHT - 20)], 2)
