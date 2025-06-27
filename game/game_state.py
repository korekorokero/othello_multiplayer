# game/game_state.py
"""
Game state management for Othello
Combines board, rules, and players to manage complete game state
"""

from typing import List, Tuple, Optional, Dict
import time
from .othello_board import OthelloBoard
from .othello_rules import OthelloRules
from .player import Player
from shared.constants import BLACK, WHITE, STARTING_PLAYER, GAME_WAITING, GAME_ACTIVE, GAME_FINISHED

class GameState:
    """
    Manages the complete state of an Othello game
    """
    
    def __init__(self, game_id: str):
        """
        Initialize a new game state
        
        Args:
            game_id: Unique identifier for this game
        """
        self.game_id = game_id
        self.board = OthelloBoard()
        self.players: Dict[int, Player] = {}  # color -> Player
        self.current_player = STARTING_PLAYER
        self.status = GAME_WAITING
        self.winner = None
        self.game_start_time = None
        self.game_end_time = None
        self.move_history: List[Dict] = []
        self.spectators: List[str] = []
        
        # Game flow control
        self.passes_in_row = 0  # Track consecutive passes
        self.last_move_time = None
        
    def add_player(self, player: Player) -> bool:
        """
        Add a player to the game
        
        Args:
            player: Player object to add
            
        Returns:
            True if player was added successfully, False otherwise
        """
        if len(self.players) >= 2:
            return False
        
        if player.color in self.players:
            return False
        
        self.players[player.color] = player
        return True
    
    def remove_player(self, color: int) -> Optional[Player]:
        """
        Remove a player from the game
        
        Args:
            color: Color of the player to remove
            
        Returns:
            Removed player object, or None if not found
        """
        return self.players.pop(color, None)
    
    def get_player(self, color: int) -> Optional[Player]:
        """Get player by color"""
        return self.players.get(color)
    
    def get_opponent(self, color: int) -> Optional[Player]:
        """Get the opponent of the given player color"""
        opponent_color = WHITE if color == BLACK else BLACK
        return self.players.get(opponent_color)
    
    def is_full(self) -> bool:
        """Check if game has maximum number of players"""
        return len(self.players) >= 2
    
    def can_start(self) -> bool:
        """Check if game can be started"""
        return (len(self.players) == 2 and 
                all(player.ready for player in self.players.values()) and
                self.status == GAME_WAITING)
    
    def start_game(self) -> bool:
        """
        Start the game if conditions are met
        
        Returns:
            True if game was started, False otherwise
        """
        if not self.can_start():
            return False
        
        self.status = GAME_ACTIVE
        self.game_start_time = time.time()
        self.current_player = STARTING_PLAYER
        self.passes_in_row = 0
        self.last_move_time = time.time()
        
        # Initialize player game stats
        for player in self.players.values():
            player.start_game()
        
        return True
    
    def make_move(self, row: int, col: int, player_color: int) -> Dict:
        """
        Attempt to make a move
        
        Args:
            row: Row coordinate
            col: Column coordinate  
            player_color: Color of the player making the move
            
        Returns:
            Dictionary with move result information
        """
        result = {
            'success': False,
            'error': None,
            'flipped_pieces': [],
            'scores': {},
            'game_over': False,
            'winner': None
        }
        
        # Validate game state
        if self.status != GAME_ACTIVE:
            result['error'] = "Game is not active"
            return result
        
        if player_color != self.current_player:
            result['error'] = "Not your turn"
            return result
        
        if player_color not in self.players:
            result['error'] = "Player not in game"
            return result
        
        # Validate and make the move
        if not OthelloRules.is_valid_move(self.board, row, col, player_color):
            result['error'] = "Invalid move"
            return result
        
        # Get flipped pieces before making the move
        flipped_pieces = OthelloRules.get_flipped_pieces(self.board, row, col, player_color)
        
        # Make the move
        if OthelloRules.make_move(self.board, row, col, player_color):
            result['success'] = True
            result['flipped_pieces'] = flipped_pieces
            result['scores'] = self.board.get_scores()
            
            # Update player stats
            player = self.players[player_color]
            player.make_move(len(flipped_pieces))
            
            # Record move in history
            self._record_move(row, col, player_color, flipped_pieces)
            
            # Reset pass counter
            self.passes_in_row = 0
            self.last_move_time = time.time()
            
            # Check if game is over
            if OthelloRules.is_game_over(self.board):
                self._end_game()
                result['game_over'] = True
                result['winner'] = self.winner
            else:
                # Switch to next player
                self._next_turn()
        
        return result
    
    def pass_turn(self, player_color: int) -> Dict:
        """
        Pass the current turn (when no valid moves available)
        
        Args:
            player_color: Color of the player passing
            
        Returns:
            Dictionary with pass result information
        """
        result = {
            'success': False,
            'error': None,
            'game_over': False,
            'winner': None
        }
        
        if self.status != GAME_ACTIVE:
            result['error'] = "Game is not active"
            return result
        
        if player_color != self.current_player:
            result['error'] = "Not your turn"
            return result
        
        # Check if player actually has no valid moves
        if OthelloRules.has_valid_moves(self.board, player_color):
            result['error'] = "You have valid moves available"
            return result
        
        result['success'] = True
        self.passes_in_row += 1
        
        # Record pass in history
        self._record_pass(player_color)
        
        # Check if both players passed (game over)
        if self.passes_in_row >= 2:
            self._end_game()
            result['game_over'] = True
            result['winner'] = self.winner
        else:
            self._next_turn()
        
        return result
    
    def _next_turn(self):
        """Switch to the next player's turn"""
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.last_move_time = time.time()
    
    def _end_game(self):
        """End the game and determine winner"""
        self.status = GAME_FINISHED
        self.game_end_time = time.time()
        self.winner = OthelloRules.get_winner(self.board)
        
        # Update player statistics
        scores = self.board.get_scores()
        for color, player in self.players.items():
            final_score = scores[color]
            if self.winner == color:
                result = 'win'
            elif self.winner == 0:  # EMPTY means tie
                result = 'draw'
            else:
                result = 'lose'
            
            player.finish_game(result, final_score)
    
    def _record_move(self, row: int, col: int, player_color: int, flipped_pieces: List[Tuple[int, int]]):
        """Record a move in the game history"""
        move = {
            'type': 'move',
            'player': player_color,
            'row': row,
            'col': col,
            'flipped_pieces': flipped_pieces,
            'timestamp': time.time(),
            'board_state': self.board.get_board_copy(),
            'scores': self.board.get_scores()
        }
        self.move_history.append(move)
    
    def _record_pass(self, player_color: int):
        """Record a pass in the game history"""
        move = {
            'type': 'pass',
            'player': player_color,
            'timestamp': time.time(),
            'scores': self.board.get_scores()
        }
        self.move_history.append(move)
    
    def get_valid_moves(self, player_color: int) -> List[Tuple[int, int]]:
        """Get valid moves for a player"""
        return OthelloRules.get_valid_moves(self.board, player_color)
    
    def get_current_scores(self) -> Dict[int, int]:
        """Get current scores for both players"""
        return self.board.get_scores()
    
    def get_game_duration(self) -> Optional[float]:
        """Get game duration in seconds"""
        if self.game_start_time is None:
            return None
        
        end_time = self.game_end_time or time.time()
        return end_time - self.game_start_time
    
    def add_spectator(self, spectator_id: str):
        """Add a spectator to the game"""
        if spectator_id not in self.spectators:
            self.spectators.append(spectator_id)
    
    def remove_spectator(self, spectator_id: str):
        """Remove a spectator from the game"""
        if spectator_id in self.spectators:
            self.spectators.remove(spectator_id)
    
    def to_dict(self) -> Dict:
        """Convert game state to dictionary for serialization"""
        return {
            'game_id': self.game_id,
            'board': self.board.get_board_copy(),
            'players': {color: player.to_dict() for color, player in self.players.items()},
            'current_player': self.current_player,
            'status': self.status,
            'winner': self.winner,
            'scores': self.get_current_scores(),
            'valid_moves': self.get_valid_moves(self.current_player) if self.status == GAME_ACTIVE else [],
            'game_duration': self.get_game_duration(),
            'spectators': self.spectators,
            'move_count': len(self.move_history)
        }
    
    def get_board_state(self) -> List[List[int]]:
        """Get current board state"""
        return self.board.get_board_copy()
    
    def is_player_turn(self, player_color: int) -> bool:
        """Check if it's a specific player's turn"""
        return self.status == GAME_ACTIVE and self.current_player == player_color
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return f"Game {self.game_id}: {self.status}, Players: {len(self.players)}, Turn: {self.current_player}"