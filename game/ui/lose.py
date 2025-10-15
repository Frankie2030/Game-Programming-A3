"""
Lose/Game Over screen
"""
import pygame
from game.core import GameState, settings


class LoseState(GameState):
    """Game over screen"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.options = ['Retry', 'Main Menu']
        self.selected = 0
        self.font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
    
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
        """Handle selection"""
        option = self.options[self.selected]
        
        if option == 'Retry':
            # Return to gameplay and respawn at checkpoint
            self.stack.pop()
        elif option == 'Main Menu':
            from game.ui.main_menu import MainMenuState
            self.stack.clear()
            self.stack.push(MainMenuState)
    
    def draw(self, screen):
        """Draw game over screen"""
        screen.fill(settings.COLOR_BLACK)
        
        # Game Over text
        title = self.font.render("TRANSMISSION FAILED", True, settings.COLOR_RED)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=150)
        screen.blit(title, title_rect)
        
        # Options
        start_y = 350
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.menu_font.render(option, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + i * 70)
            screen.blit(text, rect)
            
            if i == self.selected:
                indicator = self.menu_font.render(">", True, settings.COLOR_YELLOW)
                screen.blit(indicator, (rect.left - 50, rect.top))
