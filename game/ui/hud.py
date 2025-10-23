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
    
    def draw(self, screen, player, boss=None, show_fps=False, fps=0, show_hitboxes=False, clear_conditions=None, game_time=0.0, camera=None, minimap_entities=None):
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
        
        # Powerup invincibility timer
        if player.is_powerup_active():
            time_left = player.get_powerup_time_left()
            powerup_text = f"INVINCIBLE: {time_left:.1f}s"
            powerup_surf = self.font.render(powerup_text, True, settings.COLOR_GREEN)
            powerup_rect = powerup_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, top=50)
            
            # Pulsing background
            bg_rect = powerup_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 100, 0, 128), bg_rect)
            pygame.draw.rect(screen, settings.COLOR_GREEN, bg_rect, 2)
            
            screen.blit(powerup_surf, powerup_rect)
        
        # Boss HP bar
        if boss and boss.alive:
            boss.draw_hp_bar(screen)
        
        # FPS counter
        if show_fps:
            fps_text = f"FPS: {int(fps)}"
            fps_surf = self.small_font.render(fps_text, True, settings.COLOR_GREEN)
            screen.blit(fps_surf, (settings.SCREEN_WIDTH - 80, 10))
        
        # Minimap (top-right)
        if camera is not None:
            self._draw_minimap(screen, player, camera, minimap_entities)
        
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

    def _draw_minimap(self, screen, player, camera, minimap_entities=None):
        """Draw a simple top-right minimap showing world bounds, camera view and player."""
        # Minimap rect in screen space
        mm_w = settings.MINIMAP_WIDTH
        mm_h = settings.MINIMAP_HEIGHT
        margin = settings.MINIMAP_MARGIN
        pad = settings.MINIMAP_PADDING
        mm_rect = pygame.Rect(settings.SCREEN_WIDTH - mm_w - margin, margin, mm_w, mm_h)

        # Shadow
        shadow = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, settings.MINIMAP_SHADOW_COLOR, shadow.get_rect(), border_radius=settings.MINIMAP_BORDER_RADIUS)
        screen.blit(shadow, (mm_rect.x + 3, mm_rect.y + 3))
        
        # Background with rounded corners
        bg = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        pygame.draw.rect(bg, settings.MINIMAP_BG_COLOR, bg.get_rect(), border_radius=settings.MINIMAP_BORDER_RADIUS)
        screen.blit(bg, mm_rect.topleft)
        pygame.draw.rect(screen, settings.MINIMAP_BORDER_COLOR, mm_rect, 2, border_radius=settings.MINIMAP_BORDER_RADIUS)

        # Inner drawable area (after padding)
        inner_rect = pygame.Rect(mm_rect.x + pad, mm_rect.y + pad, mm_w - 2 * pad, mm_h - 2 * pad)

        # Optional subtle grid (quarters)
        grid_color = settings.MINIMAP_GRID_COLOR
        pygame.draw.line(screen, grid_color, (inner_rect.centerx, inner_rect.top), (inner_rect.centerx, inner_rect.bottom), 1)
        pygame.draw.line(screen, grid_color, (inner_rect.left, inner_rect.centery), (inner_rect.right, inner_rect.centery), 1)

        # Scale factors world->minimap (use inner area)
        scale_x = inner_rect.width / settings.WORLD_WIDTH
        scale_y = inner_rect.height / settings.WORLD_HEIGHT
        
        # Camera viewport rectangle mapped into minimap
        view_w = camera.screen_width * scale_x
        view_h = camera.screen_height * scale_y
        view_x = inner_rect.x + camera.x * scale_x
        view_y = inner_rect.y + camera.y * scale_y
        view_rect = pygame.Rect(int(view_x), int(view_y), int(view_w), int(view_h))
        pygame.draw.rect(screen, settings.MINIMAP_VIEWPORT_COLOR, view_rect, 2)
        
        # Player dot
        px = inner_rect.x + player.rect.centerx * scale_x
        py = inner_rect.y + player.rect.centery * scale_y
        pygame.draw.circle(screen, settings.MINIMAP_PLAYER_COLOR, (int(px), int(py)), 3)

        # Entities overlay (bullets, powerups, etc.)
        if minimap_entities:
            # Helper to plot rect-like objects
            def plot_rect(obj_rect, color, radius=2):
                cx = inner_rect.x + obj_rect.centerx * scale_x
                cy = inner_rect.y + obj_rect.centery * scale_y
                pygame.draw.circle(screen, color, (int(cx), int(cy)), radius)

            # Bullets
            for b in minimap_entities.get('bullets', []) or []:
                plot_rect(b.rect, (255, 255, 0), 2)
            
            # Coins
            for c in minimap_entities.get('coins', []) or []:
                if hasattr(c, 'collected') and c.collected:
                    continue
                plot_rect(c.rect, settings.COLOR_YELLOW, 2)

            # Stars (Flux Surge)
            for s in minimap_entities.get('stars', []) or []:
                if hasattr(s, 'collected') and s.collected:
                    continue
                plot_rect(s.rect, settings.COLOR_BLUE, 2)

            # Powerups
            for p in minimap_entities.get('powerups', []) or []:
                if hasattr(p, 'collected') and p.collected:
                    continue
                plot_rect(p.rect, settings.COLOR_GREEN, 2)

            # Storm items
            for st in minimap_entities.get('storms', []) or []:
                plot_rect(st.rect, (255, 100, 50), 2)

            # Enemies
            for e in minimap_entities.get('enemies', []) or []:
                if hasattr(e, 'alive') and not e.alive:
                    continue
                plot_rect(e.rect, settings.COLOR_RED, 2)
