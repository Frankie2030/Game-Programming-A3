"""
Level state - main gameplay
"""
import pygame
from game.core import GameState, settings, Stopwatch
from game.core.clear_conditions import ClearConditions
from game.world.camera import Camera
from game.world.collisions import CollisionSystem
from game.world.checkpoints import Checkpoint
from game.entities.player import Player
from game.entities.coin import Coin
from game.entities.star import FluxStar
from game.entities.powerup import PowerUp
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
    
    def __init__(self, stack):
        super().__init__(stack)
        
        # Load level
        level_path = "game/assets/levels/level1.json"
        level_data = LevelLoader.load_from_json(level_path)
        
        # Set up systems
        self.collision_system = CollisionSystem(level_data['tile_map'])
        self.tile_map = level_data['tile_map']
        self.camera = Camera(settings.WORLD_WIDTH, settings.WORLD_HEIGHT)
        self.input_handler = InputHandler()
        self.hud = HUD()
        self.stopwatch = Stopwatch()
        
        # Audio
        self.audio = stack.persistent_data.get('audio')
        
        # Spawn player
        self.player = Player(level_data['spawn_x'], level_data['spawn_y'], self.audio)
        
        # Spawn coins
        self.coins = []
        for pos in level_data['coins']:
            self.coins.append(Coin(pos[0], pos[1]))
        
        # Spawn stars
        self.stars = []
        for pos in level_data['stars']:
            self.stars.append(FluxStar(pos[0], pos[1]))
        
        # Spawn power-ups
        self.powerups = []
        for pdata in level_data.get('powerups', []):
            self.powerups.append(PowerUp(pdata['x'], pdata['y'], pdata['type']))
        
        # Spawn spikes
        self.spikes = []
        for sdata in level_data.get('spikes', []):
            self.spikes.append(Spikes(sdata['x'], sdata['y'], sdata['orientation']))
        
        # Spawn breakable blocks
        self.breakables = []
        for bdata in level_data.get('breakables', []):
            self.breakables.append(BreakableBlock(bdata['x'], bdata['y'], bdata['contents']))
        
        # Spawn checkpoints
        self.checkpoints = []
        for pos in level_data['checkpoints']:
            self.checkpoints.append(Checkpoint(pos[0], pos[1]))
        
        # Spawn enemies
        self.enemies = []
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
        
        # Bullets
        self.bullets = []
        
        # Debug mode
        self.show_hitboxes = False
        
        # Clear conditions tracking
        self.clear_conditions = ClearConditions(len(self.enemies))
        
        # Start timer
        self.stopwatch.start()
        
        # Start background music
        if self.audio:
            self.audio.play_music('game/assets/audio/bgm/space-trip-114102.mp3')
    
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
        
        # Spawn bullet if player is attacking
        if self.player.should_spawn_bullet():
            x, y = self.player.get_bullet_spawn_pos()
            direction = 1 if self.player.facing_right else -1
            bullet = Bullet(x, y, direction, self.player.bullet_frames)
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
        self.camera.update(self.player.rect)
        
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
            if spike.check_collision(self.player.rect, self.player.gravity_dir):
                if not self.player.is_invulnerable():
                    if self.player.take_damage():
                        if self.audio:
                            self.audio.play_sfx('hit')
        
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
                        if self.player.take_damage():
                            if self.audio:
                                self.audio.play_sfx('hit')
        
        # Update boss
        if self.player.rect.right > self.boss.rect.left - 200:
            self.boss_active = True
        
        if self.boss_active:
            self.boss.update(dt)
            
            # Check if boss lasers hit player
            if self.boss.check_hit_player(self.player.rect, self.player.is_invulnerable()):
                if self.player.take_damage():
                    if self.audio:
                        self.audio.play_sfx('hit')
            
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
        if self.boss_door_open and self.player.rect.x > settings.WORLD_WIDTH - 100:
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
        screen.fill((20, 20, 30))  # Dark blue background
        
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
        
        # Draw HUD
        boss_to_draw = self.boss if self.boss_active else None
        self.hud.draw(screen, self.player, boss=boss_to_draw, show_fps=True, 
                     fps=self.stack.persistent_data.get('fps', 60), show_hitboxes=self.show_hitboxes,
                     clear_conditions=self.clear_conditions, game_time=self.stopwatch.get_time())
