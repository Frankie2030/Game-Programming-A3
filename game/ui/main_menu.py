"""
Main menu
"""
import math
import pygame
from game.core import GameState, settings
from game.core.save_system import SaveSystem
from game.world.background import ParallaxBackground


class MainMenuState(GameState):
    """Main menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self._update_options()
        
        # Animated background reused from gameplay
        self.background = ParallaxBackground(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self._bg_time = 0.0
        
        # Mouse navigation support
        self.option_rects = []
        self.mouse_enabled = True
        
        # Visual polish
        self._pulse_time = 0.0
    
    def enter(self, previous_state=None):
        """Called when entering this state"""
        audio = self.stack.persistent_data.get('audio')
        if audio:
            audio.play_music(audio.MUSIC_MENU)
    
    def _update_options(self):
        """Update menu options based on save state"""
        if SaveSystem.has_resume():
            self.options = ['Resume Game', 'Level Select', 'New Game', 'How to Play', 'Options', 'About', 'Exit']
        else:
            self.options = ['New Game', 'Level Select', 'How to Play', 'Options', 'About', 'Exit']
        self.selected = 0
    
    def update(self, dt, events):
        """Update menu"""
        # Animate background with gentle auto-scroll and sway
        self._bg_time += dt
        sway = math.sin(self._bg_time * 0.25) * 60  # slow sway
        auto_scroll = self._bg_time * 30.0  # slow constant scroll
        self.background.update(auto_scroll + sway)
        
        # Pulse for selected highlight
        self._pulse_time += dt
    
    def handle_event(self, event):
        """Handle input"""
        # Call parent to handle mute toggle
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_option()
        elif event.type == pygame.MOUSEMOTION and self.mouse_enabled:
            mx, my = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mx, my):
                    self.selected = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.mouse_enabled:
            mx, my = event.pos
            if 0 <= self.selected < len(self.option_rects) and self.option_rects[self.selected].collidepoint(mx, my):
                self._select_option()
    
    def _select_option(self):
        """Handle menu selection"""
        option = self.options[self.selected]
        
        if option == 'Resume Game':
            from game.world.level import LevelState
            # Resume the current level from saved checkpoint
            level_id = SaveSystem.get_current_level()
            if level_id:
                self.stack.push_with_transition(LevelState, level_id=level_id, restore_checkpoint=True)
        elif option == 'Level Select':
            from game.ui.level_select import LevelSelectState
            self.stack.push_with_transition(LevelSelectState)
        elif option == 'New Game':
            from game.world.level import LevelState
            # Delete existing save when starting new game
            SaveSystem.delete_save()
            self.stack.push_with_transition(LevelState, level_id=1)
        elif option == 'How to Play':
            from game.ui.how_to_play import HowToPlayState
            self.stack.push(HowToPlayState)
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
        # Background
        self.background.draw(screen)
        
        # Soft vignette overlay for readability
        vignette = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        vignette.fill((0, 0, 0, 110))
        screen.blit(vignette, (0, 0))
        
        # Title
        title_text = "GRAVITY COURIER"
        # Drop shadow
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(centerx=settings.SCREEN_WIDTH // 2 + 3, y=97)
        screen.blit(shadow, shadow_rect)
        # Foreground title
        title = self.title_font.render(title_text, True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=94)
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle = subtitle_font.render("Flip gravity. Deliver data. Survive.", True, settings.COLOR_WHITE)
        subtitle_rect = subtitle.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=180)
        screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 300
        self.option_rects = []
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.menu_font.render(option, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + i * 60)
            
            # Pulsing background highlight for selected option
            if i == self.selected:
                pulse = (math.sin(self._pulse_time * 6.0) * 0.5 + 0.5)  # 0..1
                highlight_alpha = int(80 + 70 * pulse)
                pad_x, pad_y = 18, 8
                highlight = pygame.Surface((rect.width + pad_x * 2, rect.height + pad_y * 2), pygame.SRCALPHA)
                highlight.fill((255, 220, 50, highlight_alpha))
                screen.blit(highlight, (rect.x - pad_x, rect.y - pad_y))
            
            screen.blit(text, rect)
            self.option_rects.append(rect)
            
            # Selection indicator
            if i == self.selected:
                indicator = self.menu_font.render(">", True, settings.COLOR_YELLOW)
                screen.blit(indicator, (rect.left - 50, rect.top))
        
        # Show save info if available
        if SaveSystem.has_resume():
            save_info = SaveSystem.get_save_info()
            if save_info:
                info_text = f"In Progress: Level {save_info['current_level']} | Attempt #{save_info['attempts']}"
                info_surf = self.small_font.render(info_text, True, settings.COLOR_GRAY)
                info_rect = info_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + len(self.options) * 60 + 20)
                screen.blit(info_surf, info_rect)

        # Mute indicator (top right)
        audio = self.stack.persistent_data.get('audio')
        if audio and audio.is_muted():
            muted_text = "MUTED"
            muted_surf = self.menu_font.render(muted_text, True, settings.COLOR_RED)
            muted_rect = muted_surf.get_rect(right=settings.SCREEN_WIDTH - 20, top=20)
            # Background for visibility
            bg_rect = muted_rect.inflate(20, 10)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 160))
            screen.blit(bg_surf, bg_rect.topleft)
            screen.blit(muted_surf, muted_rect)
        
        # Footer hints
        footer = self.small_font.render("Enter/Click: Select   W/S or Up/Down: Navigate   M: Mute   Esc: Quit", True, settings.COLOR_WHITE)
        screen.blit(footer, (20, settings.SCREEN_HEIGHT - 34))
