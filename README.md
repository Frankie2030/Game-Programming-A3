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
```bash
python -m game.main
```

## Controls

### Movement
- **Arrow Keys / WASD**: Move left and right
- **Space / W / Up Arrow**: Jump
- **E / Shift**: Flip gravity (allows floating in space)

### Interface
- **ESC**: Pause game / Open menu
- **B**: Toggle debug mode (hitbox visualization)
- **Enter**: Confirm selections in menus

## How to Play

### Basic Mechanics
1. **Movement**: Use standard platforming controls to navigate the station
2. **Gravity Flip**: Press E to reverse your gravity, allowing you to walk on ceilings
3. **Floating**: When not touching ground or ceiling, you float in space - but this drains stamina
4. **Stamina Management**: Your stamina bar appears when floating or regenerating. It takes 5 seconds to fully drain and causes 1 HP damage when depleted

### Combat System
- **Enemy Elimination**: Stomp on enemies from the opposite gravity direction
- **Directional Combat**: Approach enemies from above (normal gravity) or below (inverted gravity)
- **Sound Feedback**: Listen for stomp sound effects when successfully defeating enemies

### Collectibles and Power-ups
- **Data Canisters (Coins)**: Collect these throughout the level
- **Power-ups**: Enhance your abilities, including 3x faster stamina regeneration
- **Flux Surge Stars**: Grant 7 seconds of invincibility and increased speed
- **Breakable Containers**: Destroy crates and panels to reveal hidden items

### Progression System
- **Checkpoints**: Touch flag markers to set respawn points
- **Health System**: Start with 3 HP, lose health from enemy contact or stamina depletion
- **Invincibility Frames**: Brief invulnerability after taking damage (visible as flashing)

### Victory Conditions and Star Rating

#### Clear Conditions
1. **1 Star (Mandatory)**: Defeat the Gyro-Core boss
2. **2 Stars**: Defeat ALL enemies in the level
3. **3 Stars**: Complete the entire level within 120 seconds

#### HUD Information
- **Health Points**: Current HP out of maximum
- **Coins Collected**: Running total of data canisters
- **Enemy Progress**: Shows defeated/total enemies (e.g., "Enemies: 3/10")
- **Timer**: Current completion time (turns red after 120 seconds)
- **Stamina Bar**: Appears above player when floating or regenerating

### Boss Battle
- **Gyro-Core**: The final boss with multiple phases and attack patterns
- **Vulnerable Windows**: Attack during the recalibration phase (yellow core)
- **Pattern Recognition**: Learn and adapt to the boss's behavior cycles

### Audio Design
- **Background Music**: Atmospheric space-themed soundtrack
- **Sound Effects**: 
  - Bump sounds when hitting walls/ceilings during jumps
  - Stomp effects for enemy defeats
  - Coin collection chimes
  - Power-up activation sounds

## Key Features

### Core Mechanics
- Gravity-flip mechanics with cooldown system
- Stamina-based floating system (5-second drain, HP penalty)
- Invincibility frames with visual feedback
- Power-up enhanced stamina regeneration (3x faster)

### Combat and Interaction
- Gravity-aware enemy stomp system
- Directional combat based on gravity orientation
- Breakable tiles with dynamic collision updates
- Bullet-based ranged combat system

### Progression and Rewards
- Three-tier star rating system based on performance
- Real-time enemy defeat tracking
- Time-based completion challenges
- Persistent coin collection and checkpoints

### Technical Features
- Horizontal scrolling camera with smooth following
- JSON-based level loading and entity placement
- Comprehensive audio system (BGM and contextual SFX)
- Full menu system with pause/resume functionality
- Dynamic HUD with real-time progress tracking

### Visual and Audio
- Sprite-based animation system with multiple states
- Boss HP visualization and phase indicators
- Stamina bar with color-coded status feedback
- Atmospheric space-themed audio design

## Codebase Structure

```
game/
├── assets/
│   ├── audio/
│   │   ├── bgm/             # Background music files
│   │   └── sfx/             # Sound effect files
│   ├── images/
│   │   └── sprites/         # Character and entity sprites
│   └── levels/              # JSON level data files
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

## Level Design

The level (5120×720) includes:
1. **Tutorial** (0-800px): Basic movement, first gravity flip
2. **Breakable Corridor** (800-2000px): Crates and electro-panels
3. **Flow Section** (2000-3600px): Alternating ceiling/floor platforms
4. **Boss Arena** (3600-5120px): Gyro-Core battle

## Asset Credits

Built as a demonstration of gravity-based platforming mechanics with polarity-driven level design.

- [Character Sprite: Outer Buddies - Asset Pack (Demo)](https://trevor-pupkin.itch.io/outer-buddies)
- [Enemy Sprite](https://github.com/ArrenanRatnavelu/AlienInvasionGame/tree/master)
- [BGM: Space trip - Playsound](https://pixabay.com/vi/music/d%E1%BB%B1ng-c%E1%BA%A3nh-space-trip-114102/)
- Background: Cyberpunk City Skyline - Public Domain / Creative Commons
- BGM: Cyberpunk Street (Main Menu Theme) - Public Domain / Creative Commons
- [BGM: The Last Encounter (Boss Theme)](https://opengameart.org/content/rpg-battle-theme-the-last-encounter-0)
- SFX: 
  - Game Over: https://pixabay.com/sound-effects/game-over-39-199830/
  - Others: Super Mario Bros
