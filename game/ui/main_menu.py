"""
Main menu
"""
import pygame
from game.core import GameState, settings
from game.core.save_system import SaveSystem


class MainMenuState(GameState):
    """Main menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self._update_options()
    
    def _update_options(self):
        """Update menu options based on save state"""
        if SaveSystem.has_save():
            self.options = ['Resume Game', 'New Game', 'Options', 'About', 'Exit']
        else:
            self.options = ['New Game', 'Options', 'About', 'Exit']
        self.selected = 0
    
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
        
        if option == 'Resume Game':
            from game.world.level import LevelState
            # Load saved game data and pass it to LevelState
            save_data = SaveSystem.load_game()
            if save_data:
                self.stack.push(LevelState, save_data=save_data)
        elif option == 'New Game':
            from game.world.level import LevelState
            # Delete existing save when starting new game
            SaveSystem.delete_save()
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
        
        # Show save info if available
        if SaveSystem.has_save():
            save_info = SaveSystem.get_save_info()
            if save_info:
                boss_status = "Defeated" if save_info['boss_defeated'] else f"HP: {save_info['boss_hp']}"
                info_text = f"Save: Level {save_info['level']} | {save_info['coins']} coins | {save_info['game_time']:.1f}s | Boss: {boss_status}"
                info_surf = self.small_font.render(info_text, True, settings.COLOR_GRAY)
                info_rect = info_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + len(self.options) * 60 + 20)
                screen.blit(info_surf, info_rect)
