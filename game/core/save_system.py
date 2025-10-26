"""Save/Load system for game progress tracking"""
import json
import os
from datetime import datetime


class SaveSystem:
    """Manages game progress save/load functionality
    
    Save structure:
    {
        'unlocked_levels': [1, 2],
        'current_level': 1,  # Level currently being attempted (for Resume)
        'levels': {
            '1': {
                'completed': True,
                'attempts': 0,
                'best_time': 45.2,
                'best_coins': 20,
                'best_enemies_defeated': 5
            },
            '2': {
                'completed': False,
                'attempts': 3,
                'best_time': None,
                'best_coins': 0,
                'best_enemies_defeated': 0
            }
        }
    }
    """
    
    SAVE_FILE = "save_game.json"
    
    @staticmethod
    def _load_data():
        """Internal: Load raw save data"""
        if not os.path.exists(SaveSystem.SAVE_FILE):
            return {
                'unlocked_levels': [1],
                'current_level': None,
                'levels': {}
            }
        
        try:
            with open(SaveSystem.SAVE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load save: {e}")
            return {
                'unlocked_levels': [1],
                'current_level': None,
                'levels': {}
            }
    
    @staticmethod
    def _save_data(data):
        """Internal: Save raw data"""
        try:
            with open(SaveSystem.SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save: {e}")
            return False
    
    @staticmethod
    def save_game(player_data, level_data, game_time, coins_collected, enemies_defeated, boss_data=None, entities_data=None):
        """Save current game state for resuming later"""
        try:
            data = SaveSystem._load_data()
            
            # Store the game state for resuming
            data['game_state'] = {
                'player': player_data,
                'level': level_data,
                'game_time': game_time,
                'coins_collected': coins_collected,
                'enemies_defeated': enemies_defeated,
                'boss': boss_data,
                'entities': entities_data,
                'timestamp': datetime.now().isoformat()
            }
            
            return SaveSystem._save_data(data)
        except Exception as e:
            print(f"Failed to save game state: {e}")
            return False
    
    @staticmethod
    def start_level(level_id):
        """Mark a level as currently being played and increment attempts"""
        data = SaveSystem._load_data()
        data['current_level'] = level_id
        
        # Initialize level data if doesn't exist
        level_key = str(level_id)
        if level_key not in data['levels']:
            data['levels'][level_key] = {
                'completed': False,
                'attempts': 0,
                'best_time': None,
                'best_coins': 0,
                'best_enemies_defeated': 0
            }
        
        # Increment attempts
        data['levels'][level_key]['attempts'] += 1
        
        SaveSystem._save_data(data)
    
    @staticmethod
    def complete_level(level_id, time, coins, enemies_defeated):
        """Save level completion stats and unlock next level"""
        data = SaveSystem._load_data()
        level_key = str(level_id)
        
        # Initialize if doesn't exist
        if level_key not in data['levels']:
            data['levels'][level_key] = {
                'completed': False,
                'attempts': 0,
                'best_time': None,
                'best_coins': 0,
                'best_enemies_defeated': 0
            }
        
        level_data = data['levels'][level_key]
        level_data['completed'] = True
        level_data['attempts'] = 0  # Reset attempts on completion
        
        # Update bests
        if level_data['best_time'] is None or time < level_data['best_time']:
            level_data['best_time'] = time
        if coins > level_data['best_coins']:
            level_data['best_coins'] = coins
        if enemies_defeated > level_data['best_enemies_defeated']:
            level_data['best_enemies_defeated'] = enemies_defeated
        
        # Unlock next level
        next_level = level_id + 1
        if next_level not in data['unlocked_levels']:
            data['unlocked_levels'].append(next_level)
        
        # Clear current level
        data['current_level'] = None
        
        SaveSystem._save_data(data)
    
    @staticmethod
    def get_level_stats(level_id):
        """Get stats for a specific level"""
        data = SaveSystem._load_data()
        level_key = str(level_id)
        
        if level_key in data['levels']:
            return data['levels'][level_key]
        
        return {
            'completed': False,
            'attempts': 0,
            'best_time': None,
            'best_coins': 0,
            'best_enemies_defeated': 0
        }
    
    @staticmethod
    def get_unlocked_levels():
        """Get list of unlocked levels"""
        data = SaveSystem._load_data()
        return data.get('unlocked_levels', [1])
    
    @staticmethod
    def get_current_level():
        """Get the level currently being attempted (for Resume)"""
        data = SaveSystem._load_data()
        return data.get('current_level')
    
    @staticmethod
    def has_resume():
        """Check if there's a level in progress to resume"""
        data = SaveSystem._load_data()
        return data.get('current_level') is not None and 'game_state' in data
    
    @staticmethod
    def has_save():
        """Check if any save data exists"""
        return os.path.exists(SaveSystem.SAVE_FILE)
    
    @staticmethod
    def delete_save():
        """Delete all save data"""
        try:
            if os.path.exists(SaveSystem.SAVE_FILE):
                os.remove(SaveSystem.SAVE_FILE)
            return True
        except Exception as e:
            print(f"Failed to delete save: {e}")
            return False
    
    @staticmethod
    def get_save_info():
        """Get summary info for display in main menu"""
        data = SaveSystem._load_data()
        current_level = data.get('current_level')
        
        if current_level:
            level_stats = SaveSystem.get_level_stats(current_level)
            return {
                'current_level': current_level,
                'attempts': level_stats['attempts'],
                'unlocked_levels': data['unlocked_levels']
            }
        
        return None
