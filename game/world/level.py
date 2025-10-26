"""
Level state - main gameplay
"""
import pygame
from game.core import GameState, settings, Stopwatch
from game.core.clear_conditions import ClearConditions
from game.world.camera import Camera
from game.world.collisions import CollisionSystem
from game.world.checkpoints import Checkpoint
from game.world.background import ParallaxBackground
from game.entities.player import Player
from game.entities.coin import Coin
from game.entities.star import FluxStar
from game.entities.powerup import PowerUp
from game.entities.storm import StormPowerup
from game.entities.spikes import Spikes
from game.entities.breakable import BreakableBlock
from game.entities.enemy import Drone
from game.entities.boss import GyroBoss
from game.entities.bullet import Bullet
from game.entities.button import Button
from game.entities.gate import Gate
from game.io.input import InputHandler
from game.io.level_loader import LevelLoader
from game.ui.hud import HUD


class LevelState(GameState):
    """Main gameplay state"""
    
    def __init__(self, stack, level_id=1, restore_checkpoint=False):
        super().__init__(stack)
        
        # Load level
        level_path = f"game/assets/levels/level{level_id}.json"
        level_data = LevelLoader.load_from_json(level_path)
        self.level_id = level_id
        
        # Track this attempt
        from game.core.save_system import SaveSystem
        SaveSystem.start_level(level_id)
        self.level_stats = SaveSystem.get_level_stats(level_id)
        
        # Set up systems
        self.collision_system = CollisionSystem(level_data['tile_map'])
        self.tile_map = level_data['tile_map']
        self.camera = Camera(settings.WORLD_WIDTH, settings.WORLD_HEIGHT)
        self.background = ParallaxBackground(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Load key bindings from persistent data
        key_bindings = stack.persistent_data.get('key_bindings')
        self.input_handler = InputHandler(key_bindings)
        stack.persistent_data['input_handler'] = self.input_handler
        
        self.hud = HUD()
        self.stopwatch = Stopwatch()
        # Low-health effect timer
        self.low_health_flash_timer = 0.0
        
        # Audio
        self.audio = stack.persistent_data.get('audio')
        
        # Always spawn player at level spawn point
        self.player = Player(level_data['spawn_x'], level_data['spawn_y'], self.audio)
        
        # Spawn coins (always fresh)
        self.coins = []
        for pos in level_data['coins']:
            coin = Coin(pos[0], pos[1])
            coin.initial_pos = (pos[0], pos[1])  # Store for identification
            self.coins.append(coin)
        
        # Spawn stars (always fresh)
        self.stars = []
        for pos in level_data['stars']:
            star = FluxStar(pos[0], pos[1])
            star.initial_pos = (pos[0], pos[1])
            self.stars.append(star)
        
        # Spawn power-ups (always fresh)
        self.powerups = []
        for pdata in level_data.get('powerups', []):
            powerup = PowerUp(pdata['x'], pdata['y'], pdata['type'])
            powerup.initial_pos = (pdata['x'], pdata['y'])
            self.powerups.append(powerup)
        
        # Spawn storm powerups (always fresh)
        self.storms = []
        for pos in level_data.get('storms', []):
            print(f"Loading storm at position: {pos}")  # Debug output
            storm = StormPowerup(pos[0], pos[1])
            storm.initial_pos = (pos[0], pos[1])
            self.storms.append(storm)
        
        print(f"Total storms loaded: {len(self.storms)}")  # Debug output
        
        # Spawn spikes
        self.spikes = []
        for sdata in level_data.get('spikes', []):
            self.spikes.append(Spikes(sdata['x'], sdata['y'], sdata['orientation']))
        
        # Spawn gates
        self.gates = []
        for gdata in level_data.get('gates', []):
            gate = Gate(gdata['x'], gdata['y'], gdata['height'], gdata['orientation'])
            gate.initial_pos = (gdata['x'], gdata['y'])
            self.gates.append(gate)
        
        # Spawn buttons
        self.buttons = []
        for bdata in level_data.get('buttons', []):
            button = Button(bdata['x'], bdata['y'], bdata['color'], bdata.get('facing', 'up'))
            button.initial_pos = (bdata['x'], bdata['y'])
            self.buttons.append(button)
        
        # Wire button callbacks to gates for level 2 puzzle
        if self.level_id == 2 and len(self.buttons) >= 2 and len(self.gates) >= 3:
            # Button 0 (bottom) toggles gates 0 and 2 (1st and 3rd)
            def toggle_gates_0_and_2():
                self.gates[0].toggle()
                self.gates[2].toggle()
            self.buttons[0].on_toggle = toggle_gates_0_and_2
            
            # Button 1 (middle) toggles gates 1 and 2 (2nd and 3rd)
            def toggle_gates_1_and_2():
                self.gates[1].toggle()
                self.gates[2].toggle()
            self.buttons[1].on_toggle = toggle_gates_1_and_2
        
        # Spawn breakable blocks (always fresh)
        self.breakables = []
        for bdata in level_data.get('breakables', []):
            block = BreakableBlock(bdata['x'], bdata['y'], bdata['contents'])
            block.initial_pos = (bdata['x'], bdata['y'])
            self.breakables.append(block)
        
        # Spawn checkpoints
        self.checkpoints = []
        for pos in level_data['checkpoints']:
            self.checkpoints.append(Checkpoint(pos[0], pos[1]))
        
        # Spawn enemies (always fresh)
        self.enemies = []
        for enemy_data in level_data['enemies']:
            if enemy_data['type'] == 'drone':
                color = enemy_data.get('color', 'blue')
                drone = Drone(enemy_data['x'], enemy_data['y'],
                            enemy_data['anchor'], enemy_data['range'], color)
                drone.initial_pos = (enemy_data['x'], enemy_data['y'])
                self.enemies.append(drone)
        
        # Spawn boss (only if boss exists in level)
        if 'boss_x' in level_data and 'boss_y' in level_data:
            self.boss = GyroBoss(level_data['boss_x'], level_data['boss_y'])
            self.boss_active = False
            self.boss_door_open = False
        else:
            self.boss = None
            self.boss_active = False
            self.boss_door_open = False
        
        # Set boss arena bounds for spike attacks (only if boss exists)
        if self.boss:
            # Find floor and ceiling positions near boss
            boss_tile_x = level_data['boss_x'] // settings.TILE_SIZE
            boss_tile_y = level_data['boss_y'] // settings.TILE_SIZE
            
            # Search for floor (below boss)
            floor_y = level_data['boss_y']
            for y in range(boss_tile_y, len(self.tile_map)):
                if self.tile_map[y][boss_tile_x] is not None:
                    floor_y = y * settings.TILE_SIZE
                    break
            
            # Search for ceiling (above boss)
            ceiling_y = level_data['boss_y']
            for y in range(boss_tile_y, -1, -1):
                if self.tile_map[y][boss_tile_x] is not None:
                    ceiling_y = (y + 1) * settings.TILE_SIZE
                    break

            # Set arena width (roughly 400 pixels on each side of boss)
            left_x = max(0, level_data['boss_x'] - 400)
            right_x = min(settings.WORLD_WIDTH, level_data['boss_x'] + 400)

            self.boss.set_arena_bounds(floor_y, ceiling_y, left_x, right_x)
        
        # Bullets
        self.bullets = []
        
        # Debug mode
        self.show_hitboxes = False
        
        # Checkpoint state persistence
        self.checkpoint_data = None  # Stores snapshot when checkpoint activated
        
        # Clear conditions tracking
        self.clear_conditions = ClearConditions(len(self.enemies))
        
        # Start timer
        self.stopwatch.start()
        
        # Boss music tracking
        self.boss_music_playing = False
        
        # Restore from saved checkpoint if requested
        if restore_checkpoint:
            saved_data = SaveSystem._load_data()
            if 'game_state' in saved_data and saved_data['game_state']:
                game_state = saved_data['game_state']
                # Restore checkpoint data
                if 'entities' in game_state and game_state['entities']:
                    self.checkpoint_data = game_state['entities']
                    # Apply the checkpoint state immediately
                    self._restore_from_checkpoint_data()
                    print("DEBUG: Restored from saved checkpoint")
    
    def enter(self, previous_state=None):
        """Called when entering this state"""
        if self.audio:
            self.audio.play_music(self.audio.MUSIC_GAME)
    
    def update(self, dt, events):
        """Update gameplay"""
        # Update input
        self.input_handler.update(events)
        
        # Check for pause
        if self.input_handler.is_action_pressed('pause'):
            from game.ui.pause import PauseState
            self.stack.push(PauseState)
            return
        
        # Toggle debug hitboxes
        if self.input_handler.is_action_pressed('debug'):
            self.show_hitboxes = not self.show_hitboxes
        
        # Update player
        self.player.update(dt, self.input_handler, self.collision_system)
        
        # Spawn bullet(s) if player is attacking
        if self.player.should_spawn_bullet():
            x, y = self.player.get_bullet_spawn_pos()
            direction = 1 if self.player.facing_right else -1
            
            # Check if double shot is active (permanent P powerup)
            if self.player.has_double_shot():
                # Spawn 2 bullets: up and down
                bullets_to_spawn = [
                    (x, y - 8, direction),  # Upper bullet
                    (x, y + 8, direction)   # Lower bullet
                ]
            else:
                # Normal single bullet
                bullets_to_spawn = [(x, y, direction)]
            
            # Create bullets
            for bullet_x, bullet_y, bullet_dir in bullets_to_spawn:
                bullet = Bullet(bullet_x, bullet_y, bullet_dir, self.player.bullet_frames)
                self.bullets.append(bullet)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt, self.collision_system)
            if not bullet.alive:
                self.bullets.remove(bullet)
            else:
                # Check bullet hits enemy
                for enemy in self.enemies:
                    if enemy.alive and bullet.rect.colliderect(enemy.rect):
                        enemy.take_damage()
                        bullet.alive = False
                        if not enemy.alive:  # Enemy was defeated
                            self.clear_conditions.defeat_enemy()
                        if self.audio:
                            self.audio.play_sfx('stomp')
                        break
                
                # Check bullet hits button
                for button in self.buttons:
                    if button.check_bullet_hit(bullet.rect):
                        button.activate()
                        bullet.alive = False
                        if self.audio:
                            self.audio.play_sfx('stomp')
                        break
                
                # Check bullet hits boss
                if self.boss and self.boss_active and self.boss.vulnerable and bullet.rect.colliderect(self.boss.rect):
                    if self.boss.take_damage():
                        bullet.alive = False
                        if self.audio:
                            self.audio.play_sfx('boss_hit')
        
        # Update camera
        self.camera.update(self.player.rect, dt)
        
        # Update background
        self.background.update(self.camera.x)
        
        # Update stopwatch
        self.stopwatch.update(dt)
        
        # Update coins
        for coin in self.coins:
            if coin.update(dt, self.player.rect):
                hp_gained = self.player.collect_coin()
                if self.audio:
                    self.audio.play_sfx('coin')
                # No extra sound for HP gain - already played in collect_coin()
        
        # Update stars
        for star in self.stars:
            if star.update(dt, self.player.rect):
                self.player.activate_flux_surge()
                if self.audio:
                    self.audio.play_sfx('powerup')
        
        # Update power-ups (P icon - permanent double shot)
        for powerup in self.powerups:
            if powerup.update(dt, self.player.rect):
                self.player.activate_double_shot()
                if self.audio:
                    self.audio.play_sfx('powerup')
        
        # Update storm powerups (energy - permanent stamina boost)
        for storm in self.storms:
            if storm.update(dt, self.player.rect):
                self.player.activate_stamina_boost()
                if self.audio:
                    self.audio.play_sfx('powerup')
        
        # Update storm visual effect
        if hasattr(self, 'storm_flash_timer') and self.storm_flash_timer > 0:
            self.storm_flash_timer -= dt
        
        # Update breakable blocks
        for block in self.breakables:
            block.update(dt)
            if block.is_solid() and block.rect.colliderect(self.player.rect):
                # Check if player hits it
                if abs(self.player.vel_y) > 50:  # Moving with some velocity
                    item = block.hit('any')
                    if item == 'coin':
                        # Spawn coin above block
                        coin = Coin(block.rect.centerx - 8, block.rect.top - 20)
                        coin.initial_pos = (block.rect.centerx - 8, block.rect.top - 20)
                        self.coins.append(coin)
                    elif item == 'powerup':
                        # Spawn power-up above block
                        powerup = PowerUp(block.rect.centerx - 12, block.rect.top - 30)
                        powerup.initial_pos = (block.rect.centerx - 12, block.rect.top - 30)
                        self.powerups.append(powerup)
        
        # Update buttons
        for button in self.buttons:
            button.update(dt)
            # Check if player stomped button
            if button.check_stomp(self.player.rect, self.player.vel_y, self.player.gravity_dir):
                button.activate()
                # Bounce player slightly
                self.player.vel_y = -settings.PLAYER_JUMP_IMPULSE * self.player.gravity_dir * 0.5
                if self.audio:
                    self.audio.play_sfx('stomp')
        
        # Update gates
        for gate in self.gates:
            gate.update(dt)
            
            # Check if gate blocks player movement (solid collision)
            if gate.is_solid():
                gate_rect = gate.get_collision_rect()
                if gate_rect.colliderect(self.player.rect):
                    # Push player out of gate
                    overlap_x = min(self.player.rect.right, gate_rect.right) - max(self.player.rect.left, gate_rect.left)
                    overlap_y = min(self.player.rect.bottom, gate_rect.bottom) - max(self.player.rect.top, gate_rect.top)
                    
                    # Push in direction of smallest overlap
                    if overlap_x < overlap_y:
                        # Push horizontally
                        if self.player.rect.centerx < gate_rect.centerx:
                            self.player.rect.right = gate_rect.left
                        else:
                            self.player.rect.left = gate_rect.right
                        self.player.vel_x = 0
                    else:
                        # Push vertically
                        if self.player.rect.centery < gate_rect.centery:
                            self.player.rect.bottom = gate_rect.top
                            self.player.on_ground = True
                        else:
                            self.player.rect.top = gate_rect.bottom
                        self.player.vel_y = 0
            
            # Check gate collision (damage from spikes)
            if gate.check_collision(self.player.rect, self.player.gravity_dir, self.player.is_invulnerable()):
                if not self.player.is_invulnerable():
                    previous_hp = self.player.hp
                    if self.player.take_damage(camera=self.camera):
                        if self.audio:
                            self.audio.play_sfx('hit')
                        if previous_hp >= 2 and self.player.hp == 1:
                            self.low_health_flash_timer = 0.35
        
        # Check spike collisions
        for spike in self.spikes:
            if spike.check_collision(self.player.rect, self.player.gravity_dir, self.player.is_invulnerable()):
                if not self.player.is_invulnerable():
                    previous_hp = self.player.hp
                    if self.player.take_damage(camera=self.camera):
                        if self.audio:
                            self.audio.play_sfx('hit')
                        # Trigger low-health overlay when dropping to 1 HP
                        if previous_hp >= 2 and self.player.hp == 1:
                            self.low_health_flash_timer = 0.35
        
        # # Check if player is stuck on spikes (apply movement restrictions)
        # player_stuck_on_spikes = False
        # for spike in self.spikes:
        #     if spike.is_player_stuck(self.player.rect, self.player.gravity_dir):
        #         player_stuck_on_spikes = True
        #         break
        
        # # Apply sticky behavior - reduce movement speed when stuck on spikes
        # if player_stuck_on_spikes:
        #     # Reduce horizontal movement speed significantly
        #     self.player.vel_x *= 0.1  # Only 10% of normal speed
        #     # Prevent jumping when stuck (make it harder to escape)
        #     if self.player.vel_y < 0:  # If trying to jump
        #         self.player.vel_y *= 0.3  # Reduce jump power
        
        # Update checkpoints
        for checkpoint in self.checkpoints:
            if checkpoint.update(dt, self.player.rect):
                # Set checkpoint to middle of checkpoint position
                self.player.set_checkpoint((checkpoint.rect.centerx - self.player.rect.width // 2, 
                                           checkpoint.rect.bottom - self.player.rect.height))
                # Capture game state when checkpoint is activated
                self._capture_checkpoint_state()
                if self.audio:
                    self.audio.play_sfx('checkpoint')
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.collision_system)
            
            # Check collision with player
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                # If Flux Surge (star) is active, instantly kill enemy on contact
                if self.player.is_flux_surge_active():
                    enemy.take_damage()
                    if not enemy.alive:  # Enemy was defeated
                        self.clear_conditions.defeat_enemy()
                    if self.audio:
                        self.audio.play_sfx('stomp')
                # Check stomp
                elif enemy.check_stomp(self.player):
                    enemy.take_damage()
                    if not enemy.alive:  # Enemy was defeated
                        self.clear_conditions.defeat_enemy()
                    self.player.vel_y = -settings.PLAYER_JUMP_IMPULSE * self.player.gravity_dir * 0.7  # Bounce
                    if self.audio:
                        self.audio.play_sfx('stomp')
                else:
                    # Not a stomp - hit player
                    if not self.player.is_invulnerable():
                        previous_hp = self.player.hp
                        if self.player.take_damage(camera=self.camera):
                            if self.audio:
                                self.audio.play_sfx('hit')
                            if previous_hp >= 2 and self.player.hp == 1:
                                self.low_health_flash_timer = 0.35
        
        # Update boss (only if boss exists)
        if self.boss:
            if self.player.rect.right > self.boss.rect.left - 200:
                self.boss_active = True
            
            # Handle boss music transition
            if self.boss_active and not self.boss.defeated and not self.boss_music_playing:
                # Switch to boss music
                if self.audio:
                    self.audio.play_music(self.audio.MUSIC_BOSS)
                self.boss_music_playing = True
            elif self.boss.defeated and self.boss_music_playing:
                # Boss defeated, switch back to game music
                if self.audio:
                    self.audio.play_music(self.audio.MUSIC_GAME)
                self.boss_music_playing = False
            
            if self.boss_active:
                self.boss.update(dt)
                
                # Check if boss hazards (lasers + spikes) hit player
                if self.boss.check_hit_player(self.player.rect, self.player.is_invulnerable(), self.player.gravity_dir):
                    previous_hp = self.player.hp
                    if self.player.take_damage(camera=self.camera):
                        if self.audio:
                            self.audio.play_sfx('hit')
                        if previous_hp >= 2 and self.player.hp == 1:
                            self.low_health_flash_timer = 0.35
                
                # Check if player hits boss during vulnerable phase
                if self.boss.vulnerable and self.player.rect.colliderect(self.boss.rect):
                    if self.player.gravity_dir == 1 and self.player.vel_y > 0:
                        # Stomp from above
                        if self.boss.take_damage():
                            self.player.vel_y = -settings.PLAYER_JUMP_IMPULSE * 0.7
                            if self.audio:
                                self.audio.play_sfx('boss_hit')
                    elif self.player.gravity_dir == -1 and self.player.vel_y < 0:
                        # Stomp from below
                        if self.boss.take_damage():
                            self.player.vel_y = settings.PLAYER_JUMP_IMPULSE * 0.7
                            if self.audio:
                                self.audio.play_sfx('boss_hit')
                
                # Check if boss defeated
                if self.boss.defeated and not self.boss_door_open:
                    self.boss_door_open = True
                    self.clear_conditions.defeat_boss()
            
            # Check win condition (for boss levels)
            if self.boss_door_open and self.boss.defeated and self.player.rect.x > settings.WORLD_WIDTH - 100:
                from game.ui.win import WinState
                self.clear_conditions.set_completion_time(self.stopwatch.get_time())
                self.stack.replace_with_transition(WinState, 
                                 coins=self.player.coins, 
                                 time=self.stopwatch.get_time(),
                                 clear_conditions=self.clear_conditions,
                                 level_id=self.level_id)
                return
        else:
            # No boss - check win condition for reaching end of level
            if self.player.rect.x > settings.WORLD_WIDTH - 100:
                from game.ui.win import WinState
                self.clear_conditions.set_completion_time(self.stopwatch.get_time())
                self.stack.replace_with_transition(WinState, 
                                 coins=self.player.coins, 
                                 time=self.stopwatch.get_time(),
                                 clear_conditions=self.clear_conditions,
                                 level_id=self.level_id)
                return
        
        # Check lose condition
        if not self.player.alive:
            # Show lose screen with transition
            from game.ui.lose import LoseState
            self.stack.push_with_transition(LoseState)  # Push with transition
            
            # Reset level state to checkpoint
            self._reset_to_checkpoint()
            return
    
    def draw(self, screen):
        """Draw level"""
        # Draw parallax background
        self.background.draw(screen)
        
        # Draw tiles
        for row in self.tile_map:
            for tile in row:
                if tile:
                    tile.draw(screen, self.camera)
        
        # Draw checkpoints
        for checkpoint in self.checkpoints:
            checkpoint.draw(screen, self.camera)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(screen, self.camera)
        
        # Draw stars
        for star in self.stars:
            star.draw(screen, self.camera)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(screen, self.camera)
        
        # Draw breakable blocks
        for block in self.breakables:
            block.draw(screen, self.camera)
        
        # Draw spikes
        for spike in self.spikes:
            spike.draw(screen, self.camera, self.show_hitboxes)
        
        # Draw gates
        for gate in self.gates:
            gate.draw(screen, self.camera)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen, self.camera)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera)
            # Draw hitbox if debug mode
            if self.show_hitboxes:
                debug_rect = enemy.rect.copy()
                debug_rect.x -= self.camera.x
                debug_rect.y -= self.camera.y
                pygame.draw.rect(screen, (255, 0, 255), debug_rect, 2)
        
        # Draw boss (only if boss exists)
        if self.boss and self.boss_active:
            self.boss.draw(screen, self.camera)
            if self.show_hitboxes:
                debug_rect = self.boss.rect.copy()
                debug_rect.x -= self.camera.x
                debug_rect.y -= self.camera.y
                pygame.draw.rect(screen, (255, 0, 255), debug_rect, 2)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen, self.camera)
        
        # Draw player
        self.player.draw(screen, self.camera)
        if self.show_hitboxes:
            debug_rect = self.player.rect.copy()
            debug_rect.x -= self.camera.x
            debug_rect.y -= self.camera.y
            pygame.draw.rect(screen, (0, 255, 0), debug_rect, 2)
        
        # Draw storms
        for storm in self.storms:
            storm.draw(screen, self.camera)
        
        # Low-health flash overlay when HP just dropped to 1
        if self.low_health_flash_timer > 0:
            self.low_health_flash_timer = max(0.0, self.low_health_flash_timer - (1.0 / settings.FPS))
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            # Fade out alpha
            alpha = int(180 * (self.low_health_flash_timer / 0.35))
            overlay.fill((220, 30, 30, alpha))
            screen.blit(overlay, (0, 0))

        # Draw storm flash effect
        if hasattr(self, 'storm_flash_timer') and self.storm_flash_timer > 0:
            # Create a white flash overlay
            flash_surf = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(255 * (self.storm_flash_timer / 0.5))  # Fade out over 0.5 seconds
            flash_surf.fill((255, 255, 255, alpha))
            screen.blit(flash_surf, (0, 0))
        
        # Draw HUD
        boss_to_draw = self.boss if self.boss_active else None
        # Prepare entities for minimap overlay
        minimap_entities = {
            'bullets': self.bullets,
            'coins': self.coins,
            'stars': self.stars,
            'powerups': self.powerups,
            'storms': self.storms,
            'enemies': self.enemies,
        }
        
        self.hud.draw(screen, self.player, boss=boss_to_draw, show_fps=True, 
                     fps=self.stack.persistent_data.get('fps', 60), show_hitboxes=self.show_hitboxes,
                     clear_conditions=self.clear_conditions, game_time=self.stopwatch.get_time(), camera=self.camera,
                     minimap_entities=minimap_entities, audio_manager=self.audio)
    
    def _reset_to_checkpoint(self):
        """Reset level state when respawning from checkpoint"""
        print("DEBUG: Resetting to checkpoint...")
        # Respawn player
        self.player.respawn()
        
        # Clear all bullets
        self.bullets.clear()
        
        # Restore from checkpoint data if it exists
        if self.checkpoint_data:
            print("DEBUG: Restoring from checkpoint data")
            # Restore player state
            player_state = self.checkpoint_data['player']
            self.player.hp = settings.PLAYER_HP  # Always restore to max HP on respawn
            self.player.coins = player_state['coins']
            self.player.double_shot = player_state['double_shot']
            self.player.stamina_boost = player_state['stamina_boost']
            self.player.max_stamina = player_state['max_stamina']
            self.player.checkpoint_coins = player_state['checkpoint_coins']
            self.player.last_hp_bonus_at = player_state['last_hp_bonus_at']
            
            # Restore enemy states - keep dead enemies dead
            dead_enemy_positions = set(self.checkpoint_data['dead_enemies'])
            for enemy in self.enemies:
                if enemy.initial_pos in dead_enemy_positions:
                    enemy.alive = False
                    enemy.hp = 0
                else:
                    enemy.alive = True
                    enemy.hp = 1
            
            # Restore enemies_defeated count
            if 'enemies_defeated' in self.checkpoint_data:
                self.clear_conditions.enemies_defeated = self.checkpoint_data['enemies_defeated']
            
            # Restore collected items - keep them collected
            collected_coin_positions = set(self.checkpoint_data['collected_coins'])
            for coin in self.coins:
                if hasattr(coin, 'initial_pos'):
                    coin.collected = coin.initial_pos in collected_coin_positions
            
            collected_star_positions = set(self.checkpoint_data['collected_stars'])
            for star in self.stars:
                if hasattr(star, 'initial_pos'):
                    star.collected = star.initial_pos in collected_star_positions
            
            collected_powerup_positions = set(self.checkpoint_data['collected_powerups'])
            for powerup in self.powerups:
                if hasattr(powerup, 'initial_pos'):
                    powerup.collected = powerup.initial_pos in collected_powerup_positions
            
            collected_storm_positions = set(self.checkpoint_data['collected_storms'])
            for storm in self.storms:
                if hasattr(storm, 'initial_pos'):
                    storm.collected = storm.initial_pos in collected_storm_positions
            
            # Restore broken blocks
            broken_block_positions = set(self.checkpoint_data['broken_blocks'])
            for block in self.breakables:
                block.broken = block.initial_pos in broken_block_positions
            
            # Restore button/gate states
            button_states = self.checkpoint_data['button_states']
            for button in self.buttons:
                if button.initial_pos in button_states:
                    button.pressed = button_states[button.initial_pos]
            
            gate_states = self.checkpoint_data['gate_states']
            for gate in self.gates:
                if gate.initial_pos in gate_states:
                    gate.open = gate_states[gate.initial_pos]
            
            # Restore boss state
            boss_state = self.checkpoint_data['boss_state']
            if self.boss and boss_state:
                self.boss.hp = boss_state['hp']
                self.boss.defeated = boss_state['defeated']
                self.boss.phase = boss_state['phase']
                self.boss.alive = boss_state['alive']
                self.boss_active = False  # Boss not active until player approaches
                self.boss_door_open = boss_state['defeated']
                self.boss_music_playing = False
        else:
            # No checkpoint data - reset to fresh state (original behavior)
            for enemy in self.enemies:
                enemy.alive = True
                enemy.hp = 1
            
            for coin in self.coins:
                coin.collected = False
            
            for star in self.stars:
                star.collected = False
            
            for powerup in self.powerups:
                powerup.collected = False
            
            for storm in self.storms:
                storm.collected = False
            
            self.clear_conditions.enemies_defeated = 0
            self.player.coins = 0
            
            if self.boss:
                self.boss_active = False
                self.boss.defeated = False
                self.boss.alive = True
                self.boss.hp = settings.BOSS_HP
                self.boss.vulnerable = False
                self.boss.phase = 'spin_up'
                self.boss.pattern_timer.start(settings.BOSS_PATTERN_DURATION)
                self.boss.phase_timer.stop()
                self.boss.beam_rotation = 0
                self.boss.spike_attack_timer = 0
                self.boss.animated_spikes.clear()
                self.boss_door_open = False
                self.boss_music_playing = False
        
        # Reset input states so keys aren't stuck
        self.input_handler.reset_movement_inputs()
        
        # Update camera to player position
        self.camera.x = self.player.rect.centerx - settings.SCREEN_WIDTH // 2
        self.camera.x = max(0, min(self.camera.x, settings.WORLD_WIDTH - settings.SCREEN_WIDTH))
    
    def _restore_from_checkpoint_data(self):
        """Restore game state from checkpoint_data (used when loading saved game)"""
        if not self.checkpoint_data:
            return
        
        print("DEBUG: Applying checkpoint data...")
        
        # Restore player state
        player_state = self.checkpoint_data.get('player', {})
        if player_state:
            self.player.hp = settings.PLAYER_HP  # Always restore to max HP
            self.player.coins = player_state.get('coins', 0)
            self.player.double_shot = player_state.get('double_shot', False)
            self.player.stamina_boost = player_state.get('stamina_boost', False)
            self.player.max_stamina = player_state.get('max_stamina', 1.0)
            self.player.checkpoint_pos = tuple(player_state.get('checkpoint_pos', self.player.checkpoint_pos))
            self.player.checkpoint_coins = player_state.get('checkpoint_coins', 0)
            self.player.last_hp_bonus_at = player_state.get('last_hp_bonus_at', 0)
            # Move player to checkpoint
            self.player.rect.x, self.player.rect.y = self.player.checkpoint_pos
        
        # Restore enemy states (convert lists back to tuples for hashing)
        dead_enemy_positions = set(tuple(pos) if isinstance(pos, list) else pos 
                                   for pos in self.checkpoint_data.get('dead_enemies', []))
        for enemy in self.enemies:
            if hasattr(enemy, 'initial_pos'):
                if enemy.initial_pos in dead_enemy_positions:
                    enemy.alive = False
                    enemy.hp = 0
        
        # Restore enemies_defeated count for clear conditions
        if 'enemies_defeated' in self.checkpoint_data:
            self.clear_conditions.enemies_defeated = self.checkpoint_data['enemies_defeated']
        
        # Restore collected items (convert lists back to tuples for hashing)
        collected_coin_positions = set(tuple(pos) if isinstance(pos, list) else pos 
                                       for pos in self.checkpoint_data.get('collected_coins', []))
        for coin in self.coins:
            if hasattr(coin, 'initial_pos'):
                coin.collected = coin.initial_pos in collected_coin_positions
        
        collected_star_positions = set(tuple(pos) if isinstance(pos, list) else pos 
                                       for pos in self.checkpoint_data.get('collected_stars', []))
        for star in self.stars:
            if hasattr(star, 'initial_pos'):
                star.collected = star.initial_pos in collected_star_positions
        
        collected_powerup_positions = set(tuple(pos) if isinstance(pos, list) else pos 
                                          for pos in self.checkpoint_data.get('collected_powerups', []))
        for powerup in self.powerups:
            if hasattr(powerup, 'initial_pos'):
                powerup.collected = powerup.initial_pos in collected_powerup_positions
        
        collected_storm_positions = set(tuple(pos) if isinstance(pos, list) else pos 
                                        for pos in self.checkpoint_data.get('collected_storms', []))
        for storm in self.storms:
            if hasattr(storm, 'initial_pos'):
                storm.collected = storm.initial_pos in collected_storm_positions
        
        # Restore broken blocks (convert lists back to tuples for hashing)
        broken_block_positions = set(tuple(pos) if isinstance(pos, list) else pos 
                                     for pos in self.checkpoint_data.get('broken_blocks', []))
        for block in self.breakables:
            if hasattr(block, 'initial_pos'):
                block.broken = block.initial_pos in broken_block_positions
        
        # Restore button/gate states (convert string keys back to tuples if needed)
        button_states_raw = self.checkpoint_data.get('button_states', {})
        button_states = {}
        for key, value in button_states_raw.items():
            # Convert string representation back to tuple if needed
            if isinstance(key, str):
                # JSON converts tuple keys to strings like "[x, y]"
                import ast
                try:
                    key = tuple(ast.literal_eval(key))
                except:
                    pass
            elif isinstance(key, list):
                key = tuple(key)
            button_states[key] = value
        
        for button in self.buttons:
            if hasattr(button, 'initial_pos') and button.initial_pos in button_states:
                button.pressed = button_states[button.initial_pos]
        
        gate_states_raw = self.checkpoint_data.get('gate_states', {})
        gate_states = {}
        for key, value in gate_states_raw.items():
            if isinstance(key, str):
                import ast
                try:
                    key = tuple(ast.literal_eval(key))
                except:
                    pass
            elif isinstance(key, list):
                key = tuple(key)
            gate_states[key] = value
        
        for gate in self.gates:
            if hasattr(gate, 'initial_pos') and gate.initial_pos in gate_states:
                gate.open = gate_states[gate.initial_pos]
        
        # Restore boss state
        boss_state = self.checkpoint_data.get('boss_state')
        if self.boss and boss_state:
            self.boss.hp = boss_state.get('hp', self.boss.hp)
            self.boss.defeated = boss_state.get('defeated', False)
            self.boss.phase = boss_state.get('phase', 'spin_up')
            self.boss.alive = boss_state.get('alive', True)
            self.boss_door_open = boss_state.get('defeated', False)
        
        # Restore game time if available
        if 'game_time' in self.checkpoint_data:
            # Note: Stopwatch doesn't have a direct set method, would need to add one
            pass
    
    def _capture_checkpoint_state(self):
        """Capture current game state when checkpoint is activated"""
        print("DEBUG: Capturing checkpoint state...")
        # Capture dead enemies by their initial positions
        dead_enemies = []
        for enemy in self.enemies:
            if not enemy.alive:
                dead_enemies.append(enemy.initial_pos)
        print(f"DEBUG: Dead enemies: {len(dead_enemies)}")
        
        # Capture collected items by their initial positions
        collected_coins = [coin.initial_pos for coin in self.coins if coin.collected and hasattr(coin, 'initial_pos')]
        collected_stars = [star.initial_pos for star in self.stars if star.collected and hasattr(star, 'initial_pos')]
        collected_powerups = [powerup.initial_pos for powerup in self.powerups if powerup.collected and hasattr(powerup, 'initial_pos')]
        collected_storms = [storm.initial_pos for storm in self.storms if storm.collected and hasattr(storm, 'initial_pos')]
        print(f"DEBUG: Collected coins: {len(collected_coins)}, stars: {len(collected_stars)}, powerups: {len(collected_powerups)}, storms: {len(collected_storms)}")
        
        # Capture broken blocks
        broken_blocks = [block.initial_pos for block in self.breakables if block.broken]
        
        # Capture button/gate states (convert tuple keys to strings for JSON compatibility)
        button_states = {str(btn.initial_pos): btn.pressed for btn in self.buttons}
        gate_states = {str(gate.initial_pos): gate.open for gate in self.gates}
        
        # Capture boss state if exists
        boss_state = None
        if self.boss:
            boss_state = {
                'hp': self.boss.hp,
                'defeated': self.boss.defeated,
                'phase': self.boss.phase,
                'alive': self.boss.alive
            }
        
        # Capture player state
        player_state = {
            'hp': self.player.hp,
            'coins': self.player.coins,
            'double_shot': self.player.double_shot,
            'stamina_boost': self.player.stamina_boost,
            'max_stamina': self.player.max_stamina,
            'checkpoint_pos': self.player.checkpoint_pos,
            'checkpoint_coins': self.player.checkpoint_coins,
            'last_hp_bonus_at': self.player.last_hp_bonus_at
        }
        
        # Store all state in checkpoint_data
        self.checkpoint_data = {
            'player': player_state,
            'dead_enemies': dead_enemies,
            'collected_coins': collected_coins,
            'collected_stars': collected_stars,
            'collected_powerups': collected_powerups,
            'collected_storms': collected_storms,
            'broken_blocks': broken_blocks,
            'button_states': button_states,
            'gate_states': gate_states,
            'boss_state': boss_state,
            'game_time': self.stopwatch.get_time(),
            'enemies_defeated': self.clear_conditions.enemies_defeated
        }
    
    def _activate_storm_effect(self):
        """Activate storm effect - clear enemies in large radius"""
        print("Storm effect activated!")  # Debug output
        
        # Add visual flash effect
        self.storm_flash_timer = 0.5  # Flash for 0.5 seconds
        
        # Calculate storm radius - INCREASED to 50% of screen height for better effect
        storm_radius = int(settings.SCREEN_HEIGHT * 0.5)  # 360 pixels (was 144)
        print(f"Storm radius: {storm_radius} pixels")  # Debug output
        
        # Get player position
        player_center = self.player.rect.center
        print(f"Player position: {player_center}")  # Debug output
        
        # Debug: Show all enemies and their distances
        print(f"Total enemies: {len(self.enemies)}")
        for i, enemy in enumerate(self.enemies):
            if enemy.alive:
                enemy_center = enemy.rect.center
                distance = ((player_center[0] - enemy_center[0]) ** 2 + 
                           (player_center[1] - enemy_center[1]) ** 2) ** 0.5
                print(f"Enemy {i}: pos={enemy_center}, distance={distance:.1f}, within_radius={distance <= storm_radius}")
        
        # Clear enemies within storm radius
        enemies_cleared = 0
        for enemy in self.enemies[:]:  # Use slice to avoid modification during iteration
            if enemy.alive:
                # Calculate distance from player to enemy
                enemy_center = enemy.rect.center
                distance = ((player_center[0] - enemy_center[0]) ** 2 + 
                           (player_center[1] - enemy_center[1]) ** 2) ** 0.5
                
                if distance <= storm_radius:
                    # Enemy is within storm radius - defeat it
                    print(f"Clearing enemy at distance {distance:.1f}")  # Debug output
                    enemy.alive = False
                    enemies_cleared += 1
                    self.clear_conditions.defeat_enemy()
        
        # Visual feedback - could add screen flash or particles here
        print(f"Storm cleared {enemies_cleared} enemies!")
