"""
Core game settings and constants
"""

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
PLAYER_HP = 3
PLAYER_INVULN_TIME = 1.5  # seconds after hit
COYOTE_TIME = 0.15  # seconds
JUMP_BUFFER_TIME = 0.1  # seconds

# Power-ups
FLUX_SURGE_DURATION = 7.0  # seconds

# Stamina System
STAMINA_MAX_TIME = 5.0  # seconds from full to empty
STAMINA_DRAIN_RATE = 1.0 / STAMINA_MAX_TIME  # 1.0 / seconds (20% per second)
STAMINA_REGEN_RATE = 3.0
STAMINA_POWERUP_MULTIPLIER = 2.0  # 2x faster regeneration with powerup

# Boss
BOSS_HP = 8
BOSS_PATTERN_DURATION = 10.0  # seconds
BOSS_WEAK_WINDOW = 2.0  # seconds
BOSS_TELEGRAPH_TIME = 1.5  # seconds

# Camera
CAMERA_SMOOTHING = 0.1  # lerp factor (lower = smoother)

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
