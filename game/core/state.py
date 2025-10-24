"""
Game state management system
"""
import pygame

class GameState:
    """Base class for all game states"""
    
    def __init__(self, stack):
        self.stack = stack
        self.screen = stack.screen
        self.persistent_data = stack.persistent_data
    
    def enter(self, previous_state=None):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass
    
    def update(self, dt, events):
        """Update state logic"""
        pass
    
    def draw(self, screen):
        """Render state"""
        pass
    
    def handle_event(self, event):
        """Handle individual pygame event"""
        # Handle mute toggle with 'M' key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            if 'audio' in self.persistent_data:
                audio_manager = self.persistent_data['audio']
                audio_manager.toggle_mute()


class StateStack:
    """Manages game state transitions"""
    
    def __init__(self, screen):
        self.screen = screen
        self.states = []
        self.persistent_data = {}
        self.transition = None
        self.pending_state_change = None
    
    def push(self, state_class, *args, **kwargs):
        """Push a new state onto the stack"""
        # Exit current state if exists
        if self.states:
            self.states[-1].exit()
        
        # Create and enter new state
        new_state = state_class(self, *args, **kwargs)
        previous = self.states[-1] if self.states else None
        new_state.enter(previous)
        self.states.append(new_state)
        return new_state
    
    def push_with_transition(self, state_class, *args, **kwargs):
        """Push a new state with fade transition"""
        from game.core.transition import FadeTransition
        self.transition = FadeTransition(duration=0.3)
        self.pending_state_change = ('push', state_class, args, kwargs)
    
    def pop(self):
        """Remove current state and return to previous"""
        if not self.states:
            return None
        
        # Exit current state
        current = self.states.pop()
        current.exit()
        
        # Re-enter previous state if it exists
        if self.states:
            self.states[-1].enter(current)
        
        return current
    
    def pop_with_transition(self):
        """Remove current state with fade transition"""
        from game.core.transition import FadeTransition
        self.transition = FadeTransition(duration=0.3)
        self.pending_state_change = ('pop', None, None, None)
    
    def replace(self, state_class, *args, **kwargs):
        """Replace current state with a new one"""
        if self.states:
            self.pop()
        return self.push(state_class, *args, **kwargs)
    
    def replace_with_transition(self, state_class, *args, **kwargs):
        """Replace current state with transition"""
        from game.core.transition import FadeTransition
        self.transition = FadeTransition(duration=0.3)
        self.pending_state_change = ('replace', state_class, args, kwargs)
    
    def clear_and_push_with_transition(self, state_class, *args, **kwargs):
        """Clear all states and push new state with transition"""
        from game.core.transition import FadeTransition
        self.transition = FadeTransition(duration=0.3)
        self.pending_state_change = ('clear_and_push', state_class, args, kwargs)
    
    def clear(self):
        """Remove all states"""
        while self.states:
            self.pop()
    
    def update(self, dt, events):
        """Update the current state"""
        # Update transition if active
        if self.transition:
            self.transition.update(dt)
            
            # Execute pending state change at halfway point (fully black)
            if self.transition.is_halfway() and self.pending_state_change:
                action, state_class, args, kwargs = self.pending_state_change
                self.pending_state_change = None
                
                if action == 'push':
                    self.push(state_class, *args, **kwargs)
                elif action == 'replace':
                    if self.states:
                        self.pop()
                    self.push(state_class, *args, **kwargs)
                elif action == 'pop':
                    self.pop()
                elif action == 'clear_and_push':
                    self.clear()
                    self.push(state_class, *args, **kwargs)
            
            # Clear transition when complete
            if self.transition.is_complete():
                self.transition = None
        
        # Update current state only if no transition is blocking
        if self.states and not self.transition:
            self.states[-1].update(dt, events)
    
    def draw(self, screen):
        """Draw the current state"""
        if self.states:
            self.states[-1].draw(screen)
        
        # Draw transition overlay on top
        if self.transition:
            self.transition.draw(screen)
    
    def handle_event(self, event):
        """Pass event to current state"""
        if self.states:
            self.states[-1].handle_event(event)
    
    def current_state(self):
        """Get current state"""
        return self.states[-1] if self.states else None
    
    def is_empty(self):
        """Check if stack is empty"""
        return len(self.states) == 0
