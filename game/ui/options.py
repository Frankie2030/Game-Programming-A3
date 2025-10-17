"""
Options menu
"""
import math
import pygame
from game.core import GameState, settings


class OptionsState(GameState):
    """Options/settings menu"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.selected = 0
        self.font = pygame.font.Font(None, 36)
        self.audio = stack.persistent_data.get('audio')
        
        # Distinct animated background
        self._time = 0.0
        self._bg = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self._rebuild_bg()
        
        # Mouse navigation/interaction
        self.mouse_enabled = True
        self.option_rects = []
        self.slider_rects = []
    
    def update(self, dt, events):
        """Update"""
        self._time += dt
        if int(self._time * 60) % 6 == 0:
            self._rebuild_bg(pulse=True)
    
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
        elif event.type == pygame.MOUSEMOTION and self.mouse_enabled:
            mx, my = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mx, my):
                    self.selected = i
                    break
        elif event.type == pygame.MOUSEWHEEL and self.mouse_enabled:
            if self.selected in (0, 1):
                self._adjust_volume(event.y * 0.05)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.selected == 2 and len(self.option_rects) > 2 and self.option_rects[2].collidepoint(mx, my):
                self.stack.pop()
            for i in (0, 1):
                if i < len(self.slider_rects) and self.slider_rects[i].collidepoint(mx, my):
                    self.selected = i
                    self._set_volume_by_mouse(i, mx)
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            mx, _ = event.pos
            if self.selected in (0, 1):
                self._set_volume_by_mouse(self.selected, mx)
    
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
    
    def _set_volume_by_mouse(self, idx, mouse_x):
        if not self.audio or idx >= len(self.slider_rects):
            return
        bar = self.slider_rects[idx]
        ratio = (mouse_x - bar.x) / max(1, bar.width)
        ratio = max(0.0, min(1.0, ratio))
        if idx == 0:
            self.audio.set_music_volume(ratio)
        else:
            self.audio.set_sfx_volume(ratio)
    
    def _rebuild_bg(self, pulse=False):
        """Rebuild subtle animated radial gradient background."""
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        max_r = int((cx * cx + cy * cy) ** 0.5)
        base = 30
        self._bg.fill((0, 0, 0))
        for r in range(0, max_r, 8):
            t = r / max_r
            amp = 12 if pulse else 0
            shade = base + int((1 - t) * 80) + int(math.sin(self._time * 2 + t * 8) * amp)
            color = (shade // 3, shade // 2, shade)
            pygame.draw.circle(self._bg, color, (cx, cy), max_r - r)
    
    def draw(self, screen):
        """Draw options menu"""
        screen.blit(self._bg, (0, 0))
        panel = pygame.Surface((settings.SCREEN_WIDTH - 200, settings.SCREEN_HEIGHT - 200), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 130))
        screen.blit(panel, (100, 100))
        
        # Title
        title = self.font.render("OPTIONS", True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=120)
        screen.blit(title, title_rect)
        
        # Volume controls
        y = 260
        labels = ["Music Volume", "SFX Volume", "Back"]
        
        self.option_rects = []
        self.slider_rects = []
        for i, label in enumerate(labels):
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.font.render(label, True, color)
            rect = text.get_rect(x=200, y=y + i * 80)
            screen.blit(text, rect)
            self.option_rects.append(rect)
            
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
                # Knob
                knob_x = bar_x + fill_width
                pygame.draw.circle(screen, settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE,
                                   (knob_x, bar_y + bar_height // 2), 10)
                self.slider_rects.append(pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            else:
                self.slider_rects.append(pygame.Rect(0, 0, 0, 0))
                
                # Percentage
                pct_text = f"{int(vol * 100)}%"
                pct_surf = self.font.render(pct_text, True, settings.COLOR_WHITE)
                screen.blit(pct_surf, (bar_x + bar_width + 20, bar_y - 5))
        
        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst = inst_font.render("Enter/Click: Select   Arrows/WASD or Wheel: Adjust   ESC: Back", True, settings.COLOR_GRAY)
        inst_rect = inst.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 50)
        screen.blit(inst, inst_rect)
