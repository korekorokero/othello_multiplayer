# game/player.py
"""
Player class for Othello game
"""

from typing import Optional
from shared.constants import BLACK, WHITE, PLAYER_COLORS
import time

class Player:
    """
    Represents a player in the Othello game
    """
    
    def __init__(self, username: str, color: int, player_id: Optional[str] = None):
        """
        Initialize a new player
        
        Args:
            username: Player's username
            color: Player's color (BLACK or WHITE)
            player_id: Optional unique identifier for the player
            
        Raises:
            ValueError: If color is not BLACK or WHITE
        """
        if color not in [BLACK, WHITE]:
            raise ValueError(f"Invalid player color: {color}")
        
        self.username = username
        self.color = color
        self.player_id = player_id or username
        self.score = 0
        self.ready = False
        self.connected = True
        self.last_seen = time.time()
        
        # Game statistics
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.games_drawn = 0
        
        # Current game stats
        self.moves_made = 0
        self.pieces_captured = 0
        self.game_start_time = None
    
    @property
    def color_name(self) -> str:
        """Get the color name as a string"""
        return PLAYER_COLORS[self.color]
    
    @property
    def is_black(self) -> bool:
        """Check if player is playing as black"""
        return self.color == BLACK
    
    @property
    def is_white(self) -> bool:
        """Check if player is playing as white"""
        return self.color == WHITE
    
    @property
    def win_rate(self) -> float:
        """Calculate player's win rate"""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100
    
    def set_ready(self, ready: bool = True):
        """Set player's ready status"""
        self.ready = ready
    
    def set_connected(self, connected: bool = True):
        """Set player's connection status"""
        self.connected = connected
        if connected:
            self.last_seen = time.time()
    
    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen = time.time()
    
    def start_game(self):
        """Initialize game-specific stats"""
        self.moves_made = 0
        self.pieces_captured = 0
        self.game_start_time = time.time()
        self.ready = False
    
    def make_move(self, pieces_captured: int = 0):
        """Record a move made by the player"""
        self.moves_made += 1
        self.pieces_captured += pieces_captured
    
    def finish_game(self, result: str, final_score: int):
        """
        Record game completion
        
        Args:
            result: Game result ('win', 'lose', 'draw')
            final_score: Player's final score
        """
        self.games_played += 1
        self.score = final_score
        
        if result == 'win':
            self.games_won += 1
        elif result == 'lose':
            self.games_lost += 1
        elif result == 'draw':
            self.games_drawn += 1
    
    def get_game_duration(self) -> Optional[float]:
        """Get current game duration in seconds"""
        if self.game_start_time is None:
            return None
        return time.time() - self.game_start_time
    
    def get_stats(self) -> dict:
        """Get player statistics as a dictionary"""
        return {
            'username': self.username,
            'color': self.color,
            'color_name': self.color_name,
            'games_played': self.games_played,
            'games_won': self.games_won,
            'games_lost': self.games_lost,
            'games_drawn': self.games_drawn,
            'win_rate': round(self.win_rate, 2),
            'current_score': self.score,
            'ready': self.ready,
            'connected': self.connected
        }
    
    def reset_game_stats(self):
        """Reset current game statistics"""
        self.moves_made = 0
        self.pieces_captured = 0
        self.game_start_time = None
        self.score = 0
    
    def to_dict(self) -> dict:
        """Convert player to dictionary for serialization"""
        return {
            'username': self.username,
            'color': self.color,
            'player_id': self.player_id,
            'score': self.score,
            'ready': self.ready,
            'connected': self.connected,
            'moves_made': self.moves_made,
            'pieces_captured': self.pieces_captured
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create player from dictionary"""
        player = cls(
            username=data['username'],
            color=data['color'],
            player_id=data.get('player_id')
        )
        player.score = data.get('score', 0)
        player.ready = data.get('ready', False)
        player.connected = data.get('connected', True)
        player.moves_made = data.get('moves_made', 0)
        player.pieces_captured = data.get('pieces_captured', 0)
        return player
    
    def __str__(self) -> str:
        """String representation of the player"""
        return f"{self.username} ({self.color_name})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Player(username='{self.username}', color={self.color}, "
                f"score={self.score}, ready={self.ready}, connected={self.connected})")
    
    def __eq__(self, other) -> bool:
        """Check equality based on player_id"""
        if not isinstance(other, Player):
            return False
        return self.player_id == other.player_id
    
    def __hash__(self) -> int:
        """Hash based on player_id for use in sets/dicts"""
        return hash(self.player_id)