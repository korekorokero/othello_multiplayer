import pygame
from constants import *

def initialize_pygame():
    """Initialize pygame and return screen object"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Othello Game")
    return screen

def create_fonts():
    """Create and return font objects"""
    return {
        'large': pygame.font.Font(None, FONT_LARGE),
        'medium': pygame.font.Font(None, FONT_MEDIUM),
        'small': pygame.font.Font(None, FONT_SMALL)
    }

def get_cell_from_mouse(mouse_pos, board_x, board_y, cell_size):
    """Convert mouse position to board cell coordinates"""
    mouse_x, mouse_y = mouse_pos
    board_width = BOARD_SIZE * cell_size
    
    # Check if mouse is within board boundaries
    if (board_x <= mouse_x <= board_x + board_width and
        board_y <= mouse_y <= board_y + board_width):
        
        col = (mouse_x - board_x) // cell_size
        row = (mouse_y - board_y) // cell_size
        
        # Ensure we're within valid range
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
    
    return None