"""
Audio management system
"""
import pygame
import os


class AudioManager:
    """Manages BGM and SFX playback"""
    
    def __init__(self):
        pygame.mixer.init()
        
        # Volume settings (0.0 to 1.0)
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
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
