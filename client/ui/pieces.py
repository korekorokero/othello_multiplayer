import pygame
from constants import *

class Pieces:
    def __init__(self, board):
        self.board = board
        self.piece_radius = self.board.cell_size // 2 - PIECE_RADIUS_OFFSET
    
    def draw(self, screen):
        """Draw all pieces on the board"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece_type = self.board.get_piece(row, col)
                if piece_type != EMPTY:
                    self._draw_single_piece(screen, row, col, piece_type)
    
    def _draw_single_piece(self, screen, row, col, piece_type):
        """Draw a single piece at the specified position"""
        x, y = self.board.get_cell_center(row, col)
        
        # Choose color based on piece type
        if piece_type == BLACK_PIECE:
            color = COLORS['black_piece']
        elif piece_type == WHITE_PIECE:
            color = COLORS['white_piece']
        else:
            return  # Invalid piece type
        
        # Draw piece
        pygame.draw.circle(screen, color, (x, y), self.piece_radius)
        pygame.draw.circle(screen, COLORS['grid_lines'], (x, y), self.piece_radius, 2)
    
    def draw_preview_piece(self, screen, row, col, piece_type, alpha=128):
        """Draw a semi-transparent preview piece"""
        if not self.board.is_valid_position(row, col):
            return
        
        x, y = self.board.get_cell_center(row, col)
        
        # Choose color based on piece type
        if piece_type == BLACK_PIECE:
            color = COLORS['black_piece']
        elif piece_type == WHITE_PIECE:
            color = COLORS['white_piece']
        else:
            return
        
        # Create a surface with alpha
        piece_surface = pygame.Surface((self.piece_radius * 2, self.piece_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(piece_surface, (*color, alpha), 
                         (self.piece_radius, self.piece_radius), self.piece_radius)
        
        # Blit the surface to the screen