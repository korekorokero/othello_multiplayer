# game/othello_board.py
"""
Othello board data structure and basic operations
"""

from typing import List, Tuple, Optional
from shared.constants import BOARD_SIZE, EMPTY, BLACK, WHITE

class OthelloBoard:
    """
    Represents the Othello game board with basic operations
    """
    
    def __init__(self):
        """Initialize an empty 8x8 board"""
        self.size = BOARD_SIZE
        self.board = self._create_empty_board()
        self._setup_initial_position()
    
    def _create_empty_board(self) -> List[List[int]]:
        """Create an empty board filled with EMPTY values"""
        return [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
    
    def _setup_initial_position(self):
        """Set up the initial Othello position with 4 pieces in the center"""
        center = self.size // 2
        # Initial position: WB / BW pattern in center
        self.board[center - 1][center - 1] = WHITE  # (3,3)
        self.board[center - 1][center] = BLACK      # (3,4)
        self.board[center][center - 1] = BLACK      # (4,3)
        self.board[center][center] = WHITE          # (4,4)
    
    def get_cell(self, row: int, col: int) -> int:
        """
        Get the value of a cell on the board
        
        Args:
            row: Row coordinate (0-based)
            col: Column coordinate (0-based)
            
        Returns:
            Cell value (EMPTY, BLACK, or WHITE)
            
        Raises:
            IndexError: If coordinates are out of bounds
        """
        if not self.is_valid_position(row, col):
            raise IndexError(f"Position ({row}, {col}) is out of bounds")
        return self.board[row][col]
    
    def set_cell(self, row: int, col: int, value: int):
        """
        Set the value of a cell on the board
        
        Args:
            row: Row coordinate (0-based)
            col: Column coordinate (0-based)
            value: Cell value to set (EMPTY, BLACK, or WHITE)
            
        Raises:
            IndexError: If coordinates are out of bounds
            ValueError: If value is not valid
        """
        if not self.is_valid_position(row, col):
            raise IndexError(f"Position ({row}, {col}) is out of bounds")
        
        if value not in [EMPTY, BLACK, WHITE]:
            raise ValueError(f"Invalid cell value: {value}")
        
        self.board[row][col] = value
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """
        Check if the given position is within board bounds
        
        Args:
            row: Row coordinate
            col: Column coordinate
            
        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= row < self.size and 0 <= col < self.size
    
    def is_empty(self, row: int, col: int) -> bool:
        """
        Check if a cell is empty
        
        Args:
            row: Row coordinate
            col: Column coordinate
            
        Returns:
            True if cell is empty, False otherwise
        """
        return self.is_valid_position(row, col) and self.board[row][col] == EMPTY
    
    def get_board_copy(self) -> List[List[int]]:
        """
        Get a deep copy of the current board state
        
        Returns:
            2D list representing the board
        """
        return [row[:] for row in self.board]
    
    def set_board(self, new_board: List[List[int]]):
        """
        Set the board to a new state
        
        Args:
            new_board: 2D list representing the new board state
            
        Raises:
            ValueError: If board dimensions are incorrect
        """
        if len(new_board) != self.size or any(len(row) != self.size for row in new_board):
            raise ValueError(f"Board must be {self.size}x{self.size}")
        
        # Validate all cell values
        for row in new_board:
            for cell in row:
                if cell not in [EMPTY, BLACK, WHITE]:
                    raise ValueError(f"Invalid cell value: {cell}")
        
        self.board = [row[:] for row in new_board]
    
    def count_pieces(self, player: int) -> int:
        """
        Count the number of pieces for a specific player
        
        Args:
            player: Player color (BLACK or WHITE)
            
        Returns:
            Number of pieces for the player
        """
        count = 0
        for row in self.board:
            for cell in row:
                if cell == player:
                    count += 1
        return count
    
    def get_scores(self) -> dict:
        """
        Get the current score for both players
        
        Returns:
            Dictionary with scores for BLACK and WHITE
        """
        return {
            BLACK: self.count_pieces(BLACK),
            WHITE: self.count_pieces(WHITE)
        }
    
    def is_full(self) -> bool:
        """
        Check if the board is completely filled
        
        Returns:
            True if board is full, False otherwise
        """
        for row in self.board:
            for cell in row:
                if cell == EMPTY:
                    return False
        return True
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """
        Get a list of all empty cell coordinates
        
        Returns:
            List of (row, col) tuples for empty cells
        """
        empty_cells = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == EMPTY:
                    empty_cells.append((row, col))
        return empty_cells
    
    def reset(self):
        """Reset the board to initial Othello position"""
        self.board = self._create_empty_board()
        self._setup_initial_position()
    
    def __str__(self) -> str:
        """
        String representation of the board for debugging
        
        Returns:
            String representation of the board
        """
        symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}
        result = []
        result.append("  " + "".join(f"{i}" for i in range(self.size)))
        for i, row in enumerate(self.board):
            row_str = f"{i} " + "".join(symbols[cell] for cell in row)
            result.append(row_str)
        return "\n".join(result)
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"OthelloBoard(size={self.size}, scores={self.get_scores()})"