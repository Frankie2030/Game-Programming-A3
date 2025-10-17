"""
Input handling and action mapping
"""
import pygame


class InputHandler:
    """Maps keyboard input to game actions"""
    
    def __init__(self):
        # Action states
        self.actions = {
            'left': False,
            'right': False,
            'jump': False,
            'jump_pressed': False,  # True only on the frame pressed
            'action': False,
            'action_pressed': False,
            'attack': False,
            'attack_pressed': False,
            'pause': False,
            'pause_pressed': False,
            'confirm': False,
            'confirm_pressed': False,
            'back': False,
            'back_pressed': False,
            'debug': False,
            'debug_pressed': False,
        }
        
        # Key mappings
        self.key_map = {
            pygame.K_LEFT: 'left',
            pygame.K_a: 'left',
            pygame.K_RIGHT: 'right',
            pygame.K_d: 'right',
            pygame.K_w: 'jump',
            pygame.K_UP: 'jump',
            # Additional jump keys to avoid rollover issues
            pygame.K_k: 'jump',
            pygame.K_z: 'jump',
            pygame.K_e: 'action',
            pygame.K_LSHIFT: 'action',
            pygame.K_RSHIFT: 'action',
            # Multiple attack keys so firing is independent from jump
            pygame.K_SPACE: 'attack',
            pygame.K_j: 'attack',
            pygame.K_x: 'attack',
            pygame.K_LCTRL: 'attack',
            pygame.K_RCTRL: 'attack',
            pygame.K_ESCAPE: 'pause',
            pygame.K_p: 'pause',
            pygame.K_RETURN: 'confirm',
            pygame.K_BACKSPACE: 'back',
            pygame.K_b: 'debug',
        }
    
    def update(self, events):
        """Update action states based on events"""
        # Reset pressed states
        self.actions['jump_pressed'] = False
        self.actions['action_pressed'] = False
        self.actions['attack_pressed'] = False
        self.actions['pause_pressed'] = False
        self.actions['confirm_pressed'] = False
        self.actions['back_pressed'] = False
        self.actions['debug_pressed'] = False
        
        # Handle events
        for event in events:
            if event.type == pygame.KEYDOWN:
                action = self.key_map.get(event.key)
                if action:
                    self.actions[action] = True
                    # Set pressed flag for single-frame actions
                    if action == 'jump':
                        self.actions['jump_pressed'] = True
                    elif action == 'action':
                        self.actions['action_pressed'] = True
                    elif action == 'attack':
                        self.actions['attack_pressed'] = True
                    elif action == 'pause':
                        self.actions['pause_pressed'] = True
                    elif action == 'confirm':
                        self.actions['confirm_pressed'] = True
                    elif action == 'back':
                        self.actions['back_pressed'] = True
                    elif action == 'debug':
                        self.actions['debug_pressed'] = True
            
            elif event.type == pygame.KEYUP:
                action = self.key_map.get(event.key)
                if action:
                    self.actions[action] = False
            
            # Support mouse left button to attack
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.actions['attack'] = True
                    self.actions['attack_pressed'] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.actions['attack'] = False
    
    def is_action_active(self, action):
        """Check if action is currently active (held)"""
        return self.actions.get(action, False)
    
    def is_action_pressed(self, action):
        """Check if action was just pressed this frame"""
        return self.actions.get(f'{action}_pressed', False)
    
    def get_horizontal_input(self):
        """Get horizontal movement direction (-1, 0, 1)"""
        direction = 0
        if self.actions['left']:
            direction -= 1
        if self.actions['right']:
            direction += 1
        return direction
    
    def reset_movement_inputs(self):
        """Reset all movement-related inputs (for respawn/state changes)"""
        self.actions['left'] = False
        self.actions['right'] = False
        self.actions['jump'] = False
        self.actions['action'] = False
        self.actions['attack'] = False
