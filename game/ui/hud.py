"""
Heads-up display
"""
import pygame
from game.core import settings


class HUD:
    """Display player stats and game info"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
    
    def draw(self, screen, player, boss=None, show_fps=False, fps=0, show_hitboxes=False, clear_conditions=None, game_time=0.0):
        """Draw HUD elements"""
        # HP/Lives
        hp_text = f"HP: {player.hp}/{settings.PLAYER_HP}"
        hp_surf = self.font.render(hp_text, True, settings.COLOR_WHITE)
        screen.blit(hp_surf, (10, 10))
        
        # Coins
        coin_text = f"Coins: {player.coins}"
        coin_surf = self.font.render(coin_text, True, settings.COLOR_YELLOW)
        screen.blit(coin_surf, (10, 40))
        
        # Clear conditions progress
        if clear_conditions:
            # Enemy progress
            defeated, total = clear_conditions.get_enemies_progress()
            enemy_text = f"Enemies: {defeated}/{total}"
            enemy_color = settings.COLOR_GREEN if defeated >= total else settings.COLOR_WHITE
            enemy_surf = self.font.render(enemy_text, True, enemy_color)
            screen.blit(enemy_surf, (10, 70))
            
            # Timer (show in red if over 2 minutes for 3-star warning)
            time_text = f"Time: {game_time:.1f}s"
            time_color = settings.COLOR_RED if game_time > settings.TIME_LIMIT_3_STAR else settings.COLOR_WHITE
            time_surf = self.font.render(time_text, True, time_color)
            screen.blit(time_surf, (10, 100))
        
        # Flux Surge timer
        if player.is_flux_surge_active():
            time_left = player.get_flux_surge_time_left()
            star_text = f"FLUX SURGE: {time_left:.1f}s"
            star_surf = self.font.render(star_text, True, settings.COLOR_YELLOW)
            star_rect = star_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, top=10)
            
            # Pulsing background
            bg_rect = star_rect.inflate(20, 10)
            pygame.draw.rect(screen, (100, 100, 0, 128), bg_rect)
            pygame.draw.rect(screen, settings.COLOR_YELLOW, bg_rect, 2)
            
            screen.blit(star_surf, star_rect)
        
        # Boss HP bar
        if boss and boss.alive:
            boss.draw_hp_bar(screen)
        
        # FPS counter
        if show_fps:
            fps_text = f"FPS: {int(fps)}"
            fps_surf = self.small_font.render(fps_text, True, settings.COLOR_GREEN)
            screen.blit(fps_surf, (settings.SCREEN_WIDTH - 80, 10))
        
        # Controls hint
        hint_text = "Arrow/WASD: Move | Space/W: Jump | E/Shift: Flip Gravity | B: Debug | ESC: Pause"
        hint_surf = self.small_font.render(hint_text, True, settings.COLOR_GRAY)
        hint_rect = hint_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, 
                                        bottom=settings.SCREEN_HEIGHT - 5)
        screen.blit(hint_surf, hint_rect)
        
        # Debug mode indicator
        if show_hitboxes:
            debug_text = "DEBUG MODE: Hitboxes ON"
            debug_surf = self.font.render(debug_text, True, (255, 0, 255))
            screen.blit(debug_surf, (10, 130))
