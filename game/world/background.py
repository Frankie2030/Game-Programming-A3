"""
Proper city skyline background system with transparency support
"""
import pygame
import os
from game.core import settings


class ParallaxBackground:
    """Background system that properly handles transparent city skyline images"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        print(f"Creating transparent city skyline background: {screen_width}x{screen_height}")
        
        # Create a dark sky background
        self.sky_surface = pygame.Surface((screen_width, screen_height))
        # Dark blue-purple sky gradient
        for y in range(screen_height):
            r = int(20 + (y / screen_height) * 30)
            g = int(10 + (y / screen_height) * 20)
            b = int(40 + (y / screen_height) * 60)
            color = (r, g, b)
            pygame.draw.line(self.sky_surface, color, (0, y), (screen_width, y))
        
        # Load the actual city skyline images with proper transparency
        self.layers = []
        self._load_transparent_images()
        
        print(f"Background ready with {len(self.layers)} transparent layers")
    
    def _load_transparent_images(self):
        """Load city skyline images with proper transparency handling"""
        layer_paths = [
            "game/assets/images/bg/Layers/back.png",
            "game/assets/images/bg/Layers/buildings.png", 
            "game/assets/images/bg/Layers/front.png"
        ]
        
        speeds = [0.2, 0.5, 0.8]  # Back, middle, front
        
        for i, (path, speed) in enumerate(zip(layer_paths, speeds)):
            try:
                print(f"Loading transparent layer {i+1}: {path}")
                
                # Load with alpha channel preserved
                image = pygame.image.load(path).convert_alpha()
                print(f"Original: {image.get_size()}")
                
                # Scale to fit screen height, maintain aspect ratio
                scale_factor = self.screen_height / image.get_height()
                new_width = int(image.get_width() * scale_factor)
                new_height = int(image.get_height() * scale_factor)
                
                # Scale the image while preserving transparency
                scaled_image = pygame.transform.scale(image, (new_width, new_height))
                
                # Make the layer more dim by reducing opacity
                scaled_image = scaled_image.copy()
                scaled_image.set_alpha(100)  # 0-255, lower = more dim
                print(f"Scaled: {scaled_image.get_size()}")
                
                # Ensure the image is wide enough for seamless scrolling
                if new_width < self.screen_width * 2:
                    # Create a wider version by repeating the image
                    repeat_count = (self.screen_width * 2) // new_width + 1
                    wide_surface = pygame.Surface((new_width * repeat_count, new_height), pygame.SRCALPHA)
                    for j in range(repeat_count):
                        wide_surface.blit(scaled_image, (j * new_width, 0))
                    scaled_image = wide_surface
                    new_width = scaled_image.get_width()
                
                layer = {
                    'image': scaled_image,
                    'width': new_width,
                    'height': new_height,
                    'speed': speed,
                    'x': 0
                }
                
                self.layers.append(layer)
                print(f"Transparent layer {i+1} loaded: {new_width}x{new_height}, speed={speed}")
                
            except Exception as e:
                print(f"Error loading {path}: {e}")
                # Create a visible fallback with transparency
                fallback = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
                colors = [(100, 50, 50, 200), (50, 100, 50, 200), (50, 50, 100, 200)]
                fallback.fill(colors[i] if i < len(colors) else (100, 100, 100, 200))
                
                layer = {
                    'image': fallback,
                    'width': self.screen_width * 2,
                    'height': self.screen_height,
                    'speed': speed,
                    'x': 0
                }
                self.layers.append(layer)
                print(f"Created transparent fallback layer {i+1}")
    
    def update(self, camera_x):
        """Update parallax positions"""
        for layer in self.layers:
            layer['x'] = -camera_x * layer['speed']
    
    def draw(self, screen):
        """Draw background with proper transparent layering"""
        # Draw sky background first
        screen.blit(self.sky_surface, (0, 0))
        
        # Draw city skyline layers in order (back to front)
        for i, layer in enumerate(self.layers):
            # Calculate how many copies we need to cover the screen
            start_x = layer['x'] % layer['width']
            if start_x > 0:
                start_x -= layer['width']
            
            # Draw all copies needed to cover the screen
            x = start_x
            while x < self.screen_width:
                screen.blit(layer['image'], (x, 0))
                x += layer['width']
        
        # Removed debug overlay text