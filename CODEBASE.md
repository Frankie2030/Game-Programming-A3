# Gravity Courier - Codebase Overview

This document explains the architecture, runtime flow, and gameplay features of the A3/game project. It is intended for new contributors and reviewers.

## High-Level Summary
- **Engine/Lib**: Pygame
- **Game Loop Entry**: `game/main.py:main()`
- **Core Patterns**: State stack for screens, timer utilities, camera follow, tile collisions
- **Gameplay Pillars**: Gravity flip traversal, stamina while airborne, platforming, collectibles, ranged attack, boss with phases, star rating clear conditions

## Directory Structure (A3/game)
- `core/`: settings, base state, timers, utilities, clear-conditions model
- `io/`: audio manager, input handler, JSON level loader
- `world/`: level gameplay state, camera, collisions, checkpoints, tiles
- `entities/`: player, enemies (drone), boss, hazards (spikes), collectibles (coin, star, powerup), projectiles, breakables
- `ui/`: states for main menu, options, about, pause, win, lose
- `assets/`: images, audio, levels (referenced by code)

## Boot Flow
1. `main.py` initializes Pygame, window, and clock.
2. Creates a `StateStack` and an `AudioManager` stored in `state_stack.persistent_data['audio']`.
3. Loads SFX placeholders and pushes `MainMenuState` onto the stack.
4. Game loop: poll events → delegate to current state → update current state with `dt` → draw current state → `pygame.display.flip()`.

## State System
- Base class: `core/state.py:GameState` (enter/exit/update/draw/handle_event hooks).
- `StateStack` manages push/pop/replace/clear; only top state receives updates, draws, and events.

### UI States
- `ui/main_menu.py:MainMenuState`: New Game → push `LevelState`; Options → push `OptionsState`; About → push `AboutState`; Exit → post QUIT.
- `ui/options.py:OptionsState`: Adjust music/SFX volumes via `AudioManager`; ESC to return.
- `ui/about.py:AboutState`: Static help/credits; ESC/ENTER to return.
- `ui/pause.py:PauseState`: Overlays on gameplay; Resume/Restart/Options/Main Menu; pauses/unpauses BGM on enter/exit.
- `ui/win.py:WinState`: Shows star rating and run stats; ENTER returns to main menu.
- `ui/lose.py:LoseState`: Retry (pop back to gameplay and continue at checkpoint) or Main Menu.

## Level Gameplay (`world/level.py:LevelState`)
- Loads level data from JSON via `io/level_loader.py:LevelLoader` (falls back to a test level if file missing).
- Systems:
  - `CollisionSystem` on a 2D `Tile` grid
  - `Camera` horizontal follow and clamping
  - `InputHandler` action mapping
  - `HUD` for on-screen info
  - `Stopwatch` for run time
  - `AudioManager` from persistent data
- Spawns: `Player`, `Coin`, `FluxStar`, `PowerUp`, `Spikes`, `BreakableBlock`, `Drone` enemies, `GyroBoss`, and `Checkpoint`s from level data.
- Update loop highlights:
  - Input update; toggle debug; pause pushes `PauseState`.
  - `Player.update(dt, input, collisions)` (movement, gravity flip, jump buffering, stamina, invulnerability, attack animation, bullet spawn timing).
  - Bullets update and hit enemies/boss; enemies update and can be stomped based on gravity/approach side; spikes damage by orientation.
  - Coins/stars/powerups/checkpoints update and interact; breakable blocks can spawn items.
  - Boss activates near its arena, runs phased pattern: spin-up → hazard (rotating beams) → recalibration (vulnerable). Player can stomp or shoot during vulnerable window.
  - `Camera.update(player.rect)`, `Stopwatch.update(dt)`.
  - Win: after boss defeated, crossing near world end transitions to `WinState` with coins/time/clear conditions. Lose: on player death, push `LoseState`, immediately respawn player and reset inputs/camera for retry.
- Draw loop: tiles → checkpoints → collectibles/powerups → breakables → spikes → enemies → boss → bullets → player (optional hitboxes) → HUD.

## Core Config and Utilities
- `core/settings.py`: All tunables: screen size, FPS, physics (gravity, speeds, jump impulse), stamina rates, boss constants, colors, UI font sizes, 3-star time.
- `core/timer.py`: `Timer` (countdown) and `Stopwatch` (elapsed) helpers.
- `core/utils.py`: math helpers (`clamp`, `lerp`, easing), simple geometry utilities.
- `core/clear_conditions.py`: Tracks enemies defeated, boss defeat, completion time; computes 1–3 star rating.

