"""
Save/Load system for game state
"""
import json
import os
from datetime import datetime


class SaveSystem:
    """Manages game save/load functionality"""
    
    SAVE_FILE = "save_game.json"
    
    @staticmethod
    def save_game(player_data, level_data, game_time, coins_collected, enemies_defeated, boss_data, entities_data):
        """Save current game state"""
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'player': {
                'x': player_data.get('x', 0),
                'y': player_data.get('y', 0),
                'hp': player_data.get('hp', 3),
                'coins': player_data.get('coins', 0),
                'checkpoint_x': player_data.get('checkpoint_x', 0),
                'checkpoint_y': player_data.get('checkpoint_y', 0),
                'gravity_dir': player_data.get('gravity_dir', 1),
                'stamina': player_data.get('stamina', 1.0),
                'powered_up': player_data.get('powered_up', False)
            },
            'level': {
                'level_id': level_data.get('level_id', 1),
                'spawn_x': level_data.get('spawn_x', 64),
                'spawn_y': level_data.get('spawn_y', 576)
            },
            'boss': {
                'hp': boss_data.get('hp', 8),
                'max_hp': boss_data.get('max_hp', 8),
                'alive': boss_data.get('alive', True),
                'defeated': boss_data.get('defeated', False),
                'phase': boss_data.get('phase', 'spin_up'),
                'vulnerable': boss_data.get('vulnerable', False),
                'boss_active': boss_data.get('boss_active', False),
                'boss_door_open': boss_data.get('boss_door_open', False)
            },
            'entities': {
                'coins': entities_data.get('coins', []),
                'stars': entities_data.get('stars', []),
                'powerups': entities_data.get('powerups', []),
                'enemies': entities_data.get('enemies', []),
                'breakables': entities_data.get('breakables', [])
            },
            'progress': {
                'game_time': game_time,
                'coins_collected': coins_collected,
                'enemies_defeated': enemies_defeated
            }
        }
        
        try:
            with open(SaveSystem.SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    @staticmethod
    def load_game():
        """Load saved game state"""
        if not SaveSystem.has_save():
            return None
        
        try:
            with open(SaveSystem.SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            return save_data
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    @staticmethod
    def has_save():
        """Check if a save file exists"""
        return os.path.exists(SaveSystem.SAVE_FILE)
    
    @staticmethod
    def delete_save():
        """Delete the save file"""
        try:
            if SaveSystem.has_save():
                os.remove(SaveSystem.SAVE_FILE)
            return True
        except Exception as e:
            print(f"Failed to delete save: {e}")
            return False
    
    @staticmethod
    def get_save_info():
        """Get basic info about the save file"""
        if not SaveSystem.has_save():
            return None
        
        try:
            with open(SaveSystem.SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            
            return {
                'timestamp': save_data.get('timestamp', 'Unknown'),
                'level': save_data.get('level', {}).get('level_id', 1),
                'coins': save_data.get('player', {}).get('coins', 0),
                'game_time': save_data.get('progress', {}).get('game_time', 0),
                'boss_defeated': save_data.get('boss', {}).get('defeated', False),
                'boss_hp': save_data.get('boss', {}).get('hp', 8)
            }
        except Exception as e:
            print(f"Failed to get save info: {e}")
            return None
