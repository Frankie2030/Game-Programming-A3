"""
Main menu
"""
import pygame
from game.core import GameState, settings


class MainMenuState(GameState):
    """Main menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.options = ['New Game', 'Options', 'About', 'Exit']
        self.selected = 0
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
    
    def update(self, dt, events):
        """Update menu"""
        pass
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_option()
    
    def _select_option(self):
        """Handle menu selection"""
        option = self.options[self.selected]
        
        if option == 'New Game':
            from game.world.level import LevelState
            self.stack.push(LevelState)
        elif option == 'Options':
            from game.ui.options import OptionsState
            self.stack.push(OptionsState)
        elif option == 'About':
            from game.ui.about import AboutState
            self.stack.push(AboutState)
        elif option == 'Exit':
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def draw(self, screen):
        """Draw menu"""
        screen.fill(settings.COLOR_BLACK)
        
        # Title
        title = self.title_font.render("GRAVITY COURIER", True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=100)
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle = subtitle_font.render("Flip gravity. Deliver data. Survive.", True, settings.COLOR_WHITE)
        subtitle_rect = subtitle.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=180)
        screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 300
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.menu_font.render(option, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + i * 60)
            screen.blit(text, rect)
            
            # Selection indicator
            if i == self.selected:
                indicator = self.menu_font.render(">", True, settings.COLOR_YELLOW)
                screen.blit(indicator, (rect.left - 50, rect.top))
