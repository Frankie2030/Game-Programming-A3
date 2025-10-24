"""
Core game settings and constants
"""
import pygame

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Gravity Courier"

# Tile system
TILE_SIZE = 32  # px
WORLD_WIDTH = 5120  # px (160 tiles)
WORLD_HEIGHT = 720  # px (22.5 tiles, round to 23)

# Physics
GRAVITY = 1400  # px/s²
PLAYER_RUN_SPEED = 180  # px/s
PLAYER_BOOST_SPEED = 230  # px/s (with Flux Surge)
PLAYER_JUMP_IMPULSE = 520  # px/s
GRAVITY_FLIP_COOLDOWN = 0.25  # seconds

# Player
PLAYER_HP = 5
PLAYER_INVULN_TIME = 1.5  # seconds after hit
COYOTE_TIME = 0.15  # seconds
JUMP_BUFFER_TIME = 0.1  # seconds

# Power-ups
FLUX_SURGE_DURATION = 15.0  # seconds
POWERUP_INVULN_DURATION = 15.0  # seconds

# Stamina System
STAMINA_MAX_TIME = 5.0  # seconds from full to empty
STAMINA_DRAIN_RATE = 1.0 / STAMINA_MAX_TIME  # 1.0 / seconds (20% per second)
STAMINA_REGEN_RATE = 3.0
STAMINA_POWERUP_MULTIPLIER = 2.0  # 2x faster regeneration with powerup

# Boss
BOSS_HP = 10
BOSS_PATTERN_DURATION = 10.0  # seconds
BOSS_WEAK_WINDOW = 2.0  # seconds
BOSS_TELEGRAPH_TIME = 1.5  # seconds

# Camera
CAMERA_SMOOTHING = 0.1  # lerp factor (lower = smoother)
CAMERA_SHAKE_INTENSITY = 18.0  # pixels (increased for visibility)
CAMERA_SHAKE_DURATION = 0.35  # seconds
CAMERA_SHAKE_FREQUENCY = 18.0  # Hz

# Background
BACKGROUND_PARALLAX_SPEEDS = [0.2, 0.5, 0.8]  # Back, middle, front layer speeds
BACKGROUND_SCROLL_ENABLED = True

# Colors (R, G, B)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (220, 50, 50)
COLOR_GREEN = (50, 220, 50)
COLOR_BLUE = (50, 120, 220)
COLOR_YELLOW = (255, 220, 50)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)

# Clear Conditions
TIME_LIMIT_3_STAR = 120.0  # seconds for 3-star completion

# UI
UI_FONT_SIZE = 24
UI_TITLE_SIZE = 48

# Minimap
MINIMAP_WIDTH = 220  # px
MINIMAP_HEIGHT = 120  # px
MINIMAP_MARGIN = 12  # px from screen edges
MINIMAP_PADDING = 8   # px inner padding
MINIMAP_BG_COLOR = (18, 18, 22, 230)  # RGBA more opaque for readability
MINIMAP_BORDER_COLOR = (210, 210, 210)
MINIMAP_SHADOW_COLOR = (0, 0, 0, 120)
MINIMAP_BORDER_RADIUS = 8
MINIMAP_GRID_COLOR = (80, 80, 90)
MINIMAP_VIEWPORT_COLOR = (180, 180, 255)
MINIMAP_PLAYER_COLOR = (255, 230, 50)

# Default key bindings
DEFAULT_KEY_BINDINGS = {
    'move_left': [pygame.K_a, pygame.K_LEFT],
    'move_right': [pygame.K_d, pygame.K_RIGHT],
    'move_up': [pygame.K_w, pygame.K_UP],
    'float': [pygame.K_e, pygame.K_LSHIFT, pygame.K_RSHIFT],
    'shoot': [pygame.K_SPACE, pygame.K_j, pygame.K_x, pygame.K_LCTRL, pygame.K_RCTRL],
}
