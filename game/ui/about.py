"""
About/Credits screen
"""
import pygame
from game.core import GameState, settings


class AboutState(GameState):
    """About screen"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE or event.key == pygame.K_RETURN:
                self.stack.pop()
    
    def draw(self, screen):
        """Draw about screen"""
        screen.fill(settings.COLOR_BLACK)
        
        # Title
        title = self.font.render("ABOUT GRAVITY COURIER", True, settings.COLOR_YELLOW)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=80)
        screen.blit(title, title_rect)
        
        # Info
        info = [
            "",
            "You're a bike courier inside a rotating space station.",
            "Deliver data canisters and reach the terminal.",
            "",
            "Your power: flip gravity at will.",
            "",
            "CONTROLS:",
            "Arrow Keys / WASD - Move",
            "Space / W / Up - Jump",
            "E / Shift - Flip Gravity",
            "ESC - Pause",
            "",
            "GAMEPLAY:",
            "- Collect coins (data canisters)",
            "- Flip gravity to navigate ceiling and floor",
            "- Stomp enemies from opposite gravity",
            "- Break crates and panels from correct side",
            "- Grab Flux Surge (star) for invincibility",
            "- Defeat Gyro-Core boss to win",
            "",
            "",
            "Press ESC or ENTER to return"
        ]
        
        y = 180
        for line in info:
            if line.startswith("CONTROLS") or line.startswith("GAMEPLAY"):
                color = settings.COLOR_YELLOW
            else:
                color = settings.COLOR_WHITE
            
            text = self.small_font.render(line, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y)
            screen.blit(text, rect)
            y += 25
