"""
Boss: Gyro-Core with pattern phases
"""
import pygame
from game.core import settings, Timer
from game.entities.spikes import AnimatedSpike
import math
import random


class GyroBoss:
    """Gyro-Core boss with phased pattern"""
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 96, 96)
        self.hp = settings.BOSS_HP
        self.max_hp = settings.BOSS_HP
        self.alive = True
        self.defeated = False
        
        # Phase system
        self.phase = 'spin_up'  # 'spin_up', 'hazard', 'recalibration'
        self.phase_timer = Timer()
        self.pattern_timer = Timer()
        self.pattern_timer.start(settings.BOSS_PATTERN_DURATION)
        
        # Visual
        self.rotation = 0
        self.flash_timer = 0
        self.vulnerable = False
        
        # Hazard beams (simple rotating lines)
        self.beam_rotation = 0
        self.beam_speed = 120  # degrees/second
        
        # Spike attack system
        self.animated_spikes = []  # List of active animated spikes
        self.spike_attack_timer = 0
        self.spike_attack_cooldown = 3.0  # Spawn spike wave every 3 seconds
        self.arena_bounds = None  # Will be set by level
    
    def set_arena_bounds(self, floor_y, ceiling_y, left_x, right_x):
        """Set arena boundaries for spike spawning"""
        self.arena_bounds = {
            'floor_y': floor_y,
            'ceiling_y': ceiling_y,
            'left_x': left_x,
            'right_x': right_x
        }
    
    def spawn_spike_wave(self):
        """Spawn a wave of animated spikes"""
        if not self.arena_bounds:
            return
        
        # Spawn random spikes from floor or ceiling
        # if boss hp < 50% increase number of spikes
        if self.hp < self.max_hp / 2:
            num_spikes = random.randint(30, 40)
        else:
            num_spikes = random.randint(20, 30)

        for _ in range(num_spikes):
            # Random position across arena width
            x = random.randint(self.arena_bounds['left_x'], self.arena_bounds['right_x'] - settings.TILE_SIZE)
            
            # Randomly choose floor or ceiling
            if random.choice([True, False]):
                # Spawn from floor (growing up)
                y = self.arena_bounds['floor_y']
                orientation = 'up'
            else:
                # Spawn from ceiling (growing down)
                y = self.arena_bounds['ceiling_y']
                orientation = 'down'
            
            spike = AnimatedSpike(x, y, orientation=orientation, telegraph_time=1.0, grow_time=0.5, active_time=1.0, retract_time=0.5)
            self.animated_spikes.append(spike)
    
    def update(self, dt):
        """Update boss logic"""
        if not self.alive:
            return
        
        self.flash_timer -= dt
        self.rotation += dt * 45
        
        # Update pattern timer
        pattern_expired = self.pattern_timer.update(dt)
        if pattern_expired:
            # Restart pattern
            self.pattern_timer.start(settings.BOSS_PATTERN_DURATION)
            self.phase = 'spin_up'
            self.phase_timer.stop()
        
        # Phase management
        elapsed = settings.BOSS_PATTERN_DURATION - self.pattern_timer.time_left
        
        if elapsed < settings.BOSS_TELEGRAPH_TIME:
            self.phase = 'spin_up'
            self.vulnerable = False
        elif elapsed < settings.BOSS_PATTERN_DURATION - settings.BOSS_WEAK_WINDOW:
            self.phase = 'hazard'
            self.vulnerable = False
            # Rotate beams during hazard phase
            self.beam_rotation += self.beam_speed * dt
            
            # Spike attack system - spawn waves during hazard phase
            self.spike_attack_timer += dt
            if self.spike_attack_timer >= self.spike_attack_cooldown:
                self.spawn_spike_wave()
                self.spike_attack_timer = 0
        else:
            self.phase = 'recalibration'
            self.vulnerable = True
        
        # Update all animated spikes
        for spike in self.animated_spikes[:]:
            spike.update(dt)
            if spike.is_done():
                self.animated_spikes.remove(spike)
    
    def take_damage(self, amount=1):
        """Take damage during vulnerable phase"""
        if not self.vulnerable or not self.alive:
            return False
        
        self.hp -= amount
        self.flash_timer = 0.2
        
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.defeated = True
        
        return True
    
    def check_hit_player(self, player_rect, player_invuln, player_gravity_dir):
        """Check if hazards hit player"""
        if player_invuln:
            return False
        
        # Check animated spikes
        for spike in self.animated_spikes:
            if spike.check_collision(player_rect, player_gravity_dir):
                return True
        
        # Check laser beams during hazard phase
        if self.phase != 'hazard':
            return False
        
        # Check if player intersects with rotating laser beams
        # Calculate beam lines and check collision
        boss_center = self.rect.center
        player_center = player_rect.center
        
        for i in range(2):
            angle = math.radians(self.beam_rotation + i * 180)
            # Beam extends 200 pixels from boss center
            beam_end_x = boss_center[0] + math.cos(angle) * 200
            beam_end_y = boss_center[1] + math.sin(angle) * 200
            
            # Check distance from player to beam line
            dist = self._point_to_line_distance(
                player_center[0], player_center[1],
                boss_center[0], boss_center[1],
                beam_end_x, beam_end_y
            )
            
            # Beam width is ~6 pixels, player hitbox is ~12 pixels radius
            if dist < 18:  # Hit!
                return True
        
        return False
    
    def _point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        # Calculate line length
        line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_len == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Calculate perpendicular distance
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len * line_len)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    def draw(self, screen, camera):
        """Draw boss"""
        if not self.alive and self.flash_timer <= 0:
            return
        
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        center = draw_rect.center
        
        # Choose color based on phase
        if self.flash_timer > 0:
            core_color = settings.COLOR_WHITE
        elif self.phase == 'recalibration':
            core_color = settings.COLOR_YELLOW  # Vulnerable
        elif self.phase == 'hazard':
            core_color = settings.COLOR_RED
        else:
            core_color = settings.COLOR_GRAY
        
        # Draw outer shell
        pygame.draw.circle(screen, settings.COLOR_DARK_GRAY, center, 48)
        pygame.draw.circle(screen, settings.COLOR_BLACK, center, 48, 3)
        
        # Draw rotating segments
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            x1 = center[0] + math.cos(angle) * 30
            y1 = center[1] + math.sin(angle) * 30
            x2 = center[0] + math.cos(angle) * 48
            y2 = center[1] + math.sin(angle) * 48
            pygame.draw.line(screen, settings.COLOR_BLACK, (x1, y1), (x2, y2), 4)
        
        # Draw core
        pygame.draw.circle(screen, core_color, center, 24)
        pygame.draw.circle(screen, settings.COLOR_BLACK, center, 24, 2)
        
        # Draw hazard beams during hazard phase
        if self.phase == 'hazard':
            for i in range(2):
                angle = math.radians(self.beam_rotation + i * 180)
                x1 = center[0] + math.cos(angle) * 48
                y1 = center[1] + math.sin(angle) * 48
                x2 = center[0] + math.cos(angle) * 200
                y2 = center[1] + math.sin(angle) * 200
                pygame.draw.line(screen, (255, 100, 100), (x1, y1), (x2, y2), 6)
                pygame.draw.line(screen, settings.COLOR_RED, (x1, y1), (x2, y2), 3)
        
        # Draw animated spikes
        for spike in self.animated_spikes:
            spike.draw(screen, camera)
    
    def draw_hp_bar(self, screen):
        """Draw boss HP bar at top of screen"""
        if not self.alive:
            return
        
        bar_width = 400
        bar_height = 20
        bar_x = (settings.SCREEN_WIDTH - bar_width) // 2
        bar_y = 20
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, settings.COLOR_DARK_GRAY, bg_rect)
        pygame.draw.rect(screen, settings.COLOR_BLACK, bg_rect, 2)
        
        # HP fill
        hp_ratio = self.hp / self.max_hp
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            # Color changes based on HP
            if hp_ratio > 0.5:
                color = settings.COLOR_GREEN
            elif hp_ratio > 0.25:
                color = settings.COLOR_YELLOW
            else:
                color = settings.COLOR_RED
            pygame.draw.rect(screen, color, fill_rect)
        
        # Boss name
        font = pygame.font.Font(None, 24)
        name_text = font.render("GYRO-CORE", True, settings.COLOR_WHITE)
        name_rect = name_text.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=bar_y - 5)
        screen.blit(name_text, name_rect)
