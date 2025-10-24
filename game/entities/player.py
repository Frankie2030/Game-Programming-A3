"""
Player character with gravity-flip mechanics
"""
import pygame
from game.core import settings, Timer, clamp, sign

def crop_surface(surface):
    """Crop a surface to its non-transparent bounding box."""
    rect = surface.get_bounding_rect()  # tight bounding box of non-transparent pixels
    return surface.subsurface(rect).copy()


class Player:
    """Player character with gravity control"""
    
    def __init__(self, x, y, audio=None):
        self.rect = pygame.Rect(x, y, 24, 32)
        self.audio = audio
        self.vel_x = 0
        self.vel_y = 0
        
        # Gravity state
        self.gravity_dir = 1  # +1 = down, -1 = up
        self.flip_cooldown = Timer()
        
        # Jump state
        self.on_ground = False
        self.coyote_timer = Timer(settings.COYOTE_TIME)
        self.jump_buffer = Timer(settings.JUMP_BUFFER_TIME)
        
        # Health and power-ups
        self.hp = settings.PLAYER_HP
        self.invuln_timer = Timer()
        self.flux_surge_timer = Timer()  # Star: invincibility + instant kill enemies
        self.double_shot = False  # P powerup: permanent double shot
        self.stamina_boost = False  # Storm powerup: permanent 2x stamina + 2x regen
        
        # Stamina system
        self.max_stamina = 1.0  # Base max stamina (can be 2.0 with storm powerup)
        self.stamina = 1.0  # Current stamina
        self.stamina_exhausted = False  # Track if we just hit 0 stamina
        self.flip_locked_until_full = False  # Disable manual flip until stamina refills
        
        # Try to load sprites from sprite sheet
        self.sprite_sheet = None
        self.sprite_normal = None
        self.sprite_powered = None
        self.walk_frames = []
        self.attack_frames = []
        self.bullet_frames = []
        self.animation_timer = 0
        self.current_frame = 0
        
        # Attack state
        self.is_attacking = False
        self.attack_timer = Timer()
        self.attack_frame_duration = 0.1  # 100ms per attack frame
        self.bullet_spawned = False  # Track if bullet spawned this attack
        
        try:
            # Load the sprite sheet
            sheet_raw = pygame.image.load('game/assets/images/sprites/buddie0_sheet.png').convert()
            # Set black as transparent
            sheet_raw.set_colorkey((0, 0, 0))
            print(f"Loaded sprite sheet: {sheet_raw.get_size()}")
            sheet_width, sheet_height = sheet_raw.get_size()
            cell_width = 32
            cell_height = 32

            cols = sheet_width // cell_width
            rows = sheet_height // cell_height
            total_sprites = cols * rows

            print(f"Sheet size: {sheet_width}x{sheet_height}")
            print(f"Grid: {cols} columns x {rows} rows")
            print(f"Total sprites: {total_sprites}")
            
            # Sprite sheet is 32x32 per cell, 8x5 tiles
            # Row 0: idle frames
            # Row 1: walking frames (4 frames)
            frame_width = 32
            frame_height = 32
            
            # Extract idle frame (row 1, col 0)
            self.sprite_normal = sheet_raw.subsurface((0, frame_height, frame_width, frame_height)).copy()
            print("Loaded idle sprite")
            
            # Extract walking animation frames (row 3, 4 frames)
            for i in range(4):
                frame = sheet_raw.subsurface((i * frame_width, 3 * frame_height, frame_width, frame_height)).copy()
                self.walk_frames.append(frame)
            print(f"Loaded {len(self.walk_frames)} walk frames")

            # Extract attack animation frames (row 4, 4 frames)
            for i in range(4):
                x = i * frame_width
                y = 4 * frame_height   # row 4
                frame = sheet_raw.subsurface((x, y, frame_width, frame_height)).copy()
                self.attack_frames.append(frame)

            print(f"Loaded {len(self.attack_frames)} attack frames")
            
            # Extract bullet frames (row 4, frames 4-7)
            for i in range(4, 8):
                x = i * frame_width
                y = 4 * frame_height  # row 4
                frame = sheet_raw.subsurface((x, y, frame_width, frame_height)).copy()
                cropped = crop_surface(frame)
                self.bullet_frames.append(cropped)

            print(f"Loaded {len(self.bullet_frames)} bullet frames")

            
            # Powered-up uses a different row or glowing effect
            # For now, use row 2, frame 0 for powered state
            # self.sprite_powered = sheet_raw.subsurface((0, frame_height * 2, frame_width, frame_height)).copy()
            # print("Loaded powered sprite")
            
        except Exception as e:
            print(f"ERROR loading sprite sheet: {e}")
            # Create a dummy sprite so player is always visible
            self.sprite_normal = pygame.Surface((24, 32))
            self.sprite_normal.fill((50, 120, 220))  # Blue
            print("Using fallback colored rectangle")
        
        # Stats
        self.coins = 0
        self.checkpoint_pos = (x, y)
        self.checkpoint_coins = 0
        self.last_hp_bonus_at = 0  # Track coins when last HP bonus was given
        
        # State
        self.facing_right = True
        self.alive = True
    
    def update(self, dt, input_handler, collision_system):
        """Update player state"""
        if not self.alive:
            return
        
        # Update timers
        self.flip_cooldown.update(dt)
        self.coyote_timer.update(dt)
        self.jump_buffer.update(dt)
        self.invuln_timer.update(dt)
        self.flux_surge_timer.update(dt)
        self.attack_timer.update(dt)
        
        # Handle stamina
        self._handle_stamina(dt)
        
        # Handle input
        self._handle_attack(input_handler)
        self._handle_horizontal_input(dt, input_handler)
        self._handle_gravity_flip(input_handler)
        self._handle_jump(input_handler)
        
        # Check if attack finished
        if self.is_attacking and not self.attack_timer.is_active():
            self.is_attacking = False
            self.bullet_spawned = False
        
        # Update animation and spawn bullet mid-attack
        if self.is_attacking:
            # Attack animation
            attack_duration = len(self.attack_frames) * self.attack_frame_duration
            time_elapsed = attack_duration - self.attack_timer.time_left
            self.current_frame = int(time_elapsed / self.attack_frame_duration)
            self.current_frame = min(self.current_frame, len(self.attack_frames) - 1)
        elif abs(self.vel_x) > 10:  # Moving
            self.animation_timer += dt * 10  # Animation speed
            if self.animation_timer >= 1.0:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        else:
            self.current_frame = 0
            self.animation_timer = 0
        
        # Apply gravity
        gravity_accel = settings.GRAVITY * self.gravity_dir
        self.vel_y += gravity_accel * dt
        
        # Cap fall speed
        max_fall = 600
        if self.gravity_dir == 1:
            self.vel_y = min(self.vel_y, max_fall)
        else:
            self.vel_y = max(self.vel_y, -max_fall)
        
        # Move and handle collisions
        self._move(dt, collision_system)
    
    def _handle_stamina(self, dt):
        """Handle stamina drain and regeneration"""
        if self.on_ground:
            # Regenerate stamina when on ground
            regen_rate = settings.STAMINA_REGEN_RATE
            if self.stamina_boost:
                regen_rate *= 2.0  # 2x faster with storm powerup
            self.stamina = min(self.max_stamina, self.stamina + regen_rate * settings.STAMINA_DRAIN_RATE * dt)
            # Unlock flip when fully refilled
            if self.stamina >= self.max_stamina:
                self.stamina_exhausted = False
                self.flip_locked_until_full = False
        else:
            # Drain stamina when floating (not on ground)
            self.stamina = max(0.0, self.stamina - settings.STAMINA_DRAIN_RATE * dt)
            
            # Check if stamina just reached 0
            if self.stamina <= 0.0 and not self.stamina_exhausted:
                self.stamina_exhausted = True
                # Lock manual gravity flip until stamina fully refills
                self.flip_locked_until_full = True
    
    def _handle_attack(self, input_handler):
        """Handle attack input"""
        if input_handler.is_action_pressed('attack') and not self.is_attacking:
            self.is_attacking = True
            self.bullet_spawned = False
            attack_duration = len(self.attack_frames) * self.attack_frame_duration
            self.attack_timer.start(attack_duration)
            self.current_frame = 0
    
    def _handle_horizontal_input(self, dt, input_handler):
        """Handle left/right movement"""
        direction = input_handler.get_horizontal_input()
        
        # Determine speed
        base_speed = settings.PLAYER_RUN_SPEED
        if self.flux_surge_timer.is_active():
            base_speed = settings.PLAYER_BOOST_SPEED
        
        if direction != 0:
            self.vel_x = direction * base_speed
            self.facing_right = direction > 0
        else:
            # Apply friction when not moving
            self.vel_x = 0
    
    def _handle_gravity_flip(self, input_handler):
        """Handle gravity flip action"""
        # If flip is locked, ignore manual input until stamina fully refills
        if self.flip_locked_until_full:
            return
        if input_handler.is_action_pressed('action') and not self.flip_cooldown.is_active():
            self._trigger_gravity_flip()

    def _trigger_gravity_flip(self):
        """Flip gravity immediately, applying cooldown and velocity damping"""
        self.gravity_dir *= -1
        self.flip_cooldown.start(settings.GRAVITY_FLIP_COOLDOWN)
        # Reset velocity slightly to feel more responsive
        self.vel_y *= 0.5
    
    def _handle_jump(self, input_handler):
        """Handle jump with coyote time and buffer"""
        # Update coyote time
        if self.on_ground:
            self.coyote_timer.start()
        
        # Buffer jump input
        if input_handler.is_action_pressed('jump'):
            self.jump_buffer.start()
        
        # Execute jump if buffered and coyote time valid
        if self.jump_buffer.is_active() and self.coyote_timer.is_active():
            self._do_jump()
            self.jump_buffer.stop()
            self.coyote_timer.stop()
    
    def _do_jump(self):
        """Execute jump impulse"""
        # Jump opposite to gravity
        self.vel_y = -settings.PLAYER_JUMP_IMPULSE * self.gravity_dir
        self.on_ground = False
    
    def _move(self, dt, collision_system):
        """Move with collision detection"""
        # Store previous ground state
        was_on_ground = self.on_ground
        self.on_ground = False
        
        # Move horizontally
        self.rect.x += self.vel_x * dt
        
        # Check world boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > settings.WORLD_WIDTH:
            self.rect.right = settings.WORLD_WIDTH
            self.vel_x = 0
        
        # Check horizontal collisions
        collisions = collision_system.get_tile_collisions(self.rect, self.gravity_dir)
        for tile_rect in collisions:
            if self.vel_x > 0:  # Moving right
                self.rect.right = tile_rect.left
            elif self.vel_x < 0:  # Moving left
                self.rect.left = tile_rect.right
            self.vel_x = 0
        
        # Move vertically
        self.rect.y += self.vel_y * dt
        
        # Check world boundaries
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        elif self.rect.bottom > settings.WORLD_HEIGHT:
            self.rect.bottom = settings.WORLD_HEIGHT
            self.vel_y = 0
        
        # Check vertical collisions
        collisions = collision_system.get_tile_collisions(self.rect, self.gravity_dir)
        for tile_rect in collisions:
            if self.gravity_dir == 1:  # Normal gravity
                if self.vel_y > 0:  # Falling down
                    self.rect.bottom = tile_rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Moving up (jumping and hitting ceiling)
                    # Play bump sound when jumping and hitting ceiling
                    if self.audio and abs(self.vel_y) > 100:  # Only if moving fast enough
                        self.audio.play_sfx('bump')
                    self.rect.top = tile_rect.bottom
                    self.vel_y = 0
            else:  # Inverted gravity
                if self.vel_y < 0:  # "Falling" up
                    self.rect.top = tile_rect.bottom
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y > 0:  # Moving down (jumping and hitting floor in inverted gravity)
                    # Play bump sound when jumping and hitting floor
                    if self.audio and abs(self.vel_y) > 100:  # Only if moving fast enough
                        self.audio.play_sfx('bump')
                    self.rect.bottom = tile_rect.top
                    self.vel_y = 0
    
    def take_damage(self, amount=1, camera=None):
        """Take damage if not invulnerable"""
        print(f"DEBUG: take_damage called with amount={amount}, camera={camera is not None}, current_hp={self.hp}")
        
        if self.invuln_timer.is_active() or self.flux_surge_timer.is_active():
            print("DEBUG: Player is invulnerable, damage blocked")
            return False
        
        # Store previous health to check if we're dropping to 1
        previous_hp = self.hp
        
        self.hp -= amount
        self.invuln_timer.start(settings.PLAYER_INVULN_TIME)
        
        print(f"DEBUG: Damage taken! Previous HP: {previous_hp}, New HP: {self.hp}")
        
        # Trigger camera shake if health drops to 1 (from 2 or higher)
        if camera and previous_hp >= 2 and self.hp == 1:
            print(f"DEBUG: Camera shake triggered! Previous HP: {previous_hp}, Current HP: {self.hp}")
            camera.shake()
        
        if self.hp <= 0:
            self.alive = False
        
        return True
    
    def collect_coin(self):
        """Collect a coin and check for HP bonus"""
        self.coins += 1
        
        # Give HP bonus for every 10 coins (but not if already at max)
        coins_since_last_bonus = self.coins - self.last_hp_bonus_at
        if coins_since_last_bonus >= 10 and self.hp < settings.PLAYER_HP:
            self.hp += 1
            self.last_hp_bonus_at = self.coins
            if self.audio:
                self.audio.play_sfx('powerup')  # Play a sound for HP gain
            return True  # Signal that HP was gained
        return False
    
    def activate_flux_surge(self):
        """Activate Flux Surge (star) - invincibility + instant kill enemies"""
        self.flux_surge_timer.start(settings.FLUX_SURGE_DURATION)
    
    def activate_double_shot(self):
        """Activate double shot powerup (P icon) - permanent"""
        self.double_shot = True
    
    def activate_stamina_boost(self):
        """Activate stamina boost (storm/energy) - permanent 2x stamina + 2x regen"""
        if not self.stamina_boost:
            self.stamina_boost = True
            self.max_stamina = 2.0
            self.stamina = min(self.stamina * 2.0, self.max_stamina)  # Scale current stamina proportionally
    
    def set_checkpoint(self, pos):
        """Set respawn checkpoint"""
        self.checkpoint_pos = pos
        self.checkpoint_coins = self.coins
    
    def respawn(self):
        """Respawn at last checkpoint"""
        self.rect.x, self.rect.y = self.checkpoint_pos
        self.hp = settings.PLAYER_HP
        # Keep coins from checkpoint
        # self.coins stays as checkpoint_coins
        self.vel_x = 0
        self.vel_y = 0
        self.gravity_dir = 1
        self.alive = True
        self.invuln_timer.stop()
        self.flux_surge_timer.stop()
        # Reset stamina to max (keep permanent upgrades)
        self.stamina = self.max_stamina
        self.stamina_exhausted = False
        self.flip_locked_until_full = False
        # Keep double_shot and stamina_boost (permanent powerups)
    
    def is_invulnerable(self):
        """Check if player is currently invulnerable"""
        return self.invuln_timer.is_active() or self.flux_surge_timer.is_active()
    
    def is_flux_surge_active(self):
        """Check if Flux Surge (star) is active"""
        return self.flux_surge_timer.is_active()
    
    def get_flux_surge_time_left(self):
        """Get remaining Flux Surge time"""
        return self.flux_surge_timer.time_left if self.flux_surge_timer.is_active() else 0
    
    def has_double_shot(self):
        """Check if player has double shot powerup"""
        return self.double_shot
    
    def has_stamina_boost(self):
        """Check if player has stamina boost"""
        return self.stamina_boost
    
    def get_stamina(self):
        """Get current stamina as a percentage (0.0 to max_stamina)"""
        return self.stamina
    
    def get_stamina_ratio(self):
        """Get stamina as a ratio (0.0 to 1.0) for UI display"""
        return self.stamina / self.max_stamina if self.max_stamina > 0 else 0
    
    def should_spawn_bullet(self):
        """Check if bullet should spawn (mid-attack animation)"""
        # Spawn immediately when attack starts (no animation frame delay)
        if self.is_attacking and not self.bullet_spawned:
            self.bullet_spawned = True
            return True
        return False
    
    def get_bullet_spawn_pos(self):
        """Get position where bullet should spawn (gun tip position)"""
        # Offset from player center
        offset_x = 16 if self.facing_right else -16
        offset_y = 0  # Adjust if gun is higher/lower
        return (self.rect.centerx + offset_x, self.rect.centery + offset_y)
    
    def draw(self, screen, camera):
        """Draw player"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.x
        draw_rect.y -= camera.y
        
        # Draw stamina bar if needed (floating or refilling)
        should_show_stamina = not self.on_ground or (self.on_ground and self.stamina < self.max_stamina)
        if should_show_stamina:
            self._draw_stamina_bar(screen, draw_rect)
        
        # Flashing effect during invulnerability (skip rendering every 10 frames)
        is_invulnerable = self.invuln_timer.is_active()
        should_skip_render = is_invulnerable and (int(self.invuln_timer.time_left * 60) % 10 < 5)
        
        # Try to use sprite with animation
        sprite = None
        if self.is_attacking and len(self.attack_frames) > 0:
            # Use attack animation
            sprite = self.attack_frames[self.current_frame]
        elif abs(self.vel_x) > 10 and len(self.walk_frames) > 0:
            # Use walking animation
            sprite = self.walk_frames[self.current_frame]
        elif self.sprite_normal:
            # Use idle sprite
            sprite = self.sprite_normal
        
        if sprite and not should_skip_render:            
            sprite = crop_surface(sprite)
            sprite_scaled = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))

            if not self.facing_right:
                sprite_scaled = pygame.transform.flip(sprite_scaled, True, False)
            if self.gravity_dir == -1:
                sprite_scaled = pygame.transform.flip(sprite_scaled, False, True)
            
            # Add YELLOW glow ONLY for flux surge (star powerup - invincibility + instant kill)
            if self.flux_surge_timer.is_active():
                time_left = self.flux_surge_timer.time_left
                # Flicker when almost over (last 3 seconds)
                should_show_glow = True
                if time_left <= 3.0:
                    # Flicker faster as time runs out
                    flicker_speed = 10 if time_left > 1.5 else 20
                    should_show_glow = (int(time_left * flicker_speed) % 2 == 0)
                
                if should_show_glow:
                    glow_surf = pygame.Surface((self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA)
                    # Bright yellow glow for star powerup only
                    pygame.draw.circle(glow_surf, (255, 255, 100, 80), (self.rect.width // 2 + 8, self.rect.height // 2 + 8), self.rect.width // 2 + 8)
                    screen.blit(glow_surf, (draw_rect.centerx - self.rect.width // 2 - 8, draw_rect.centery - self.rect.height // 2 - 8))
            
            # No glow for double shot (P powerup) - permanent upgrade, shown in HUD only
            # No glow for stamina boost (storm) - permanent upgrade, shown in HUD only
            
            # Position the sprite relative to the collision box
            sprite_rect = sprite_scaled.get_rect(center=self.rect.center)
            sprite_rect.x -= camera.x
            sprite_rect.y -= camera.y
            # Draw sprite
            screen.blit(sprite_scaled, draw_rect)
        elif not should_skip_render:
            # Fallback: colored rect
            # Check for flux surge with flickering when almost over
            if self.flux_surge_timer.is_active():
                time_left = self.flux_surge_timer.time_left
                should_show = True
                if time_left <= 3.0:
                    flicker_speed = 10 if time_left > 1.5 else 20
                    should_show = (int(time_left * flicker_speed) % 2 == 0)
                color = settings.COLOR_YELLOW if should_show else settings.COLOR_BLUE
            elif is_invulnerable:
                color = (150, 200, 255)  # Light blue when invulnerable
            else:
                color = settings.COLOR_BLUE
            
            pygame.draw.rect(screen, color, draw_rect)
            
            # Draw facing direction indicator
            indicator_x = draw_rect.right if self.facing_right else draw_rect.left
            indicator_y = draw_rect.centery
            indicator_points = [
                (indicator_x, indicator_y - 5),
                (indicator_x + (10 if self.facing_right else -10), indicator_y),
                (indicator_x, indicator_y + 5)
            ]
            pygame.draw.polygon(screen, settings.COLOR_WHITE, indicator_points)
    
    def _draw_stamina_bar(self, screen, draw_rect):
        """Draw stamina bar relative to gravity (above when normal, below when flipped)"""
        bar_width = 32
        bar_height = 4
        bar_x = draw_rect.centerx - bar_width // 2
        # Place above in normal gravity, below when flipped
        if self.gravity_dir == 1:
            bar_y = draw_rect.top - 10
        else:
            bar_y = draw_rect.bottom + 6
        
        # Background bar (empty)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, settings.COLOR_DARK_GRAY, bg_rect)
        
        # Foreground bar (filled based on stamina ratio)
        stamina_ratio = self.stamina / self.max_stamina if self.max_stamina > 0 else 0
        fill_width = int(bar_width * stamina_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            # Color based on stamina level
            if stamina_ratio > 0.5:
                color = settings.COLOR_GREEN
            elif stamina_ratio > 0.25:
                color = settings.COLOR_YELLOW
            else:
                color = settings.COLOR_RED
            pygame.draw.rect(screen, color, fill_rect)
        
        # Border (cyan if stamina boost is active)
        border_color = (100, 200, 255) if self.stamina_boost else settings.COLOR_WHITE
        pygame.draw.rect(screen, border_color, bg_rect, 1)
