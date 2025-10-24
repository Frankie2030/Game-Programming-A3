"""
Level loading from JSON format
"""
import json
from game.core import settings
from game.world.tile import Tile


class LevelLoader:
    """Loads level data from JSON"""
    
    @staticmethod
    def load_from_json(filepath):
        """Load level from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return LevelLoader._parse_level_data(data)
        except FileNotFoundError:
            print(f"Warning: Level file {filepath} not found, using test level")
            return LevelLoader.create_test_level()
    
    @staticmethod
    def _parse_level_data(data):
        """Parse JSON level data into game structures"""
        level_data = data.get('level', {})
        
        width_tiles = settings.WORLD_WIDTH // settings.TILE_SIZE
        height_tiles = settings.WORLD_HEIGHT // settings.TILE_SIZE
        
        # Initialize empty tile map
        tile_map = [[None for _ in range(width_tiles)] for _ in range(height_tiles)]
        
        # Parse layers (background tiles)
        layers = level_data.get('layers', {})
        
        # Ground layer - fills rectangles
        if 'ground' in layers:
            for rect in layers['ground']:
                x_range = rect.get('x', [0, width_tiles])
                y_range = rect.get('y', [height_tiles - 2, height_tiles])
                for row in range(y_range[0], y_range[1]):
                    for col in range(x_range[0], x_range[1]):
                        if 0 <= row < height_tiles and 0 <= col < width_tiles:
                            x = col * settings.TILE_SIZE
                            y = row * settings.TILE_SIZE
                            tile_map[row][col] = Tile(1, x, y, solid_up=True, solid_down=True)
        
        # Ceiling layer - for upside-down gravity
        if 'ceiling_layer' in layers:
            for rect in layers['ceiling_layer']:
                x_range = rect.get('x', [0, width_tiles])
                y_range = rect.get('y', [0, 1])
                for row in range(y_range[0], y_range[1]):
                    for col in range(x_range[0], x_range[1]):
                        if 0 <= row < height_tiles and 0 <= col < width_tiles:
                            x = col * settings.TILE_SIZE
                            y = row * settings.TILE_SIZE
                            tile_map[row][col] = Tile(1, x, y, solid_up=True, solid_down=True)
        
        # Parse objects (platforms, walls, etc.)
        objects = level_data.get('objects', {})
        
        # Platform objects
        if 'platform' in objects:
            for pos in objects['platform']:
                col, row = pos[0], pos[1]
                if 0 <= row < height_tiles and 0 <= col < width_tiles:
                    x = col * settings.TILE_SIZE
                    y = row * settings.TILE_SIZE
                    tile_map[row][col] = Tile(2, x, y, solid_up=True, solid_down=True)
        
        # Ceiling objects
        if 'ceiling' in objects:
            for pos in objects['ceiling']:
                col, row = pos[0], pos[1]
                if 0 <= row < height_tiles and 0 <= col < width_tiles:
                    x = col * settings.TILE_SIZE
                    y = row * settings.TILE_SIZE
                    tile_map[row][col] = Tile(1, x, y, solid_up=True, solid_down=True)
        
        # Breakable crates
        if 'crate' in objects:
            for pos in objects['crate']:
                col, row = pos[0], pos[1]
                if 0 <= row < height_tiles and 0 <= col < width_tiles:
                    x = col * settings.TILE_SIZE
                    y = row * settings.TILE_SIZE
                    tile_map[row][col] = Tile(3, x, y, solid_up=True, solid_down=True,
                                             breakable=True)
        
        # Electro-panels with charged faces
        if 'panel' in objects:
            for pos in objects['panel']:
                col, row, face = pos[0], pos[1], pos[2] if len(pos) > 2 else None
                if 0 <= row < height_tiles and 0 <= col < width_tiles:
                    x = col * settings.TILE_SIZE
                    y = row * settings.TILE_SIZE
                    tile_map[row][col] = Tile(4, x, y, solid_up=True, solid_down=True,
                                             breakable=True, charged_face=face)
        
        # Parse entities
        entities_data = level_data.get('entities', {})
        
        # Coins
        coins = []
        for pos in entities_data.get('coin', []):
            col, row = pos[0], pos[1]
            x = col * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 8
            y = row * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 8
            coins.append((x, y))
        
        # Stars (Flux Surge)
        stars = []
        for pos in entities_data.get('star', []):
            col, row = pos[0], pos[1]
            x = col * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 12
            y = row * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 12
            stars.append((x, y))
        
        # Power-ups
        powerups = []
        for pos in entities_data.get('powerup', []):
            col, row = pos[0], pos[1]
            ptype = pos[2] if len(pos) > 2 else 'speed'
            x = col * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 12
            y = row * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 12
            powerups.append({'x': x, 'y': y, 'type': ptype})
        
        # Storm powerups
        storms = []
        for pos in entities_data.get('storm', []):
            col, row = pos[0], pos[1]
            x = col * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 12
            y = row * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 12
            print(f"Level loader: Adding storm at ({x}, {y})")  # Debug output
            storms.append((x, y))
        
        # Spikes
        spikes = []
        for pos in entities_data.get('spikes', []):
            col, row = pos[0], pos[1]
            orientation = pos[2] if len(pos) > 2 else 'up'
            x = col * settings.TILE_SIZE
            y = row * settings.TILE_SIZE
            spikes.append({'x': x, 'y': y, 'orientation': orientation})
        
        # Buttons
        buttons = []
        for pos in entities_data.get('button', []):
            col, row = pos[0], pos[1]
            color = pos[2] if len(pos) > 2 else 'red'
            facing = pos[3] if len(pos) > 3 else 'up'
            x = col * settings.TILE_SIZE
            y = row * settings.TILE_SIZE
            buttons.append({'x': x, 'y': y, 'color': color, 'facing': facing})
        
        # Gates
        gates = []
        for pos in entities_data.get('gate', []):
            col, row = pos[0], pos[1]
            height_tiles = pos[2] if len(pos) > 2 else 3
            orientation = pos[3] if len(pos) > 3 else 'up'
            x = col * settings.TILE_SIZE
            y = row * settings.TILE_SIZE
            height = height_tiles * settings.TILE_SIZE
            gates.append({'x': x, 'y': y, 'height': height, 'orientation': orientation})
        
        # Breakable blocks
        breakables = []
        for pos in entities_data.get('breakable', []):
            col, row = pos[0], pos[1]
            contents = pos[2] if len(pos) > 2 else None
            x = col * settings.TILE_SIZE
            y = row * settings.TILE_SIZE
            breakables.append({'x': x, 'y': y, 'contents': contents})
        
        # Checkpoints
        checkpoints = []
        for pos in entities_data.get('checkpoint', []):
            col, row = pos[0], pos[1]
            # Center the checkpoint on the tile and place it on the ground
            x = col * settings.TILE_SIZE + settings.TILE_SIZE // 2 - 8  # 8 = half of checkpoint width (16)
            y = row * settings.TILE_SIZE - 48  # Position flag pole on the ground (48 = checkpoint height)
            checkpoints.append((x, y))
        
        # Enemies
        enemies = []
        for enemy_data in entities_data.get('Drone', []):
            col, row = enemy_data[0], enemy_data[1]
            anchor = enemy_data[2] if len(enemy_data) > 2 else 'floor'
            patrol_range = enemy_data[3] if len(enemy_data) > 3 else 128
            color = enemy_data[4] if len(enemy_data) > 4 else 'blue'
            x = col * settings.TILE_SIZE
            y = row * settings.TILE_SIZE
            enemies.append({
                'type': 'drone',
                'x': x,
                'y': y,
                'anchor': anchor,
                'range': patrol_range,
                'color': color
            })
        
        # Player spawn
        spawn_data = entities_data.get('spawn', [[2, height_tiles - 3]])[0]
        spawn_x = spawn_data[0] * settings.TILE_SIZE
        spawn_y = spawn_data[1] * settings.TILE_SIZE
        
        # Boss spawn (optional)
        result = {
            'tile_map': tile_map,
            'width': width_tiles,
            'height': height_tiles,
            'spawn_x': spawn_x,
            'spawn_y': spawn_y,
            'checkpoints': checkpoints,
            'coins': coins,
            'stars': stars,
            'powerups': powerups,
            'storms': storms,
            'spikes': spikes,
            'breakables': breakables,
            'enemies': enemies,
            'buttons': buttons,
            'gates': gates
        }
        
        # Only add boss if it exists in the level data
        if 'boss' in entities_data and entities_data['boss']:
            boss_data = entities_data['boss'][0]
            result['boss_x'] = boss_data[0] * settings.TILE_SIZE
            result['boss_y'] = boss_data[1] * settings.TILE_SIZE
        
        return result
    
    @staticmethod
    def create_test_level():
        """Create a simple test level programmatically"""
        width_tiles = settings.WORLD_WIDTH // settings.TILE_SIZE
        height_tiles = settings.WORLD_HEIGHT // settings.TILE_SIZE
        
        tile_map = [[None for _ in range(width_tiles)] for _ in range(height_tiles)]
        
        # Floor
        for row in range(height_tiles - 2, height_tiles):
            for col in range(width_tiles):
                x = col * settings.TILE_SIZE
                y = row * settings.TILE_SIZE
                tile_map[row][col] = Tile(1, x, y, solid_up=True, solid_down=True)
        
        # Simple platform
        for col in range(20, 30):
            row = height_tiles - 6
            x = col * settings.TILE_SIZE
            y = row * settings.TILE_SIZE
            tile_map[row][col] = Tile(2, x, y, solid_up=True, solid_down=True)
        
        return {
            'tile_map': tile_map,
            'width': width_tiles,
            'height': height_tiles,
            'spawn_x': 64,
            'spawn_y': settings.WORLD_HEIGHT - 96,
            'boss_x': 4480,
            'boss_y': 360,
            'checkpoints': [(1600, settings.WORLD_HEIGHT - 96)],
            'coins': [(400 + i * 64, settings.WORLD_HEIGHT - 160) for i in range(20)],
            'stars': [(2400, settings.WORLD_HEIGHT - 180)],
            'powerups': [],
            'spikes': [],
            'breakables': [],
            'enemies': [
                {'type': 'drone', 'x': 800, 'y': settings.WORLD_HEIGHT - 80, 'anchor': 'floor', 'range': 128, 'color': 'blue'},
                {'type': 'drone', 'x': 1200, 'y': settings.WORLD_HEIGHT - 80, 'anchor': 'floor', 'range': 96, 'color': 'green'}
            ],
            'buttons': [],
            'gates': []
        }
