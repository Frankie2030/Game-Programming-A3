"""
How to Play screen
"""
import pygame
from game.core import GameState, settings


class HowToPlayState(GameState):
    """How to Play screen with controls and powerup explanations"""
    
    def __init__(self, stack):
        super().__init__(stack)
        self.title_font = pygame.font.Font(None, 56)
        self.section_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Scrolling support
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Load star sprite sheet frames for animation
        self.star_frames = []
        self.star_current_frame = 0
        self.star_animation_time = 0
        self.star_frame_duration = 0.08
        
        try:
            sprite_path = 'game/assets/images/sprites/Star.png'
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
            
            # Extract frames from sprite sheet
            sheet_width = sprite_sheet.get_width()
            sheet_height = sprite_sheet.get_height()
            frame_width = sheet_height  # Assuming frames are square
            num_frames = sheet_width // frame_width
            
            for i in range(num_frames):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
                frame = sprite_sheet.subsurface(frame_rect).copy()
                frame_scaled = pygame.transform.scale(frame, (20, 20))
                self.star_frames.append(frame_scaled)
        except:
            pass  # Will draw manually if sprite fails to load
        
    def handle_event(self, event):
        """Handle input"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self.stack.pop()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.scroll_offset = min(self.scroll_offset + 20, self.max_scroll)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.scroll_offset = max(self.scroll_offset - 20, 0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                self.scroll_offset = max(self.scroll_offset - 30, 0)
            elif event.button == 5:  # Mouse wheel down
                self.scroll_offset = min(self.scroll_offset + 30, self.max_scroll)
    
    def update(self, dt, events):
        """Update star animation"""
        if len(self.star_frames) > 0:
            self.star_animation_time += dt
            if self.star_animation_time >= self.star_frame_duration:
                self.star_animation_time = 0
                self.star_current_frame = (self.star_current_frame + 1) % len(self.star_frames)
    
    def draw(self, screen):
        """Draw how to play screen"""
        screen.fill(settings.COLOR_BLACK)
        
        # Create a scrollable surface
        y = 30 - self.scroll_offset
        margin_x = 80
        
        # Title
        title = self.title_font.render("HOW TO PLAY", True, settings.COLOR_YELLOW)
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, y))
        y += 80
        
        # === YOUR MISSION ===
        section = self.section_font.render("Your Mission", True, settings.COLOR_WHITE)
        screen.blit(section, (margin_x, y))
        y += 50
        
        mission_text = [
            "You are a Gravity Courier delivering data across hazardous zones.",
            "Navigate through levels using gravity manipulation to survive and complete objectives."
        ]
        for line in mission_text:
            text = self.text_font.render(line, True, settings.COLOR_GRAY)
            screen.blit(text, (margin_x + 20, y))
            y += 35
        
        y += 20
        
        # === CONTROLS ===
        section = self.section_font.render("Controls", True, settings.COLOR_WHITE)
        screen.blit(section, (margin_x, y))
        y += 50
        
        controls = [
            ("A / D or Arrow Keys", "Move left / right"),
            ("W or Up", "Jump (buffers input, works with coyote time)"),
            ("E", "Flip gravity (cooldown: 0.25s)"),
            ("Space", "Attack (shoot bullets)"),
            ("ESC", "Pause / Back to menu"),
            ("M", "Mute / Unmute audio")
        ]
        
        for key, desc in controls:
            key_text = self.text_font.render(key, True, settings.COLOR_YELLOW)
            desc_text = self.text_font.render(f"- {desc}", True, settings.COLOR_GRAY)
            screen.blit(key_text, (margin_x + 20, y))
            screen.blit(desc_text, (margin_x + 280, y))
            y += 35
        
        y += 20
        
        # === MECHANICS ===
        section = self.section_font.render("Mechanics", True, settings.COLOR_WHITE)
        screen.blit(section, (margin_x, y))
        y += 50
        
        mechanics = [
            ("Stamina System", "Drains while airborne. Regens on ground."),
            ("", "If depleted, gravity flip is locked until fully recharged."),
            ("Health Points", "Start with 5 HP. Lose HP from enemies and hazards."),
            ("I-Frame", "Temporary protection after taking damage."),
            ("Checkpoints", "Progress is saved when respawning.")
        ]
        
        for name, desc in mechanics:
            if name:
                name_text = self.text_font.render(name, True, settings.COLOR_YELLOW)
                screen.blit(name_text, (margin_x + 20, y))
                y += 30
            desc_text = self.small_font.render(desc, True, settings.COLOR_GRAY)
            screen.blit(desc_text, (margin_x + 40, y))
            y += 28
        
        y += 20
        
        # === COLLECTIBLES ===
        section = self.section_font.render("Collectibles & Powerups", True, settings.COLOR_WHITE)
        screen.blit(section, (margin_x, y))
        y += 50
        
        collectibles = [
            ("Coin (Gold)", "Collect for score and objectives."),
            ("Star (Yellow star)", "Invincibility (15s) + instantly kill enemies on contact."),
            ("", "Does NOT work on bosses - use bullets against bosses."),
            ("Powerup (P icon)", "Permanent double shot - fire 2 bullets at once."),
            ("Storm (Energy)", "Permanent upgrade: 2x stamina capacity + 2x regen rate.")
        ]
        
        for name, desc in collectibles:
            if name:
                # Draw colored box representing the item
                if "Coin" in name:
                    pygame.draw.circle(screen, settings.COLOR_YELLOW, (margin_x + 30, y + 10), 8)
                elif "Star" in name:
                    # Draw animated star sprite or fallback
                    if len(self.star_frames) > 0:
                        frame = self.star_frames[self.star_current_frame]
                        star_rect = frame.get_rect(center=(margin_x + 30, y + 10))
                        screen.blit(frame, star_rect)
                    else:
                        # Fallback: Draw a star shape
                        import math
                        star_points = []
                        center_x, center_y = margin_x + 30, y + 10
                        outer_radius = 10
                        inner_radius = 4
                        for i in range(10):
                            angle = (i * 36 - 90) * math.pi / 180
                            radius = outer_radius if i % 2 == 0 else inner_radius
                            px = center_x + radius * math.cos(angle)
                            py = center_y + radius * math.sin(angle)
                            star_points.append((px, py))
                        pygame.draw.polygon(screen, settings.COLOR_YELLOW, star_points)
                elif "Powerup" in name:
                    pygame.draw.rect(screen, (255, 200, 0), (margin_x + 22, y + 2, 16, 16))
                    p_text = self.small_font.render("P", True, settings.COLOR_BLACK)
                    screen.blit(p_text, (margin_x + 26, y + 3))
                elif "Storm" in name:
                    # Draw energy icon representation
                    pygame.draw.circle(screen, (100, 200, 255), (margin_x + 30, y + 10), 9)
                    pygame.draw.circle(screen, (200, 230, 255), (margin_x + 30, y + 10), 5)
                
                name_text = self.text_font.render(name, True, settings.COLOR_YELLOW)
                screen.blit(name_text, (margin_x + 50, y))
                y += 30
            
            desc_text = self.small_font.render(desc, True, settings.COLOR_GRAY)
            screen.blit(desc_text, (margin_x + 70, y))
            y += 28
        
        y += 20
        
        # === ENEMIES & HAZARDS ===
        section = self.section_font.render("Enemies & Hazards", True, settings.COLOR_WHITE)
        screen.blit(section, (margin_x, y))
        y += 50
        
        hazards = [
            ("Spikes", "Instant damage on contact. Watch for orientation."),
            ("Enemies", "Patrol zones. Defeat with bullets or stomps."),
            ("Breakable Blocks", "Break them to reveal coins or powerups."),
            ("Buttons & Gates", "Activate buttons to open gates.")
        ]
        
        for name, desc in hazards:
            name_text = self.text_font.render(name, True, settings.COLOR_RED)
            screen.blit(name_text, (margin_x + 20, y))
            y += 30
            desc_text = self.small_font.render(desc, True, settings.COLOR_GRAY)
            screen.blit(desc_text, (margin_x + 40, y))
            y += 35
        
        y += 30
        
        # Update max scroll
        self.max_scroll = max(0, y - settings.SCREEN_HEIGHT + 1000)
        
        # Footer hint
        footer = self.small_font.render("ESC: Back   W/S or Scroll: Navigate", True, settings.COLOR_WHITE)
        screen.blit(footer, (20, settings.SCREEN_HEIGHT - 34))
        
        # Scroll indicator
        if self.max_scroll > 0:
            scroll_pct = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            indicator_height = 60
            indicator_y = 100 + scroll_pct * (settings.SCREEN_HEIGHT - 200)
            pygame.draw.rect(screen, settings.COLOR_GRAY, (settings.SCREEN_WIDTH - 30, indicator_y, 10, indicator_height), border_radius=5)
