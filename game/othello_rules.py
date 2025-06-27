# game/othello_rules.py
"""
Core Othello game rules and logic implementation
This module contains all the pure game logic, independent of any UI or network code
"""

from typing import List, Tuple, Set
from shared.constants import DIRECTIONS, EMPTY, BLACK, WHITE
from .othello_board import OthelloBoard

class OthelloRules:
    """
    Implements the core rules and logic for Othello game
    """
    
    @staticmethod
    def is_valid_move(board: OthelloBoard, row: int, col: int, player: int) -> bool:
        """
        Check if a move is valid according to Othello rules
        
        Args:
            board: Current board state
            row: Row coordinate for the move
            col: Column coordinate for the move
            player: Player making the move (BLACK or WHITE)
            
        Returns:
            True if move is valid, False otherwise
        """
        # Check if position is on the board and empty
        if not board.is_valid_position(row, col) or not board.is_empty(row, col):
            return False
        
        # Check if at least one piece can be flipped
        return len(OthelloRules.get_flipped_pieces(board, row, col, player)) > 0
    
    @staticmethod
    def get_flipped_pieces(board: OthelloBoard, row: int, col: int, player: int) -> List[Tuple[int, int]]:
        """
        Get all pieces that would be flipped by placing a piece at the given position
        
        Args:
            board: Current board state
            row: Row coordinate for the move
            col: Column coordinate for the move
            player: Player making the move
            
        Returns:
            List of (row, col) coordinates that would be flipped
        """
        if not board.is_valid_position(row, col) or not board.is_empty(row, col):
            return []
        
        opponent = WHITE if player == BLACK else BLACK
        flipped_pieces = []
        
        # Check all 8 directions
        for dr, dc in DIRECTIONS:
            direction_flips = OthelloRules._get_flips_in_direction(
                board, row, col, dr, dc, player, opponent
            )
            flipped_pieces.extend(direction_flips)
        
        return flipped_pieces
    
    @staticmethod
    def _get_flips_in_direction(board: OthelloBoard, start_row: int, start_col: int, 
                               dr: int, dc: int, player: int, opponent: int) -> List[Tuple[int, int]]:
        """
        Get pieces that would be flipped in a specific direction
        
        Args:
            board: Current board state
            start_row: Starting row coordinate
            start_col: Starting column coordinate
            dr: Row direction (-1, 0, or 1)
            dc: Column direction (-1, 0, or 1)
            player: Player making the move
            opponent: Opponent player
            
        Returns:
            List of coordinates that would be flipped in this direction
        """
        flips = []
        row, col = start_row + dr, start_col + dc
        
        # Look for opponent pieces in this direction
        while board.is_valid_position(row, col) and board.get_cell(row, col) == opponent:
            flips.append((row, col))
            row += dr
            col += dc
        
        # Check if we found a player piece to close the line
        if (board.is_valid_position(row, col) and 
            board.get_cell(row, col) == player and 
            len(flips) > 0):
            return flips
        
        return []
    
    @staticmethod
    def make_move(board: OthelloBoard, row: int, col: int, player: int) -> bool:
        """
        Make a move on the board if it's valid
        
        Args:
            board: Current board state (will be modified)
            row: Row coordinate for the move
            col: Column coordinate for the move
            player: Player making the move
            
        Returns:
            True if move was successful, False otherwise
        """
        if not OthelloRules.is_valid_move(board, row, col, player):
            return False
        
        # Get all pieces to flip
        flipped_pieces = OthelloRules.get_flipped_pieces(board, row, col, player)
        
        # Place the new piece
        board.set_cell(row, col, player)
        
        # Flip all captured pieces
        for flip_row, flip_col in flipped_pieces:
            board.set_cell(flip_row, flip_col, player)
        
        return True
    
    @staticmethod
    def get_valid_moves(board: OthelloBoard, player: int) -> List[Tuple[int, int]]:
        """
        Get all valid moves for a player
        
        Args:
            board: Current board state
            player: Player to get moves for
            
        Returns:
            List of (row, col) coordinates where player can move
        """
        valid_moves = []
        
        for row in range(board.size):
            for col in range(board.size):
                if OthelloRules.is_valid_move(board, row, col, player):
                    valid_moves.append((row, col))
        
        return valid_moves
    
    @staticmethod
    def has_valid_moves(board: OthelloBoard, player: int) -> bool:
        """
        Check if a player has any valid moves
        
        Args:
            board: Current board state
            player: Player to check
            
        Returns:
            True if player has valid moves, False otherwise
        """
        for row in range(board.size):
            for col in range(board.size):
                if OthelloRules.is_valid_move(board, row, col, player):
                    return True
        return False
    
    @staticmethod
    def is_game_over(board: OthelloBoard) -> bool:
        """
        Check if the game is over (no valid moves for either player or board is full)
        
        Args:
            board: Current board state
            
        Returns:
            True if game is over, False otherwise
        """
        if board.is_full():
            return True
        
        # Check if either player has valid moves
        return not (OthelloRules.has_valid_moves(board, BLACK) or 
                   OthelloRules.has_valid_moves(board, WHITE))
    
    @staticmethod
    def get_winner(board: OthelloBoard) -> int:
        """
        Determine the winner of the game
        
        Args:
            board: Current board state
            
        Returns:
            BLACK if black wins, WHITE if white wins, EMPTY if tie
        """
        scores = board.get_scores()
        black_score = scores[BLACK]
        white_score = scores[WHITE]
        
        if black_score > white_score:
            return BLACK
        elif white_score > black_score:
            return WHITE
        else:
            return EMPTY  # Tie
    
    @staticmethod
    def simulate_move(board: OthelloBoard, row: int, col: int, player: int) -> OthelloBoard:
        """
        Simulate a move without modifying the original board
        
        Args:
            board: Current board state
            row: Row coordinate for the move
            col: Column coordinate for the move
            player: Player making the move
            
        Returns:
            New board with the move applied, or None if move is invalid
        """
        if not OthelloRules.is_valid_move(board, row, col, player):
            return None
        
        # Create a copy of the board
        new_board = OthelloBoard()
        new_board.set_board(board.get_board_copy())
        
        # Make the move on the copy
        OthelloRules.make_move(new_board, row, col, player)
        
        return new_board
    
    @staticmethod
    def count_flipped_pieces(board: OthelloBoard, row: int, col: int, player: int) -> int:
        """
        Count how many pieces would be flipped by a move
        
        Args:
            board: Current board state
            row: Row coordinate for the move
            col: Column coordinate for the move
            player: Player making the move
            
        Returns:
            Number of pieces that would be flipped
        """
        return len(OthelloRules.get_flipped_pieces(board, row, col, player))
    
    @staticmethod
    def get_corner_positions() -> List[Tuple[int, int]]:
        """
        Get all corner positions on the board (strategically important)
        
        Returns:
            List of corner coordinates
        """
        return [(0, 0), (0, 7), (7, 0), (7, 7)]
    
    @staticmethod
    def get_edge_positions() -> List[Tuple[int, int]]:
        """
        Get all edge positions on the board (excluding corners)
        
        Returns:
            List of edge coordinates
        """
        edges = []
        size = 8
        
        # Top and bottom edges
        for col in range(1, size - 1):
            edges.append((0, col))      # Top edge
            edges.append((size - 1, col))  # Bottom edge
        
        # Left and right edges  
        for row in range(1, size - 1):
            edges.append((row, 0))      # Left edge
            edges.append((row, size - 1))  # Right edge
        
        return edges