"""
Win screen
"""
import pygame
from game.core import GameState, settings


class WinState(GameState):
    """Victory screen"""
    
    def __init__(self, stack, coins=0, time=0, clear_conditions=None):
        super().__init__(stack)
        self.coins = coins
        self.time = time
        self.clear_conditions = clear_conditions
        self.stars = clear_conditions.get_star_rating() if clear_conditions else 1
        self.font = pygame.font.Font(None, 72)
        self.text_font = pygame.font.Font(None, 36)
        self.star_font = pygame.font.Font(None, 48)
    
    def handle_event(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                from game.ui.main_menu import MainMenuState
                self.stack.clear()
                self.stack.push(MainMenuState)
    
    def draw(self, screen):
        """Draw win screen"""
        screen.fill(settings.COLOR_BLACK)
        
        # Victory text
        title = self.font.render("MISSION COMPLETE!", True, settings.COLOR_GREEN)
        title_rect = title.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=120)
        screen.blit(title, title_rect)
        
        # Star rating
        star_text = "★" * self.stars + "☆" * (3 - self.stars)
        star_surf = self.star_font.render(star_text, True, settings.COLOR_YELLOW)
        star_rect = star_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=180)
        screen.blit(star_surf, star_rect)
        
        # Stats
        y = 250
        
        # Build stats based on clear conditions
        stats = [
            f"Data Canisters Delivered: {self.coins}",
            f"Completion Time: {self.time:.1f}s",
            ""
        ]
        
        if self.clear_conditions:
            defeated, total = self.clear_conditions.get_enemies_progress()
            stats.extend([
                "CLEAR CONDITIONS:",
                f"🌟 Defeat Boss: {'✅' if self.clear_conditions.boss_defeated else '❌'}",
                f"🌟 Defeat All Enemies ({defeated}/{total}): {'✅' if defeated >= total else '❌'}",
                f"🌟 Complete in {settings.TIME_LIMIT_3_STAR}s: {'✅' if self.time <= settings.TIME_LIMIT_3_STAR else '❌'}",
                ""
            ])
        
        stats.extend([
            "The station is secure.",
            "",
            "Press ENTER to continue"
        ])
        
        for line in stats:
            color = settings.COLOR_YELLOW if ":" in line else settings.COLOR_WHITE
            text = self.text_font.render(line, True, color)
            rect = text.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=y)
            screen.blit(text, rect)
            y += 50
