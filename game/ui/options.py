"""
Options menu
"""
import pygame
from game.core import GameState, settings


class OptionsState(GameState):
    """Options/settings menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.selected = 0
        self.font = pygame.font.Font(None, 36)
        self.audio = stack.persistent_data.get('audio')
    
    def update(self, dt, events):
        """Update"""
        pass
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = max(0, self.selected - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = min(2, self.selected + 1)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self._adjust_volume(-0.1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self._adjust_volume(0.1)
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self.stack.pop()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Handle Enter/Space key
                if self.selected == 2:  # Back option
                    self.stack.pop()
                # For volume options, Enter/Space could also adjust volume
                elif self.selected < 2:
                    self._adjust_volume(0.1)  # Increase volume on Enter/Space
    
    def _adjust_volume(self, delta):
        """Adjust selected volume"""
        if not self.audio:
            return
        
        if self.selected == 0:  # Music
            new_vol = self.audio.get_music_volume() + delta
            self.audio.set_music_volume(new_vol)
        elif self.selected == 1:  # SFX
            new_vol = self.audio.get_sfx_volume() + delta
            self.audio.set_sfx_volume(new_vol)
    
    def draw(self, screen):
        """Draw options menu"""
        screen.fill(settings.COLOR_BLACK)
        
        # Title
        title = self.font.render("OPTIONS", True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=100)
        screen.blit(title, title_rect)
        
        # Volume controls
        y = 250
        labels = ["Music Volume", "SFX Volume", "Back"]
        
        for i, label in enumerate(labels):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.font.render(label, True, color)
            rect = text.get_rect(x=200, y=y + i * 80)
            screen.blit(text, rect)
            
            # Draw volume bar
            if i < 2 and self.audio:
                vol = self.audio.get_music_volume() if i == 0 else self.audio.get_sfx_volume()
                bar_x = 600
                bar_y = rect.centery - 10
                bar_width = 300
                bar_height = 20
                
                # Background
                pygame.draw.rect(screen, settings.COLOR_DARK_GRAY, 
                               (bar_x, bar_y, bar_width, bar_height))
                # Fill
                fill_width = int(bar_width * vol)
                pygame.draw.rect(screen, settings.COLOR_GREEN,
                               (bar_x, bar_y, fill_width, bar_height))
                # Border
                pygame.draw.rect(screen, settings.COLOR_WHITE,
                               (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Percentage
                pct_text = f"{int(vol * 100)}%"
                pct_surf = self.font.render(pct_text, True, settings.COLOR_WHITE)
                screen.blit(pct_surf, (bar_x + bar_width + 20, bar_y - 5))
        
        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst = inst_font.render("Arrow Keys: Navigate/Adjust | Enter/Space: Select | ESC: Back", True, settings.COLOR_GRAY)
        inst_rect = inst.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 50)
        screen.blit(inst, inst_rect)
