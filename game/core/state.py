"""
Game state management system
"""


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
        pass


class StateStack:
    """Manages game state transitions"""
    
    def __init__(self, screen):
        self.screen = screen
        self.states = []
        self.persistent_data = {}
    
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
    
    def replace(self, state_class, *args, **kwargs):
        """Replace current state with a new one"""
        if self.states:
            self.pop()
        return self.push(state_class, *args, **kwargs)
    
    def clear(self):
        """Remove all states"""
        while self.states:
            self.pop()
    
    def update(self, dt, events):
        """Update the current state"""
        if self.states:
            self.states[-1].update(dt, events)
    
    def draw(self, screen):
        """Draw the current state"""
        if self.states:
            self.states[-1].draw(screen)
    
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
