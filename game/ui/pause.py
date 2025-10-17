"""
Pause menu
"""
import math
import pygame
from game.core import GameState, settings
from game.world.background import ParallaxBackground
from game.core.save_system import SaveSystem


class PauseState(GameState):
    """Pause menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.options = ['Resume', 'Save & Exit', 'Exit Without Saving', 'Restart', 'Options', 'Main Menu']
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
        """Handle selection"""
        option = self.options[self.selected]
        
        if option == 'Resume':
            self.stack.pop()
        elif option == 'Save & Exit':
            self._save_and_exit()
        elif option == 'Exit Without Saving':
            self._exit_without_saving()
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
    
    def _save_and_exit(self):
        """Save current game state and exit to main menu"""
        # Get current level state
        level_state = None
        for state in self.stack.states:
            if hasattr(state, 'player') and hasattr(state, 'stopwatch'):
                level_state = state
                break
        
        if level_state:
            # Save game data
            player_data = {
                'x': level_state.player.rect.x,
                'y': level_state.player.rect.y,
                'hp': level_state.player.hp,
                'coins': level_state.player.coins,
                'checkpoint_x': level_state.player.checkpoint_pos[0],
                'checkpoint_y': level_state.player.checkpoint_pos[1],
                'gravity_dir': level_state.player.gravity_dir,
                'stamina': level_state.player.stamina,
                'powered_up': level_state.player.powered_up
            }
            
            level_data = {
                'level_id': 1,
                'spawn_x': 64,
                'spawn_y': 576
            }
            
            # Boss data
            boss_data = {
                'hp': level_state.boss.hp if hasattr(level_state, 'boss') else 8,
                'max_hp': level_state.boss.max_hp if hasattr(level_state, 'boss') else 8,
                'alive': level_state.boss.alive if hasattr(level_state, 'boss') else True,
                'defeated': level_state.boss.defeated if hasattr(level_state, 'boss') else False,
                'phase': level_state.boss.phase if hasattr(level_state, 'boss') else 'spin_up',
                'vulnerable': level_state.boss.vulnerable if hasattr(level_state, 'boss') else False,
                'boss_active': getattr(level_state, 'boss_active', False),
                'boss_door_open': getattr(level_state, 'boss_door_open', False)
            }
            
            # Entities data
            entities_data = {
                'coins': [{'x': coin.rect.x, 'y': coin.rect.y, 'collected': coin.collected} for coin in level_state.coins],
                'stars': [{'x': star.rect.x, 'y': star.rect.y, 'collected': star.collected} for star in level_state.stars],
                'powerups': [{'x': p.rect.x, 'y': p.rect.y, 'collected': p.collected, 'type': p.powerup_type} for p in level_state.powerups],
                'enemies': [{'x': e.rect.x, 'y': e.rect.y, 'alive': e.alive} for e in level_state.enemies],
                'breakables': [{'x': b.rect.x, 'y': b.rect.y, 'broken': b.broken, 'contents': b.contents} for b in level_state.breakables]
            }
            
            game_time = level_state.stopwatch.get_time()
            coins_collected = level_state.player.coins
            enemies_defeated = level_state.clear_conditions.enemies_defeated
            
            SaveSystem.save_game(player_data, level_data, game_time, coins_collected, enemies_defeated, boss_data, entities_data)
        
        # Exit to main menu
        from game.ui.main_menu import MainMenuState
        self.stack.clear()
        self.stack.push(MainMenuState)
    
    def _exit_without_saving(self):
        """Exit to main menu without saving"""
        from game.ui.main_menu import MainMenuState
        self.stack.clear()
        self.stack.push(MainMenuState)
    
    def update(self, dt, events):
        """Animate background with gentle auto-scroll and sway (like main menu)."""
        self._bg_time += dt
        sway = math.sin(self._bg_time * 0.25) * 60
        auto_scroll = self._bg_time * 30.0
        self.background.update(auto_scroll + sway)
        
        # Pulse animation timer for selection highlight
        self._pulse_time += dt

    def draw(self, screen):
        """Draw pause menu styled like main menu"""
        # Background + dim overlay
        self.background.draw(screen)
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Title with shadow
        title_text = "PAUSED"
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(centerx=settings.SCREEN_WIDTH // 2 + 3, y=120)
        screen.blit(shadow, shadow_rect)
        title = self.title_font.render(title_text, True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=116)
        screen.blit(title, title_rect)

        # Menu options with pulsing highlight
        start_y = 230
        # _pulse_time advanced in update
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
        footer = self.small_font.render("Enter/Click: Select   W/S or Up/Down: Navigate   Esc: Resume", True, settings.COLOR_WHITE)
        screen.blit(footer, (20, settings.SCREEN_HEIGHT - 34))
