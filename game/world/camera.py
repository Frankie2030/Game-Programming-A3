"""
Camera system with follow and clamping
"""
import math
import random
from game.core import settings, lerp, clamp, Timer


class Camera:
    """2D camera with horizontal follow and shake effects"""
    
    def __init__(self, world_width, world_height):
        # Base (non-shaken) camera position
        self._x = 0
        self._y = 0
        self.world_width = world_width
        self.world_height = world_height
        self.target_x = 0
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT
        
        # Camera shake system
        self.shake_timer = Timer()
        self.shake_intensity = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
    
    @property
    def x(self):
        """Public camera x including shake offset."""
        return self._x + self.shake_offset_x
    
    @x.setter
    def x(self, value):
        self._x = value
    
    @property
    def y(self):
        """Public camera y including shake offset."""
        return self._y + self.shake_offset_y
    
    @y.setter
    def y(self, value):
        self._y = value
    
    def update(self, target_rect, dt=None):
        """Update camera to follow target"""
        if dt is None:
            dt = 1.0 / 60.0  # Default to 60 FPS if not provided
            
        # Update shake timer
        self.shake_timer.update(dt)
        
        # Update shake effect
        if self.shake_timer.is_active():
            # Calculate shake intensity (decreases over time)
            shake_progress = 1.0 - (self.shake_timer.time_left / settings.CAMERA_SHAKE_DURATION)
            current_intensity = self.shake_intensity * (1.0 - shake_progress)
            
            # Generate shake offset using sine waves for smooth motion
            time = settings.CAMERA_SHAKE_DURATION - self.shake_timer.time_left
            self.shake_offset_x = math.sin(time * settings.CAMERA_SHAKE_FREQUENCY * 2 * math.pi) * current_intensity
            self.shake_offset_y = math.cos(time * settings.CAMERA_SHAKE_FREQUENCY * 2 * math.pi) * current_intensity
            
            # Debug output (only print occasionally to avoid spam)
            if int(time * 60) % 10 == 0:  # Print every 10 frames
                print(f"DEBUG: Shake active - offset_x={self.shake_offset_x:.2f}, offset_y={self.shake_offset_y:.2f}")
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
        
        # Target camera position (center on target horizontally)
        self.target_x = target_rect.centerx - self.screen_width // 2
        
        # Smooth lerp (operate on base position)
        self._x = lerp(self._x, self.target_x, settings.CAMERA_SMOOTHING)
        
        # Clamp to world bounds
        self._x = clamp(self._x, 0, max(0, self.world_width - self.screen_width))
        
        # No vertical scrolling
        self._y = 0
    
    def apply(self, rect):
        """Apply camera offset to a rect"""
        new_rect = rect.copy()
        new_rect.x -= self.x
        new_rect.y -= self.y
        return new_rect
    
    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        return x - self.x, y - self.y
    
    def screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates"""
        return x + self.x, y + self.y
    
    def shake(self, intensity=None, duration=None):
        """Trigger camera shake effect"""
        if intensity is None:
            intensity = settings.CAMERA_SHAKE_INTENSITY
        if duration is None:
            duration = settings.CAMERA_SHAKE_DURATION
            
        print(f"DEBUG: Camera shake called with intensity={intensity}, duration={duration}")
        self.shake_intensity = intensity
        self.shake_timer.start(duration)
        print(f"DEBUG: Shake timer active: {self.shake_timer.is_active()}")
