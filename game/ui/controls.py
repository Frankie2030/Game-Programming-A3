"""
Controls/key remapping menu
"""
import pygame
from game.core import GameState, settings


class ControlsState(GameState):
    """Controls configuration menu for key remapping"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.selected = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Get current key bindings or use defaults
        self.key_bindings = stack.persistent_data.get('key_bindings', settings.DEFAULT_KEY_BINDINGS.copy())
        
        # State for key remapping
        self.waiting_for_key = False
        self.remapping_action = None
        
        # Control actions that can be remapped
        self.control_labels = {
            'move_left': 'Move Left',
            'move_right': 'Move Right',
            'move_up': 'Move Up/Jump',
            'float': 'Float/Action',
            'shoot': 'Shoot',
        }
        self.control_order = ['move_left', 'move_right', 'move_up', 'float', 'shoot']
        
        # Background
        self._time = 0.0
        self._bg = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self._rebuild_bg()
        
        self.option_rects = []
    
    def update(self, dt, events):
        """Update"""
        self._time += dt
        if int(self._time * 60) % 6 == 0:
            self._rebuild_bg()
    
    def handle_event(self, event):
        """Handle input"""
        if self.waiting_for_key:
            # Waiting for user to press a key to remap
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Cancel remapping
                    self.waiting_for_key = False
                    self.remapping_action = None
                else:
                    # Handling 1 key map to multiple actions issue
                    # Remove this key from all other actions first (prevent conflicts)
                    for action in self.control_order:
                        if action != self.remapping_action:
                            if event.key in self.key_bindings.get(action, []):
                                self.key_bindings[action].remove(event.key)
                    
                    # Assign new key (replace the first binding)
                    self.key_bindings[self.remapping_action] = [event.key]
                    self.waiting_for_key = False
                    self.remapping_action = None
                    # Save bindings
                    self.stack.persistent_data['key_bindings'] = self.key_bindings
                    # Update input handler if it exists
                    if 'input_handler' in self.stack.persistent_data:
                        self.stack.persistent_data['input_handler'].update_key_bindings(self.key_bindings)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected = max(0, self.selected - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected = min(len(self.control_order), self.selected + 1)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.stack.pop()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected < len(self.control_order):
                        # Start remapping
                        self.remapping_action = self.control_order[self.selected]
                        self.waiting_for_key = True
                    elif self.selected == len(self.control_order):
                        # Reset to defaults
                        self.key_bindings = settings.DEFAULT_KEY_BINDINGS.copy()
                        self.stack.persistent_data['key_bindings'] = self.key_bindings
                        if 'input_handler' in self.stack.persistent_data:
                            self.stack.persistent_data['input_handler'].update_key_bindings(self.key_bindings)
                    elif self.selected == len(self.control_order) + 1:
                        # Back
                        self.stack.pop()
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mx, my):
                        self.selected = i
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mx, my):
                        self.selected = i
                        if self.selected < len(self.control_order):
                            self.remapping_action = self.control_order[self.selected]
                            self.waiting_for_key = True
                        elif self.selected == len(self.control_order):
                            # Reset to defaults
                            self.key_bindings = settings.DEFAULT_KEY_BINDINGS.copy()
                            self.stack.persistent_data['key_bindings'] = self.key_bindings
                            if 'input_handler' in self.stack.persistent_data:
                                self.stack.persistent_data['input_handler'].update_key_bindings(self.key_bindings)
                        elif self.selected == len(self.control_order) + 1:
                            self.stack.pop()
                        break
    
    def _rebuild_bg(self):
        """Rebuild background"""
        cx, cy = settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2
        max_r = int((cx * cx + cy * cy) ** 0.5)
        base = 25
        self._bg.fill((0, 0, 0))
        for r in range(0, max_r, 8):
            t = r / max_r
            shade = base + int((1 - t) * 70)
            color = (shade // 4, shade // 3, shade)
            pygame.draw.circle(self._bg, color, (cx, cy), max_r - r)
    
    def draw(self, screen):
        """Draw controls menu"""
        screen.blit(self._bg, (0, 0))
        
        # Semi-transparent panel
        panel = pygame.Surface((settings.SCREEN_WIDTH - 200, settings.SCREEN_HEIGHT - 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        screen.blit(panel, (100, 75))
        
        # Title
        title = self.font.render("CONTROLS", True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=100)
        screen.blit(title, title_rect)
        
        # Instructions
        if self.waiting_for_key:
            inst_text = f"Press a key to bind to {self.control_labels[self.remapping_action]} (ESC to cancel)"
            inst = self.font.render(inst_text, True, settings.COLOR_GREEN)
            inst_rect = inst.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=180)
            screen.blit(inst, inst_rect)
        else:
            inst = self.small_font.render("Select an action and press Enter/Click to remap", True, settings.COLOR_GRAY)
            inst_rect = inst.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=170)
            screen.blit(inst, inst_rect)
        
        # Control list
        y = 230
        self.option_rects = []
        
        for i, action in enumerate(self.control_order):
            label = self.control_labels[action]
            keys = self.key_bindings.get(action, [])
            key_names = [pygame.key.name(k).upper() for k in keys] if keys else ["UNBOUND"]
            key_str = ", ".join(key_names[:3])  # Show first 3 keys
            
            color = settings.COLOR_YELLOW if i == self.selected else settings.COLOR_WHITE
            text = self.font.render(f"{label}:", True, color)
            rect = text.get_rect(x=200, y=y + i * 60)
            screen.blit(text, rect)
            
            # Show current key binding
            key_text = self.font.render(key_str, True, settings.COLOR_GREEN if i == self.selected else settings.COLOR_GRAY)
            key_rect = key_text.get_rect(x=600, y=y + i * 60)
            screen.blit(key_text, key_rect)
            
            # Store rect for mouse interaction (combine both text areas)
            combined_rect = rect.union(key_rect)
            self.option_rects.append(combined_rect)
        
        # Reset to defaults button
        y_reset = y + len(self.control_order) * 60 + 20
        reset_color = settings.COLOR_YELLOW if self.selected == len(self.control_order) else settings.COLOR_WHITE
        reset_text = self.font.render("Reset to Defaults", True, reset_color)
        reset_rect = reset_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y_reset)
        screen.blit(reset_text, reset_rect)
        self.option_rects.append(reset_rect)
        
        # Back button
        y_back = y_reset + 60
        back_color = settings.COLOR_YELLOW if self.selected == len(self.control_order) + 1 else settings.COLOR_WHITE
        back_text = self.font.render("Back", True, back_color)
        back_rect = back_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y_back)
        screen.blit(back_text, back_rect)
        self.option_rects.append(back_rect)
        
        # Bottom instructions
        bottom_inst = self.small_font.render("Arrows/WASD: Navigate   Enter/Click: Select   ESC: Back", True, settings.COLOR_GRAY)
        bottom_rect = bottom_inst.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 30)
        screen.blit(bottom_inst, bottom_rect)
