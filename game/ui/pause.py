"""
Pause menu
"""
import pygame
from game.core import GameState, settings


class PauseState(GameState):
    """Pause menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.options = ['Resume', 'Restart', 'Options', 'Main Menu']
        self.selected = 0
        self.font = pygame.font.Font(None, 48)
    
    def enter(self, previous_state=None):
        """Pause music on enter"""
        audio = self.persistent_data.get('audio')
        if audio:
            audio.pause_music()
    
    def exit(self):
        """Unpause music on exit"""
        audio = self.persistent_data.get('audio')
        if audio:
            audio.unpause_music()
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self.stack.pop()  # Resume
    
    def _select_option(self):
        """Handle selection"""
        option = self.options[self.selected]
        
        if option == 'Resume':
            self.stack.pop()
        elif option == 'Restart':
            from game.world.level import LevelState
            self.stack.pop()  # Remove pause
            self.stack.replace(LevelState)  # Restart level
        elif option == 'Options':
            from game.ui.options import OptionsState
            self.stack.push(OptionsState)
        elif option == 'Main Menu':
            from game.ui.main_menu import MainMenuState
            self.stack.clear()
            self.stack.push(MainMenuState)
    
    def draw(self, screen):
        """Draw pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(settings.COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font.render("PAUSED", True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=150)
        screen.blit(title, title_rect)
        
        # Options
        start_y = 300
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + i * 60)
            screen.blit(text, rect)
            
            if i == self.selected:
                indicator = self.font.render(">", True, settings.COLOR_YELLOW)
                screen.blit(indicator, (rect.left - 50, rect.top))
