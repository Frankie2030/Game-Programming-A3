"""
Enhanced Win screen with modern UI/UX design
"""
import pygame
import math
from game.core import GameState, settings


class WinState(GameState):
    """Enhanced victory screen with animations and modern design"""
    
    def __init__(self, stack, coins=0, time=0, clear_conditions=None):
        super().__init__(stack)
        self.coins = coins
        self.time = time
        self.clear_conditions = clear_conditions
        self.stars = clear_conditions.get_star_rating() if clear_conditions else 1
        
        # Fonts
        self.title_font = pygame.font.Font(None, 84)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.stats_font = pygame.font.Font(None, 28)
        self.condition_font = pygame.font.Font(None, 24)
        self.instruction_font = pygame.font.Font(None, 20)
        
        # Animation variables
        self.time_elapsed = 0
        self.title_scale = 0
        self.star_animations = [0, 0, 0]  # Individual star animations
        self.stats_alpha = 0
        self.conditions_alpha = 0
        self.pulse_alpha = 255
        
        # Create decorative elements
        self.create_decorative_elements()
    
    def create_decorative_elements(self):
        """Create visual elements for better design"""
        # Create gradient background
        self.bg_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        for y in range(settings.SCREEN_HEIGHT):
            alpha = int(10 + (y / settings.SCREEN_HEIGHT) * 40)
            color = (alpha, alpha + 20, alpha + 10)
            pygame.draw.line(self.bg_surface, color, (0, y), (settings.SCREEN_WIDTH, y))
        
        # Create star icons
        self.star_icons = []
        for i in range(3):
            star = pygame.Surface((40, 40), pygame.SRCALPHA)
            points = []
            for j in range(10):
                angle = j * 3.14159 / 5
                if j % 2 == 0:
                    radius = 18
                else:
                    radius = 8
                x = 20 + radius * math.cos(angle)
                y = 20 + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(star, settings.COLOR_YELLOW, points)
            self.star_icons.append(star)
        
        # Create checkmark and X icons
        self.check_icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.lines(self.check_icon, settings.COLOR_GREEN, False, [(4, 12), (10, 18), (20, 6)], 3)
        
        self.x_icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.line(self.x_icon, settings.COLOR_RED, (4, 4), (20, 20), 3)
        pygame.draw.line(self.x_icon, settings.COLOR_RED, (20, 4), (4, 20), 3)
    
    def update(self, dt, events):
        """Update animations"""
        self.time_elapsed += dt
        
        # Title scale animation
        if self.time_elapsed < 1.0:
            self.title_scale = min(1.0, self.time_elapsed * 1.2)
        else:
            self.title_scale = 1.0 + 0.1 * math.sin(self.time_elapsed * 2)
        
        # Star animations (staggered)
        for i in range(3):
            if self.time_elapsed > 0.5 + i * 0.3:
                self.star_animations[i] = min(1.0, (self.time_elapsed - 0.5 - i * 0.3) * 2)
        
        # Stats fade in
        if self.time_elapsed > 1.5:
            self.stats_alpha = min(255, int((self.time_elapsed - 1.5) * 255))
        
        # Conditions fade in
        if self.time_elapsed > 2.0:
            self.conditions_alpha = min(255, int((self.time_elapsed - 2.0) * 255))
        
        # Pulse effect for continue text
        self.pulse_alpha = int(180 + 75 * abs(math.sin(self.time_elapsed * 3)))
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                from game.ui.main_menu import MainMenuState
                self.stack.clear()
                self.stack.push(MainMenuState)
    
    def draw_animated_stars(self, screen, x, y, earned_stars):
        """Draw animated star rating"""
        for i in range(3):
            star_x = x + (i - 1) * 60
            star_y = y
            
            # Scale animation
            scale = 0.3 + self.star_animations[i] * 0.7
            if i < earned_stars:
                # Earned star - golden and animated
                star_surf = pygame.transform.scale(self.star_icons[i], (int(40 * scale), int(40 * scale)))
                # Add glow effect
                glow_surf = pygame.transform.scale(self.star_icons[i], (int(50 * scale), int(50 * scale)))
                glow_surf.set_alpha(100)
                screen.blit(glow_surf, (star_x - 25, star_y - 25))
                screen.blit(star_surf, (star_x - 20, star_y - 20))
            else:
                # Unearned star - gray and static
                star_surf = pygame.transform.scale(self.star_icons[i], (int(30 * scale), int(30 * scale)))
                # Make it gray
                star_surf.fill((100, 100, 100), special_flags=pygame.BLEND_MULT)
                screen.blit(star_surf, (star_x - 15, star_y - 15))
    
    def draw_condition(self, screen, x, y, text, completed, alpha=255):
        """Draw a clear condition with icon"""
        # Background panel
        panel = pygame.Surface((400, 40), pygame.SRCALPHA)
        panel.set_alpha(alpha)
        panel.fill((20, 20, 20))
        pygame.draw.rect(panel, (60, 60, 60), (0, 0, 400, 40), 2)
        screen.blit(panel, (x - 200, y - 20))
        
        # Icon
        icon = self.check_icon if completed else self.x_icon
        icon.set_alpha(alpha)
        screen.blit(icon, (x - 180, y - 12))
        
        # Text
        color = settings.COLOR_GREEN if completed else settings.COLOR_RED
        text_surf = self.condition_font.render(text, True, color)
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, (x - 150, y - 10))
    
    def draw(self, screen):
        """Draw enhanced win screen"""
        # Background with gradient
        screen.blit(self.bg_surface, (0, 0))
        
        # Add animated particles
        for i in range(30):
            x = (i * 43 + self.time_elapsed * 100) % settings.SCREEN_WIDTH
            y = (i * 67 + self.time_elapsed * 80) % settings.SCREEN_HEIGHT
            alpha = int(50 + 30 * abs(math.sin(self.time_elapsed + i)))
            particle_color = (alpha, alpha + 50, alpha + 100)
            pygame.draw.circle(screen, particle_color, (int(x), int(y)), 2)
        
        # Main title with scale animation and glow
        title_text = "MISSION COMPLETE!"
        title_surf = self.title_font.render(title_text, True, settings.COLOR_GREEN)
        
        # Scale the title
        scaled_width = int(title_surf.get_width() * self.title_scale)
        scaled_height = int(title_surf.get_height() * self.title_scale)
        scaled_title = pygame.transform.scale(title_surf, (scaled_width, scaled_height))
        
        # Title glow effect
        for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            glow_rect = scaled_title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=80)
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            glow_surf = pygame.transform.scale(title_surf, (scaled_width, scaled_height))
            glow_surf.set_alpha(100)
            screen.blit(glow_surf, glow_rect)
        
        # Draw scaled title
        title_rect = scaled_title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=80)
        screen.blit(scaled_title, title_rect)
        
        # Animated star rating
        self.draw_animated_stars(screen, settings.SCREEN_WIDTH // 2, 160, self.stars)
        
        # Stats section with fade-in
        if self.stats_alpha > 0:
            # Stats background panel
            stats_panel = pygame.Surface((500, 120), pygame.SRCALPHA)
            stats_panel.set_alpha(self.stats_alpha)
            stats_panel.fill((10, 10, 10))
            pygame.draw.rect(stats_panel, (40, 40, 40), (0, 0, 500, 120), 2)
            screen.blit(stats_panel, (settings.SCREEN_WIDTH // 2 - 250, 220))
            
            # Stats text
            stats_text = [
                f"Data Canisters Delivered: {self.coins}",
                f"Completion Time: {self.time:.1f}s"
            ]
            
            for i, text in enumerate(stats_text):
                text_surf = self.stats_font.render(text, True, settings.COLOR_WHITE)
                text_surf.set_alpha(self.stats_alpha)
                text_rect = text_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=250 + i * 40)
                screen.blit(text_surf, text_rect)
        
        # Clear conditions section
        if self.conditions_alpha > 0 and self.clear_conditions:
            # Conditions background panel
            conditions_panel = pygame.Surface((500, 180), pygame.SRCALPHA)
            conditions_panel.set_alpha(self.conditions_alpha)
            conditions_panel.fill((10, 10, 10))
            pygame.draw.rect(conditions_panel, (40, 40, 40), (0, 0, 500, 180), 2)
            screen.blit(conditions_panel, (settings.SCREEN_WIDTH // 2 - 250, 360))
            
            # Section title
            section_title = self.subtitle_font.render("CLEAR CONDITIONS:", True, settings.COLOR_YELLOW)
            section_title.set_alpha(self.conditions_alpha)
            section_rect = section_title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=380)
            screen.blit(section_title, section_rect)
            
            # Conditions
            defeated, total = self.clear_conditions.get_enemies_progress()
            conditions = [
                ("Defeat Boss", self.clear_conditions.boss_defeated),
                (f"Defeat All Enemies ({defeated}/{total})", defeated >= total),
                (f"Complete in {settings.TIME_LIMIT_3_STAR}s", self.time <= settings.TIME_LIMIT_3_STAR)
            ]
            
            for i, (text, completed) in enumerate(conditions):
                self.draw_condition(screen, settings.SCREEN_WIDTH // 2, 420 + i * 35, text, completed, self.conditions_alpha)
        
        # Final message
        if self.conditions_alpha > 0:
            message = self.subtitle_font.render("The station is secure.", True, settings.COLOR_GREEN)
            message.set_alpha(self.conditions_alpha)
            message_rect = message.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=580)
            screen.blit(message, message_rect)
        
        # Continue instruction with pulse
        continue_text = self.instruction_font.render("Press ENTER to continue", True, (self.pulse_alpha, self.pulse_alpha, self.pulse_alpha))
        continue_rect = continue_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 30)
        screen.blit(continue_text, continue_rect)
        
        # Decorative corner elements
        corner_size = 30
        corner_color = (80, 80, 80)
        # Top corners
        pygame.draw.lines(screen, corner_color, False, [(30, 30), (30, 30 + corner_size), (30 + corner_size, 30)], 3)
        pygame.draw.lines(screen, corner_color, False, [(settings.SCREEN_WIDTH - 30, 30), (settings.SCREEN_WIDTH - 30, 30 + corner_size), (settings.SCREEN_WIDTH - 30 - corner_size, 30)], 3)
        # Bottom corners
        pygame.draw.lines(screen, corner_color, False, [(30, settings.SCREEN_HEIGHT - 30), (30, settings.SCREEN_HEIGHT - 30 - corner_size), (30 + corner_size, settings.SCREEN_HEIGHT - 30)], 3)
        pygame.draw.lines(screen, corner_color, False, [(settings.SCREEN_WIDTH - 30, settings.SCREEN_HEIGHT - 30), (settings.SCREEN_WIDTH - 30, settings.SCREEN_HEIGHT - 30 - corner_size), (settings.SCREEN_WIDTH - 30 - corner_size, settings.SCREEN_HEIGHT - 30)], 3)
