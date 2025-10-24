"""
Lose/Game Over screen
"""
import math
import pygame
from game.core import GameState, settings
from game.world.background import ParallaxBackground
from game.core.save_system import SaveSystem


class LoseState(GameState):
    """Game over screen"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.options = ['Retry', 'Main Menu']
        self.selected = 0
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self.option_rects = []
        self.mouse_enabled = True
        self._pulse_time = 0.0
        
        # Animated background like main menu
        self.background = ParallaxBackground(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self._bg_time = 0.0
    
    def enter(self, previous_state=None):
        """Called when entering this state"""
        audio = self.stack.persistent_data.get('audio')
        if audio:
            audio.stop_music()
            audio.play_sfx('game_over')
    
    def handle_event(self, event):
        """Handle input"""
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
    
    def update(self, dt, events):
        """Animate background with gentle auto-scroll and sway (like main menu)."""
        self._bg_time += dt
        sway = math.sin(self._bg_time * 0.25) * 60
        auto_scroll = self._bg_time * 30.0
        self.background.update(auto_scroll + sway)
    
    def _select_option(self):
        """Handle selection"""
        option = self.options[self.selected]
        
        if option == 'Retry':
            # Return to gameplay with transition
            self.stack.pop_with_transition()
        elif option == 'Main Menu':
            # Exit to main menu with transition
            from game.ui.main_menu import MainMenuState
            self.stack.clear_and_push_with_transition(MainMenuState)
    
    def draw(self, screen):
        """Draw game over screen styled like main menu"""
        # Background + dim overlay
        self.background.draw(screen)
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Title with shadow
        title_text = "TRANSMISSION FAILED"
        shadow = pygame.font.Font(None, 72).render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(centerx=settings.SCREEN_WIDTH // 2 + 3, y=120)
        screen.blit(shadow, shadow_rect)
        title = self.title_font.render(title_text, True, settings.COLOR_RED)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=116)
        screen.blit(title, title_rect)

        # Options with pulsing highlight
        start_y = 260
        self._pulse_time += 1.0 / settings.FPS
        self.option_rects = []
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.menu_font.render(option, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + i * 56)

            if i == self.selected:
                pulse = (math.sin(self._pulse_time * 6.0) * 0.5 + 0.5)
                highlight_alpha = int(80 + 70 * pulse)
                pad_x, pad_y = 18, 8
                highlight = pygame.Surface((rect.width + pad_x * 2, rect.height + pad_y * 2), pygame.SRCALPHA)
                highlight.fill((255, 220, 50, highlight_alpha))
                screen.blit(highlight, (rect.x - pad_x, rect.y - pad_y))

            screen.blit(text, rect)
            self.option_rects.append(rect)

            if i == self.selected:
                indicator = self.menu_font.render(">", True, settings.COLOR_YELLOW)
                screen.blit(indicator, (rect.left - 50, rect.top))

        # Footer
        footer = self.small_font.render("Enter/Click: Select   W/S or Up/Down: Navigate", True, settings.COLOR_WHITE)
        screen.blit(footer, (20, settings.SCREEN_HEIGHT - 34))
