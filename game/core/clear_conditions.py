"""
Clear conditions tracking system for star rating
"""
from game.core import settings


class ClearConditions:
    """Tracks clear conditions for star rating"""
    
    def __init__(self, total_enemies):
        self.total_enemies = total_enemies
        self.enemies_defeated = 0
        self.boss_defeated = False
        self.completion_time = 0.0
        
    def defeat_enemy(self):
        """Mark an enemy as defeated"""
        if self.enemies_defeated < self.total_enemies:
            self.enemies_defeated += 1
    
    def defeat_boss(self):
        """Mark boss as defeated"""
        self.boss_defeated = True
    
    def set_completion_time(self, time):
        """Set the completion time"""
        self.completion_time = time
    
    def get_star_rating(self):
        """Calculate star rating based on conditions"""
        stars = 1
            
        # 2 stars: Defeat all enemies
        if self.enemies_defeated >= self.total_enemies:
            stars = 2
            
            # 3 stars: Complete within time limit
            if self.completion_time <= settings.TIME_LIMIT_3_STAR:
                stars = 3
        
        return stars
    
    def get_enemies_progress(self):
        """Get enemies progress as tuple (defeated, total)"""
        return (self.enemies_defeated, self.total_enemies)
    
    def all_enemies_defeated(self):
        """Check if all enemies are defeated"""
        return self.enemies_defeated >= self.total_enemies
    
    def is_under_time_limit(self):
        """Check if under 3-star time limit"""
        return self.completion_time <= settings.TIME_LIMIT_3_STAR