"""
Simple timer utilities
"""


class Timer:
    """Countdown timer"""
    
    def __init__(self, duration=0.0):
        self.duration = duration
        self.time_left = 0.0
        self.active = False
    
    def start(self, duration=None):
        """Start or restart the timer"""
        if duration is not None:
            self.duration = duration
        self.time_left = self.duration
        self.active = True
    
    def update(self, dt):
        """Update timer, return True when it expires"""
        if not self.active:
            return False
        
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.active = False
            return True
        return False
    
    def stop(self):
        """Stop the timer"""
        self.active = False
        self.time_left = 0
    
    def is_active(self):
        """Check if timer is running"""
        return self.active
    
    def get_ratio(self):
        """Get progress ratio (0.0 to 1.0)"""
        if self.duration == 0:
            return 0
        return 1.0 - (self.time_left / self.duration)


class Stopwatch:
    """Elapsed time tracker"""
    
    def __init__(self):
        self.elapsed = 0.0
        self.active = False
    
    def start(self):
        """Start the stopwatch"""
        self.active = True
    
    def stop(self):
        """Stop the stopwatch"""
        self.active = False
    
    def reset(self):
        """Reset elapsed time"""
        self.elapsed = 0.0
    
    def update(self, dt):
        """Update elapsed time"""
        if self.active:
            self.elapsed += dt
    
    def get_time(self):
        """Get elapsed time in seconds"""
        return self.elapsed
