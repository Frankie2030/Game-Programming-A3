# Update Notes - New Features

## ✅ Completed Features

### 1. **Debug Hitboxes (Press B)**
- Press **B** to toggle hitbox visualization
- Green box = Player hitbox
- Magenta boxes = Enemy/Boss hitboxes
- Helps debug collision issues
- Indicator shows "DEBUG MODE: Hitboxes ON" when active

### 2. **Bigger Enemies with Attack Direction Arrows**
- Enemies increased from 28×20 to **48×40 pixels**
- Yellow arrows show which direction to attack from:
  - Floor enemies: Arrow points **DOWN** (attack from above)
  - Ceiling enemies: Arrow points **UP** (attack from below)
- Improved stomp tolerance (epsilon increased from 5 to 8 pixels)

### 3. **New Entities**

#### **Spikes**
- Deadly hazards that damage on contact
- Four orientations: 'up', 'down', 'left', 'right'
- Only hurt from the pointed direction
- Added to level at positions: [45,19], [46,19], [70,19], [71,19]

#### **Breakable Blocks**
- Brown brick blocks that break when hit
- May contain coins or power-ups
- Break animation with flying particles
- Contents hint shown as small icon on block
- Added 5 breakable blocks in level with various contents

#### **Power-Ups**
- Floating collectible with glow effect
- Types: 'speed', 'double_jump', etc.
- Changes player sprite when collected
- One power-up added at position [55, 10]

### 4. **Player Sprite Support**
- Normal sprite: `game/assets/images/sprites/player.png`
- Powered-up sprite: `game/assets/images/sprites/player_powered.png`
- Sprites flip based on:
  - Facing direction (left/right)
  - Gravity direction (upside-down when inverted)
- Powered-up state shows orange tint if no sprite
- Flux Surge adds glowing effect

### 5. **Game Over Screen Fix**
- Now shows "TRANSMISSION FAILED" screen when dying
- Two options:
  - **Retry**: Respawns at last checkpoint
  - **Main Menu**: Return to main menu
- Player respawns automatically at checkpoint when selecting Retry
- Maintains checkpoint coin count

## JSON Level Format Updates

### New Entity Types:

```json
"powerup": [
    [col, row, "type"]
],
"spikes": [
    [col, row, "orientation"]
],
"breakable": [
    [col, row, "contents"]  // contents can be "coin", "powerup", or null
]
```

### Example:
```json
"powerup": [[55, 10, "speed"]],
"spikes": [[45, 19, "up"], [46, 19, "up"]],
"breakable": [[28, 18, "coin"], [48, 16, "powerup"], [64, 18, null]]
```

## Asset Requirements

### Player Sprites (Optional):
- `game/assets/images/sprites/player.png` - Normal player (24×32)
- `game/assets/images/sprites/player_powered.png` - Powered-up player (24×32)

### Power-up Sprites (Optional):
- `game/assets/images/sprites/powerup_speed.png` (24×24)
- Falls back to glowing "P" box if not found

### Enemy Sprites (Already supported):
- `game/assets/images/sprites/alienblue.png` (48×40)
- `game/assets/images/sprites/aliengreen.png` (48×40)
- `game/assets/images/sprites/alienred.png` (48×40)

## Controls
- **B** - Toggle debug hitboxes
- All other controls remain the same

## Known Changes
- Enemies are now larger (48×40 instead of 28×20)
- Stomp detection more forgiving (8px tolerance)
- Death now shows lose screen before respawning
- Power-up state persists across checkpoints
