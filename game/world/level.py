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
from game.io.input import InputHandler
from game.io.level_loader import LevelLoader
from game.ui.hud import HUD


class LevelState(GameState):
    """Main gameplay state"""
    
    def __init__(self, stack, save_data=None):
        super().__init__(stack)
        
        # Load level
        level_path = "game/assets/levels/level1.json"
        level_data = LevelLoader.load_from_json(level_path)
        
        # Set up systems
        self.collision_system = CollisionSystem(level_data['tile_map'])
        self.tile_map = level_data['tile_map']
        self.camera = Camera(settings.WORLD_WIDTH, settings.WORLD_HEIGHT)
        self.background = ParallaxBackground(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.input_handler = InputHandler()
        self.hud = HUD()
        self.stopwatch = Stopwatch()
        # Low-health effect timer
        self.low_health_flash_timer = 0.0
        
        # Audio
        self.audio = stack.persistent_data.get('audio')
        
        # Spawn player (use save data if available)
        if save_data:
            player_data = save_data.get('player', {})
            spawn_x = player_data.get('x', level_data['spawn_x'])
            spawn_y = player_data.get('y', level_data['spawn_y'])
            self.player = Player(spawn_x, spawn_y, self.audio)
            # Restore player state
            self.player.hp = player_data.get('hp', 3)
            self.player.coins = player_data.get('coins', 0)
            checkpoint_x = player_data.get('checkpoint_x', spawn_x)
            checkpoint_y = player_data.get('checkpoint_y', spawn_y)
            self.player.checkpoint_pos = (checkpoint_x, checkpoint_y)
            self.player.gravity_dir = player_data.get('gravity_dir', 1)
            self.player.stamina = player_data.get('stamina', 1.0)
            self.player.powered_up = player_data.get('powered_up', False)
            # Restore game time
            self.stopwatch.set_time(save_data.get('progress', {}).get('game_time', 0))
        else:
            self.player = Player(level_data['spawn_x'], level_data['spawn_y'], self.audio)
        
        # Spawn coins
        self.coins = []
        if save_data and 'entities' in save_data and 'coins' in save_data['entities']:
            # Restore coins from save
            for coin_data in save_data['entities']['coins']:
                coin = Coin(coin_data['x'], coin_data['y'])
                coin.collected = coin_data.get('collected', False)
                self.coins.append(coin)
        else:
            # Spawn fresh coins
            for pos in level_data['coins']:
                self.coins.append(Coin(pos[0], pos[1]))
        
        # Spawn stars
        self.stars = []
        if save_data and 'entities' in save_data and 'stars' in save_data['entities']:
            # Restore stars from save
            for star_data in save_data['entities']['stars']:
                star = FluxStar(star_data['x'], star_data['y'])
                star.collected = star_data.get('collected', False)
                self.stars.append(star)
        else:
            # Spawn fresh stars
            for pos in level_data['stars']:
                self.stars.append(FluxStar(pos[0], pos[1]))
        
        # Spawn power-ups
        self.powerups = []
        if save_data and 'entities' in save_data and 'powerups' in save_data['entities']:
            # Restore power-ups from save
            for pdata in save_data['entities']['powerups']:
                powerup = PowerUp(pdata['x'], pdata['y'], pdata.get('type', 'speed'))
                powerup.collected = pdata.get('collected', False)
                self.powerups.append(powerup)
        else:
            # Spawn fresh power-ups
            for pdata in level_data.get('powerups', []):
                self.powerups.append(PowerUp(pdata['x'], pdata['y'], pdata['type']))
        
        # Spawn storm powerups
        self.storms = []
        if save_data and 'entities' in save_data and 'storms' in save_data['entities']:
            # Restore storms from save
            for storm_data in save_data['entities']['storms']:
                storm = StormPowerup(storm_data['x'], storm_data['y'])
                storm.collected = storm_data.get('collected', False)
                self.storms.append(storm)
        else:
            # Spawn fresh storms
            for pos in level_data.get('storms', []):
                print(f"Loading storm at position: {pos}")  # Debug output
                self.storms.append(StormPowerup(pos[0], pos[1]))
        
        print(f"Total storms loaded: {len(self.storms)}")  # Debug output
        
        # Spawn spikes
        self.spikes = []
        for sdata in level_data.get('spikes', []):
            self.spikes.append(Spikes(sdata['x'], sdata['y'], sdata['orientation']))
        
        # Spawn breakable blocks
        self.breakables = []
        if save_data and 'entities' in save_data and 'breakables' in save_data['entities']:
            # Restore breakables from save
            for bdata in save_data['entities']['breakables']:
                block = BreakableBlock(bdata['x'], bdata['y'], bdata.get('contents'))
                block.broken = bdata.get('broken', False)
                self.breakables.append(block)
        else:
            # Spawn fresh breakables
            for bdata in level_data.get('breakables', []):
                self.breakables.append(BreakableBlock(bdata['x'], bdata['y'], bdata['contents']))
        
        # Spawn checkpoints
        self.checkpoints = []
        for pos in level_data['checkpoints']:
            self.checkpoints.append(Checkpoint(pos[0], pos[1]))
        
        # Spawn enemies
        self.enemies = []
        if save_data and 'entities' in save_data and 'enemies' in save_data['entities']:
            # Restore enemies from save
            for i, enemy_data in enumerate(level_data['enemies']):
                if enemy_data['type'] == 'drone':
                    color = enemy_data.get('color', 'blue')
                    drone = Drone(enemy_data['x'], enemy_data['y'],
                                enemy_data['anchor'], enemy_data['range'], color)
                    # Restore enemy state if available
                    if i < len(save_data['entities']['enemies']):
                        saved_enemy = save_data['entities']['enemies'][i]
                        drone.alive = saved_enemy.get('alive', True)
                    self.enemies.append(drone)
        else:
            # Spawn fresh enemies
            for enemy_data in level_data['enemies']:
                if enemy_data['type'] == 'drone':
                    color = enemy_data.get('color', 'blue')
                    drone = Drone(enemy_data['x'], enemy_data['y'],
                                enemy_data['anchor'], enemy_data['range'], color)
                    self.enemies.append(drone)
        
        # Spawn boss
        self.boss = GyroBoss(level_data['boss_x'], level_data['boss_y'])
        self.boss_active = False
        self.boss_door_open = False
        
        # Restore boss state if loading from save
        if save_data and 'boss' in save_data:
            boss_data = save_data['boss']
            self.boss.hp = boss_data.get('hp', 8)
            self.boss.max_hp = boss_data.get('max_hp', 8)
            self.boss.alive = boss_data.get('alive', True)
            self.boss.defeated = boss_data.get('defeated', False)
            self.boss.phase = boss_data.get('phase', 'spin_up')
            self.boss.vulnerable = boss_data.get('vulnerable', False)
            self.boss_active = boss_data.get('boss_active', False)
            self.boss_door_open = boss_data.get('boss_door_open', False)
        
        # Bullets
        self.bullets = []
        
        # Debug mode
        self.show_hitboxes = False
        
        # Clear conditions tracking
        self.clear_conditions = ClearConditions(len(self.enemies))
        
        # Restore clear conditions if loading from save
        if save_data:
            progress_data = save_data.get('progress', {})
            enemies_defeated = progress_data.get('enemies_defeated', 0)
            for _ in range(enemies_defeated):
                self.clear_conditions.defeat_enemy()
        
        # Start timer
        self.stopwatch.start()
        
        # Start background music
        if self.audio:
            self.audio.play_music('game/assets/public-assets/music/cyberpunk-street.ogg')
    
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
            
            # Check if P powerup is active for triple bullets
            if self.player.is_powerup_active():
                # Spawn 3 bullets: center, up, down with more spacing
                bullets_to_spawn = [
                    (x, y, direction),  # Center bullet
                    (x, y - 16, direction),  # Upper bullet (increased from 8 to 16)
                    (x, y + 16, direction)   # Lower bullet (increased from 8 to 16)
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
                
                # Check bullet hits boss
                if self.boss_active and self.boss.vulnerable and bullet.rect.colliderect(self.boss.rect):
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
                self.player.collect_coin()
                if self.audio:
                    self.audio.play_sfx('coin')
        
        # Update stars
        for star in self.stars:
            if star.update(dt, self.player.rect):
                self.player.activate_flux_surge()
                if self.audio:
                    self.audio.play_sfx('star')
        
        # Update power-ups
        for powerup in self.powerups:
            if powerup.update(dt, self.player.rect):
                self.player.activate_powerup()
                if self.audio:
                    self.audio.play_sfx('powerup')
        
        # Update storm powerups
        for storm in self.storms:
            if storm.update(dt, self.player.rect):
                print("Storm powerup collected!")  # Debug output
                self._activate_storm_effect()
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
                        self.coins.append(Coin(block.rect.centerx - 8, block.rect.top - 20))
                    elif item == 'powerup':
                        # Spawn power-up above block
                        self.powerups.append(PowerUp(block.rect.centerx - 12, block.rect.top - 30))
        
        # Check spike collisions
        for spike in self.spikes:
            if spike.check_collision(self.player.rect, self.player.gravity_dir, self.stopwatch.get_time()):
                if not self.player.is_invulnerable():
                    previous_hp = self.player.hp
                    if self.player.take_damage(camera=self.camera):
                        if self.audio:
                            self.audio.play_sfx('hit')
                        # Trigger low-health overlay when dropping to 1 HP
                        if previous_hp >= 2 and self.player.hp == 1:
                            self.low_health_flash_timer = 0.35
        
        # Check if player is stuck on spikes (apply movement restrictions)
        player_stuck_on_spikes = False
        for spike in self.spikes:
            if spike.is_player_stuck(self.player.rect, self.player.gravity_dir):
                player_stuck_on_spikes = True
                break
        
        # Apply sticky behavior - reduce movement speed when stuck on spikes
        if player_stuck_on_spikes:
            # Reduce horizontal movement speed significantly
            self.player.vel_x *= 0.1  # Only 10% of normal speed
            # Prevent jumping when stuck (make it harder to escape)
            if self.player.vel_y < 0:  # If trying to jump
                self.player.vel_y *= 0.3  # Reduce jump power
        
        # Update checkpoints
        for checkpoint in self.checkpoints:
            if checkpoint.update(dt, self.player.rect):
                # Set checkpoint to middle of checkpoint position
                self.player.set_checkpoint((checkpoint.rect.centerx - self.player.rect.width // 2, 
                                           checkpoint.rect.bottom - self.player.rect.height))
                if self.audio:
                    self.audio.play_sfx('checkpoint')
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.collision_system)
            
            # Check collision with player
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                # Check stomp first
                if enemy.check_stomp(self.player):
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
        
        # Update boss
        if self.player.rect.right > self.boss.rect.left - 200:
            self.boss_active = True
        
        if self.boss_active:
            self.boss.update(dt)
            
            # Check if boss lasers hit player
            if self.boss.check_hit_player(self.player.rect, self.player.is_invulnerable()):
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
        
        # Check win condition
        if self.boss_door_open and self.boss.defeated and self.player.rect.x > settings.WORLD_WIDTH - 100:
            from game.ui.win import WinState
            self.clear_conditions.set_completion_time(self.stopwatch.get_time())
            self.stack.replace(WinState, 
                             coins=self.player.coins, 
                             time=self.stopwatch.get_time(),
                             clear_conditions=self.clear_conditions)
            return
        
        # Check lose condition
        if not self.player.alive:
            # Show lose screen, but respawn at checkpoint when retry
            from game.ui.lose import LoseState
            self.stack.push(LoseState)  # Push instead of replace
            # Respawn player for when they return
            self.player.respawn()
            # Reset input states so keys aren't stuck
            self.input_handler.reset_movement_inputs()
            # Update camera to player position
            self.camera.x = self.player.rect.centerx - settings.SCREEN_WIDTH // 2
            self.camera.x = max(0, min(self.camera.x, settings.WORLD_WIDTH - settings.SCREEN_WIDTH))
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
            spike.draw(screen, self.camera)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera)
            # Draw hitbox if debug mode
            if self.show_hitboxes:
                debug_rect = enemy.rect.copy()
                debug_rect.x -= self.camera.x
                debug_rect.y -= self.camera.y
                pygame.draw.rect(screen, (255, 0, 255), debug_rect, 2)
        
        # Draw boss
        if self.boss_active:
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
                     minimap_entities=minimap_entities)
    
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
