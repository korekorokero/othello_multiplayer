import pygame
from constants import *

class Board:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate board dimensions
        self.board_width = min(screen_width - 2 * BOARD_MARGIN, screen_height - 150)
        self.cell_size = self.board_width // BOARD_SIZE
        self.board_width = self.cell_size * BOARD_SIZE  # Adjust for exact fit
        
        # Board position (centered)
        self.board_x = (screen_width - self.board_width) // 2
        self.board_y = 80
        
        # Initialize board state
        self.board_state = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self._setup_initial_pieces()
    
    def _setup_initial_pieces(self):
        """Set up the initial Othello piece configuration"""
        mid = BOARD_SIZE // 2
        self.board_state[mid-1][mid-1] = WHITE_PIECE
        self.board_state[mid-1][mid] = BLACK_PIECE
        self.board_state[mid][mid-1] = BLACK_PIECE
        self.board_state[mid][mid] = WHITE_PIECE
    
    def draw(self, screen):
        """Draw the board grid"""
        # Draw board background
        board_rect = pygame.Rect(self.board_x, self.board_y, self.board_width, self.board_width)
        pygame.draw.rect(screen, COLORS['board'], board_rect)
        
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            x = self.board_x + i * self.cell_size
            pygame.draw.line(screen, COLORS['grid_lines'], 
                           (x, self.board_y), (x, self.board_y + self.board_width), 2)
            
            # Horizontal lines
            y = self.board_y + i * self.cell_size
            pygame.draw.line(screen, COLORS['grid_lines'], 
                           (self.board_x, y), (self.board_x + self.board_width, y), 2)
    
    def get_board_info(self):
        """Return board positioning information"""
        return {
            'x': self.board_x,
            'y': self.board_y,
            'width': self.board_width,
            'height': self.board_width,
            'cell_size': self.cell_size
        }
    
    def get_cell_center(self, row, col):
        """Get the center coordinates of a specific cell"""
        x = self.board_x + col * self.cell_size + self.cell_size // 2
        y = self.board_y + row * self.cell_size + self.cell_size // 2
        return x, y
    
    def is_valid_position(self, row, col):
        """Check if the given position is valid on the board"""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE
    
    def get_piece(self, row, col):
        """Get the piece at the specified position"""
        if self.is_valid_position(row, col):
            return self.board_state[row][col]
        return None
    
    def set_piece(self, row, col, piece_type):
        """Set a piece at the specified position"""
        if self.is_valid_position(row, col):
            self.board_state[row][col] = piece_type
            return True
        return False