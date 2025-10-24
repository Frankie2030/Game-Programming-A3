"""
Gravity Courier - Main entry point
"""
import pygame
import sys
from game.core import StateStack, settings
from game.ui.main_menu import MainMenuState
from game.io.audio import AudioManager


def main():
    """Main game loop"""
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create window
    # 1280x720
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    
    # Create clock
    clock = pygame.time.Clock()
    
    # Create state stack
    state_stack = StateStack(screen)
    
    # Initialize audio manager
    audio_manager = AudioManager()
    state_stack.persistent_data['audio'] = audio_manager
    
    # Load all audio assets
    audio_manager.load_all_audio()
    
    # Push initial state
    state_stack.push(MainMenuState)
    
    # Main loop
    running = True
    while running:
        # Get delta time
        dt = clock.tick(settings.FPS) / 1000.0  # Convert to seconds
        state_stack.persistent_data['fps'] = clock.get_fps()
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            else:
                state_stack.handle_event(event)
        
        # Check if state stack is empty
        if state_stack.is_empty():
            running = False
        
        # Update
        state_stack.update(dt, events)
        
        # Draw
        state_stack.draw(screen)
        
        # Flip display
        pygame.display.flip()
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