## IO Layer
- `io/audio.py:AudioManager`: Loads/plays SFX and BGM, volume controls; music is global via `pygame.mixer.music`.
- `io/input.py:InputHandler`: Maps keys to actions with both held and just-pressed flags; provides `get_horizontal_input()` and reset helpers.
- `io/level_loader.py:LevelLoader`: Parses a JSON schema into tiles and entity spawn lists. Supports layers (`ground`, `ceiling_layer`) and objects (`platform`, `ceiling`, `crate`, `panel`), and entities (`coin`, `star`, `powerup`, `spikes`, `breakable`, `checkpoint`, `Drone`, `spawn`, `boss`). Provides a programmatic `create_test_level()` fallback.

## World Systems
- `world/collisions.py:CollisionSystem`: Tile-AABB checks based on gravity direction; breakable tile checks; nearby tile queries.
- `world/camera.py:Camera`: Smooth follow with `lerp`, horizontal only; world/screen transforms.
- `world/tile.py:Tile`: Per-face solidity (`solid_up`/`solid_down`), breakable state, optional charged break-face, simple debug rendering.
- `world/checkpoints.py:Checkpoint`: Activation, simple animated flag rendering; stores respawn position.

## Entities and Mechanics
- `entities/player.py:Player`:
  - Movement: horizontal run with friction; gravity applied along `gravity_dir` (+1 down, -1 up); jump with coyote time and input buffering.
  - Gravity Flip: `action` toggles gravity with cooldown; resets vertical speed partially.
  - Stamina: drains while airborne, regenerates on ground; hitting 0 once triggers 1 HP damage and guards against repeated triggers via `stamina_exhausted`.
  - Health/Invulnerability: HP, invuln window after damage; Flux Surge grants timed invulnerability and speed boost.
  - Combat: Attack animation spawns a `Bullet` mid-sequence based on animation frame; facing influences bullet direction.
  - Checkpoints and respawn; coin tally; basic sprite-sheet animation with fallbacks to rectangles.
- `entities/bullet.py:Bullet`: Horizontal projectile with simple tile collision and looping animation.
- `entities/enemy.py:Drone`: Patrol AI with range and direction flip; stomp detection uses overlap-axis heuristic and gravity/velocity checks; sprite fallback.
- `entities/boss.py:GyroBoss`: Timed phase cycle with rotating beam hazards; vulnerable window where stomp or bullets deal damage; draws HP bar on HUD.
- `entities/coin.py`: Collectible with bobbing animation.
- `entities/star.py:FluxStar`: Grants Flux Surge (invulnerability + speed); pulsing glow.
- `entities/powerup.py:PowerUp`: Generic powerups (currently toggles a powered flag, faster stamina regen effect via settings multiplier).
- `entities/spikes.py:Spikes`: Directional hazard that only hurts from the pointed side, respecting player gravity.
- `entities/breakable.py:BreakableBlock`: Breaks on hit, can emit coin/powerup; simple debris effect.

## HUD and Presentation
- `ui/hud.py:HUD` draws HP, coins, enemy progress, timer (warns past 3-star time), Flux Surge banner with pulse, boss HP bar, FPS, controls hint, and optional debug indicator.

## Level Data Schema (summary)
- Root `level` object contains:
  - `layers`: `ground` and `ceiling_layer` rectangles (tile ranges)
  - `objects`: `platform`, `ceiling`, `crate`, `panel`
  - `entities`: lists for `coin`, `star`, `powerup`, `spikes`, `breakable`, `checkpoint`, `Drone`, and singletons `spawn`, `boss`
- Values are in tile coordinates; loader converts to pixel-space and instantiates runtime structures.

## Controls (default)
- Move: Arrow Keys / A-D
- Jump: W / Up
- Attack: Space
- Flip Gravity: E or Shift
- Pause: ESC or P
- Confirm/Back: Enter / Backspace
- Debug toggle: B

## Win/Lose Conditions and Rating
- Win: Defeat boss → boss door opens → cross end of level to transition to `WinState`.
- Lose: Player HP <= 0 → `LoseState` pushed; upon returning, player is respawned at last checkpoint.
- Star Rating: 1★ boss, 2★ all enemies defeated, 3★ under `TIME_LIMIT_3_STAR` seconds.

## Rendering Order
Tiles → Checkpoints → Coins/Stars → PowerUps → Breakables → Spikes → Enemies → Boss → Bullets → Player → HUD. Debug mode overlays hitboxes.

## Notable Extensibility Points
- Add more states by subclassing `GameState`.
- Add entities by following the pattern in `entities/` and register spawns in `LevelLoader`.
- Expand level JSON with more object/entity types; tiles support per-face solidity and breakable panels with a charged face.
- Replace placeholder art/audio under `assets/` without code changes.

## Known Behaviors/Notes
- If assets are missing, the player and enemies fall back to colored shapes, and audio warns but continues.
- Level loader warns and uses a programmatic test level if `assets/levels/level1.json` is absent.

