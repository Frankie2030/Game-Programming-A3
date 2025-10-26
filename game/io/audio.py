"""
Audio management system
"""
import pygame
import os


class AudioManager:
    """Manages BGM and SFX playback"""
    
    # Music file paths
    MUSIC_MENU = 'game/assets/audio/bgm/space-trip-114102.mp3'
    MUSIC_GAME = 'game/assets/audio/bgm/cyberpunk-street.wav'
    MUSIC_BOSS = 'game/assets/audio/bgm/The Last Encounter Medium Loop.wav'
    
    # SFX file paths
    SFX_BUMP = 'game/assets/audio/sfx/bump.ogg'
    SFX_STOMP = 'game/assets/audio/sfx/stomp.ogg'
    SFX_COIN = 'game/assets/audio/sfx/coin.ogg'
    SFX_POWERUP = 'game/assets/audio/sfx/powerup.ogg'
    SFX_GAME_OVER = 'game/assets/audio/sfx/game-over-39-199830.mp3'
    SFX_DEAD = 'game/assets/audio/sfx/dead-sound.mp3'
    
    def __init__(self):
        pygame.mixer.init()
        
        # Volume settings (0.0 to 1.0)
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # Mute state
        self._is_muted = False
        self._previous_music_volume = self.music_volume
        self._previous_sfx_volume = self.sfx_volume
        
        # Sound effects cache
        self.sfx_cache = {}
        
        # Current music
        self.current_music = None
    
    def load_sfx(self, name, filepath):
        """Load a sound effect"""
        try:
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(self.sfx_volume)
            self.sfx_cache[name] = sound
        except:
            print(f"Warning: Could not load SFX '{name}' from {filepath}")
            # Create a dummy silent sound
            self.sfx_cache[name] = None
    
    def play_sfx(self, name):
        """Play a sound effect"""
        if name in self.sfx_cache and self.sfx_cache[name]:
            self.sfx_cache[name].play()
    
    def play_music(self, filepath, loops=-1):
        """Play background music (loops infinitely by default)"""
        try:
            if self.current_music != filepath:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.current_music = filepath
        except:
            print(f"Warning: Could not load music from {filepath}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_cache.values():
            if sound:
                sound.set_volume(self.sfx_volume)
    
    def get_music_volume(self):
        """Get current music volume"""
        return self.music_volume
    
    def get_sfx_volume(self):
        """Get current SFX volume"""
        return self.sfx_volume
    
    def load_all_audio(self):
        """Pre-load all necessary music and SFX at game startup"""
        # Load SFX
        self.load_sfx('bump', self.SFX_BUMP)
        self.load_sfx('stomp', self.SFX_STOMP)
        self.load_sfx('coin', self.SFX_COIN)
        self.load_sfx('powerup', self.SFX_POWERUP)
        self.load_sfx('game_over', self.SFX_GAME_OVER)
        self.load_sfx('dead-sound', self.SFX_DEAD)
        
        # Load placeholder SFX for sounds we don't have files for yet
        placeholder_sfx = ['jump', 'gravity_flip', 'hit', 'enemy_defeat', 
                          'boss_hit', 'star', 'checkpoint', 'pause', 'confirm']
        for sfx in placeholder_sfx:
            self.sfx_cache[sfx] = None  # Placeholder
    
    def stop_all_audio(self):
        """Stop all audio (music and SFX)"""
        self.stop_music()
        # Stop all SFX channels
        pygame.mixer.stop()
    
    def toggle_mute(self):
        """Toggle mute state for all audio"""
        if self._is_muted:
            # Unmute: restore previous volumes
            self.music_volume = self._previous_music_volume
            self.sfx_volume = self._previous_sfx_volume
            self._is_muted = False
        else:
            # Mute: store current volumes and set to 0
            self._previous_music_volume = self.music_volume
            self._previous_sfx_volume = self.sfx_volume
            self.music_volume = 0.0
            self.sfx_volume = 0.0
            self._is_muted = True
        
        # Apply volume changes
        pygame.mixer.music.set_volume(self.music_volume)
        for sound in self.sfx_cache.values():
            if sound:
                sound.set_volume(self.sfx_volume)
    
    def is_muted(self):
        """Check if audio is currently muted"""
        return self._is_muted
