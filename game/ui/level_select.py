"""
Level selection menu
"""
import math
import pygame
from game.core import GameState, settings
from game.core.save_system import SaveSystem
from game.world.background import ParallaxBackground


class LevelSelectState(GameState):
    """Level selection menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.title_font = pygame.font.Font(None, 64)
        self.level_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 20)
        
        # Get unlocked levels from save
        self.unlocked_levels = SaveSystem.get_unlocked_levels()
        
        # Level info
        self.levels = [
            {'id': 1, 'name': 'Station Alpha', 'description': 'Training mission'},
            {'id': 2, 'name': 'Station Beta', 'description': 'Boss fight'}
        ]
        
        self.selected = 0
        
        # Animated background
        self.background = ParallaxBackground(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self._bg_time = 0.0
        self._pulse_time = 0.0
    
    def update(self, dt, events):
        """Update menu"""
        self._bg_time += dt
        sway = math.sin(self._bg_time * 0.25) * 60
        auto_scroll = self._bg_time * 30.0
        self.background.update(auto_scroll + sway)
        
        self._pulse_time += dt
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.levels)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.levels)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_level()
            elif event.key == pygame.K_ESCAPE:
                self.stack.pop()
    
    def _select_level(self):
        """Load selected level"""
        level_id = self.levels[self.selected]['id']
        
        # Check if level is unlocked
        if level_id not in self.unlocked_levels:
            return  # Can't select locked level
        
        from game.world.level import LevelState
        self.stack.pop()  # Remove level select
        self.stack.push_with_transition(LevelState, level_id=level_id)
    
    def draw(self, screen):
        """Draw level select menu"""
        # Background
        self.background.draw(screen)
        
        # Vignette
        vignette = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        vignette.fill((0, 0, 0, 110))
        screen.blit(vignette, (0, 0))
        
        # Title
        title_text = "SELECT LEVEL"
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(centerx=settings.SCREEN_WIDTH // 2 + 3, y=97)
        screen.blit(shadow, shadow_rect)
        
        title = self.title_font.render(title_text, True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=94)
        screen.blit(title, title_rect)
        
        # Level cards
        start_y = 240
        card_width = 400
        card_height = 100
        
        for i, level in enumerate(self.levels):
            level_id = level['id']
            is_unlocked = level_id in self.unlocked_levels
            is_selected = i == self.selected
            
            y_pos = start_y + i * (card_height + 20)
            x_pos = settings.SCREEN_WIDTH // 2 - card_width // 2
            
            # Card background
            if is_selected:
                pulse = (math.sin(self._pulse_time * 6.0) * 0.5 + 0.5)
                bg_alpha = int(120 + 80 * pulse) if is_unlocked else int(50 + 30 * pulse)
                bg_color = (60, 60, 20) if is_unlocked else (40, 20, 20)
            else:
                bg_alpha = 100 if is_unlocked else 40
                bg_color = (40, 40, 20) if is_unlocked else (30, 15, 15)
            
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            card_surf.fill((*bg_color, bg_alpha))
            screen.blit(card_surf, (x_pos, y_pos))
            
            # Card border
            border_color = settings.COLOR_YELLOW if is_selected and is_unlocked else (80, 80, 80) if is_unlocked else (50, 50, 50)
            pygame.draw.rect(screen, border_color, (x_pos, y_pos, card_width, card_height), 3)
            
            # Level number
            level_num_text = f"Level {level_id}"
            level_num_surf = self.level_font.render(level_num_text, True, settings.COLOR_YELLOW if is_unlocked else (80, 80, 80))
            screen.blit(level_num_surf, (x_pos + 20, y_pos + 15))
            
            # Level name
            name_surf = pygame.font.Font(None, 32).render(level['name'], True, settings.COLOR_WHITE if is_unlocked else (100, 100, 100))
            screen.blit(name_surf, (x_pos + 20, y_pos + 50))
            
            # Description
            desc_surf = self.small_font.render(level['description'], True, settings.COLOR_GRAY if is_unlocked else (60, 60, 60))
            screen.blit(desc_surf, (x_pos + 20, y_pos + 75))
            
            # Lock icon for locked levels
            if not is_unlocked:
                lock_text = self.level_font.render("🔒", True, (100, 100, 100))
                screen.blit(lock_text, (x_pos + card_width - 60, y_pos + 30))
            
            # Selection indicator
            if is_selected and is_unlocked:
                indicator = self.level_font.render(">", True, settings.COLOR_YELLOW)
                screen.blit(indicator, (x_pos - 40, y_pos + 30))
        
        # Footer
        footer = self.small_font.render("Enter/Space: Select   W/S or Up/Down: Navigate   Esc: Back", True, settings.COLOR_WHITE)
        screen.blit(footer, (20, settings.SCREEN_HEIGHT - 34))
