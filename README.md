# Gravity Courier

A gravity-flipping platformer set in a rotating space station where you play as a courier navigating through hazardous environments using unique gravity manipulation abilities. Master the art of floating in space while managing your stamina and completing objectives under time pressure.

## Theme

Gravity Courier takes place aboard a malfunctioning space station where gravity systems have gone haywire. As a specialized courier, you must deliver critical data canisters while battling hostile security drones and ultimately confronting the station's corrupted central processing unit, the Gyro-Core boss. The game combines precision platforming with strategic resource management through its innovative stamina system.

## Setup and Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation Steps
1. Clone or download the game files
2. Navigate to the game directory
3. Install required dependencies:
```bash
pip install -r game/requirements.txt
```

### Running the Game
From A3/ directory, run:
```bash
python -m game.main
```
or:
```bash
python run.py
```

## Controls

### Interface
- **ESC**: Pause game / Back to Previous Menu
- **B**: Toggle debug mode (hitbox visualization)
- **Enter**: Confirm selections in menus

## How to Play

### Basic Mechanics
1. **Movement**: Use standard platforming controls to navigate the station (**WASD**).
2. **Gravity Flip**: Press E to reverse your gravity, allowing you to walk on ceilings and floating in space. When floating (not touching ground or ceiling), you drain stamina. Your stamina bar appears when floating or regenerating. When the stamina is fully drained, you will not be able to float until it has been fully recharged.
3. **Weapons**: Press Space to shoot the enemies with outerspace bullets.

**Note**: The keys are remappable to your customization.

### Combat System
- **Enemy Elimination**: Stomp on enemies from the opposite gravity direction
- **Directional Combat**: Approach enemies from above (normal gravity) or below (inverted gravity)
- **Sound Feedback**: Listen for stomp sound effects when successfully defeating enemies

### Collectibles and Power-ups
- **Data Canisters (Coins)**: Collect these throughout the level
- **Power-ups**: Enhance your abilities, including faster stamina regeneration
- **Flux Surge Stars**: Grant temporary invincibility and increased speed
- **Breakable Containers**: Destroy crates and panels to reveal hidden items

### Progression System
- **Checkpoints**: Touch flag markers to set respawn points
- **Health System**: Start with 3 HP, lose health from enemy contact or stamina depletion
- **Invincibility Frames**: Brief invulnerability after taking damage (visible as flashing)

### Victory Conditions and Star Rating

#### Clear Conditions
1. **1 Star (Mandatory)**: Complete the Stage
2. **2 Stars**: Defeat ALL enemies in the level
3. **3 Stars**: Complete the entire level within 120 seconds

#### HUD Information
- **Health Points**
- **Data Canisters**: Running total of coins collected
- **Enemy Progress**: Shows (defeated / total) enemies
- **Timer**
- **Stamina Bar**: Appears above player when floating or regenerating

### Boss Battle
- **Gyro-Core**: The final boss with multiple phases and attack patterns
- **Vulnerable Windows**: Attack during the recalibration phase (yellow core)
- **Pattern Recognition**: Learn and adapt to the boss's behavior cycles

## Other Features
- Save and Load (from checkpoint)
- Pause menu with full functionality
- Comprehensive Guide for Players
- Powerups (Double Shot, Invincibility, Stamina Boost)
- I-frames with visual feedback
- Breakable tiles
- Clear condition with Star rating system
- Horizontal scrolling camera
- Environmental Puzzle (with buttons and gates)

## Codebase Structure

```
game/
├── assets/
│   ├── audio/
│   │   ├── bgm/             # Background music files
│   │   └── sfx/             # Sound effect files
│   ├── images/
│   │   └── sprites/         # Character and entity sprites
│   └── levels/              # JSON level data files (we modify entities appear in the level here)
├── core/
│   ├── clear_conditions.py  # Star rating and victory tracking
│   ├── settings.py          # Game constants and configuration
│   ├── state.py             # State management system
│   └── __init__.py          # Core utilities (Timer, Stopwatch)
├── entities/
│   ├── boss.py              # Gyro-Core boss implementation
│   ├── bullet.py            # Player projectile system
│   ├── coin.py              # Collectible data canisters
│   ├── enemy.py             # Security drone enemies
│   ├── player.py            # Player character with stamina system
│   └── [other entities]     # Additional game objects
├── world/
│   ├── level.py             # Main gameplay state and logic
│   ├── camera.py            # Scrolling camera system
│   ├── collisions.py        # Collision detection and response
│   └── checkpoints.py       # Save point system
├── io/
│   ├── audio.py             # Audio management and playback
│   ├── input.py             # Input handling and mapping
│   └── level_loader.py      # JSON level parsing
├── ui/
│   ├── hud.py               # In-game interface and progress display
│   ├── win.py               # Victory screen with star rating
│   └── [menu states]        # Various menu implementations
└── main.py                  # Application entry point
```

## Asset Credits

Built as a demonstration of gravity-based platforming mechanics with polarity-driven level design.

- [Character Sprite: Outer Buddies - Asset Pack (Demo)](https://trevor-pupkin.itch.io/outer-buddies)
- [Enemy Sprite](https://github.com/ArrenanRatnavelu/AlienInvasionGame/tree/master)
- [BGM: Space trip - Playsound](https://pixabay.com/vi/music/d%E1%BB%B1ng-c%E1%BA%A3nh-space-trip-114102/)
- Background: Cyberpunk City Skyline - Public Domain / Creative Commons
- BGM: Cyberpunk Street (Main Menu Theme) - Public Domain / Creative Commons
- [BGM: The Last Encounter (Boss Theme)](https://opengameart.org/content/rpg-battle-theme-the-last-encounter-0)
- [Star Sprite Set](https://soulofkiran.itch.io/pixel-art-animated-star)
- [Stamina Sprite](https://iconscout.com/icon/improve-energy-icon_9055343)
- SFX: 
  - [Game Over](https://pixabay.com/sound-effects/game-over-39-199830/)
  - [Damage taken](https://www.101soundboards.com/boards/965630-arknights-dead-sound-soundboard)
  - Others: Super Mario Bros
