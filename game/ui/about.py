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
        
        # Scrolling variables
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 100  # pixels per second
        self.auto_scroll = True
        self.auto_scroll_direction = 1  # 1 for down, -1 for up
        self.auto_scroll_pause_time = 0
        self.auto_scroll_pause_duration = 2.0  # pause for 2 seconds at top/bottom
        
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
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.scroll_y = max(0, self.scroll_y - 50)
                self.auto_scroll = False
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 50)
                self.auto_scroll = False
            elif event.key == pygame.K_SPACE:
                self.auto_scroll = not self.auto_scroll
    
    def update(self, dt, events):
        """Update animations"""
        self.time += dt
        # Pulse effect for return instruction
        self.pulse_alpha = int(180 + 75 * abs(math.sin(self.time * 3)))
        
        # Handle auto-scrolling
        if self.auto_scroll:
            if self.auto_scroll_pause_time > 0:
                self.auto_scroll_pause_time -= dt
            else:
                self.scroll_y += self.auto_scroll_direction * self.scroll_speed * dt
                
                # Check bounds and reverse direction
                if self.scroll_y <= 0:
                    self.scroll_y = 0
                    self.auto_scroll_direction = 1
                    self.auto_scroll_pause_time = self.auto_scroll_pause_duration
                elif self.scroll_y >= self.max_scroll:
                    self.scroll_y = self.max_scroll
                    self.auto_scroll_direction = -1
                    self.auto_scroll_pause_time = self.auto_scroll_pause_duration
        
        # Clamp scroll position
        self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
    
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
        
        # Create a surface for scrolling content
        content_height = 1200  # Estimate total content height
        content_surface = pygame.Surface((settings.SCREEN_WIDTH, content_height), pygame.SRCALPHA)
        
        # Calculate max scroll based on content height
        self.max_scroll = max(0, content_height - settings.SCREEN_HEIGHT + 100)
        
        # Add some subtle animated stars in background
        for i in range(20):
            x = (i * 67) % settings.SCREEN_WIDTH
            y = (i * 43 + self.time * 50) % settings.SCREEN_HEIGHT
            alpha = int(50 + 30 * abs(math.sin(self.time + i)))
            star_color = (alpha, alpha, alpha)
            pygame.draw.circle(content_surface, star_color, (int(x), int(y)), 1)
        
        # Main title with glow effect
        title_text = self.title_font.render("ABOUT GRAVITY COURIER", True, settings.COLOR_YELLOW)
        title_rect = title_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=60)
        
        # Title glow
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            glow_text = self.title_font.render("ABOUT GRAVITY COURIER", True, (100, 100, 0))
            content_surface.blit(glow_text, glow_rect)
        
        content_surface.blit(title_text, title_rect)
        
        # Game description
        desc_text = self.body_font.render("You're a bike courier inside a rotating space station.", True, settings.COLOR_WHITE)
        desc_rect = desc_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=120)
        content_surface.blit(desc_text, desc_rect)
        
        desc2_text = self.body_font.render("Deliver data canisters and reach the terminal.", True, settings.COLOR_WHITE)
        desc2_rect = desc2_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=150)
        content_surface.blit(desc2_text, desc2_rect)
        
        # Power description with icon
        power_text = self.body_font.render("Your power: flip gravity at will.", True, settings.COLOR_BLUE)
        power_rect = power_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=180)
        content_surface.blit(self.icons['gravity'], (power_rect.x - 30, power_rect.y - 2))
        content_surface.blit(power_text, power_rect)
        
        # Controls section
        controls_items = [
            "Arrow Keys / WASD - Move",
            "Space / W / Up - Jump", 
            "E / Shift - Flip Gravity",
            "ESC - Pause"
        ]
        y = self.draw_section(content_surface, "CONTROLS", controls_items, 220, 'gravity')
        
        # Gameplay section
        gameplay_items = [
            "- Collect coins (data canisters)",
            "- Flip gravity to navigate ceiling and floor",
            "- Stomp enemies from opposite gravity",
            "- Break crates and panels from correct side",
            "- Grab Flux Surge (star) for invincibility",
            "- Defeat Gyro-Core boss to win"
        ]
        y = self.draw_section(content_surface, "GAMEPLAY", gameplay_items, y + 20, 'coin')
        
        # Credits section
        credits_items = [
            "Background Art: Cyberpunk City Skyline",
            "Music: Cyberpunk Street Theme",
            "Assets: Public Domain / Creative Commons",
            "Game Engine: Pygame",
            "Developer: Student Project"
        ]
        y = self.draw_section(content_surface, "CREDITS", credits_items, y + 20, 'star')
        
        # Additional sections for scrolling
        features_items = [
            "- Parallax scrolling background",
            "- Dynamic gravity mechanics",
            "- Multiple enemy types",
            "- Power-up system",
            "- Boss battle mechanics",
            "- Save/Load system"
        ]
        y = self.draw_section(content_surface, "FEATURES", features_items, y + 20, 'boss')
        
        # Technical info
        tech_items = [
            "- Built with Python & Pygame",
            "- Resolution: 1280x720",
            "- Target FPS: 60",
            "- Tile-based level system",
            "- Collision detection system"
        ]
        y = self.draw_section(content_surface, "TECHNICAL", tech_items, y + 20, 'star')
        
        # Return instruction with pulse effect
        return_text = self.small_font.render("Press ESC or ENTER to return", True, (self.pulse_alpha, self.pulse_alpha, self.pulse_alpha))
        return_rect = return_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y + 30)
        content_surface.blit(return_text, return_rect)
        
        # Scroll instructions
        scroll_text = self.small_font.render("Arrow Keys: Manual scroll | Space: Toggle auto-scroll", True, (150, 150, 150))
        scroll_rect = scroll_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y + 60)
        content_surface.blit(scroll_text, scroll_rect)
        
        # Blit the scrolled content to screen
        screen.blit(content_surface, (0, -self.scroll_y))
        
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
