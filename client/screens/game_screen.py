import pygame
import sys
from constants import *
from utils.utils import initialize_pygame, create_fonts, get_cell_from_mouse
from ui.board import Board
from ui.pieces import Pieces
from ui.ui_elements import UIElements

class OthelloScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        """Initialize the Othello game screen"""
        self.width = width
        self.height = height
        self.screen = initialize_pygame()
        self.fonts = create_fonts()
        
        # Initialize game components
        self.board = Board(width, height)
        self.pieces = Pieces(self.board)
        self.ui = UIElements(width, height, self.fonts, self.board.get_board_info())
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_board_click(self, mouse_pos):
        """Handle clicks on the board"""
        board_info = self.board.get_board_info()
        cell = get_cell_from_mouse(mouse_pos, board_info['x'], board_info['y'], board_info['cell_size'])
        
        if cell:
            row, col = cell
            print(f"Clicked on cell: ({row}, {col})")
            # Here you would add game logic for placing pieces
            # For now, just demonstrate by placing a piece
            if self.board.get_piece(row, col) == EMPTY:
                # Alternate between black and white for demonstration
                current_piece = BLACK_PIECE if self.ui.current_player == "Black" else WHITE_PIECE
                self.board.set_piece(row, col, current_piece)
                
                # Switch player for demonstration
                self.ui.set_current_player("White" if self.ui.current_player == "Black" else "Black")
    
    def handle_button_click(self, mouse_pos):
        """Handle button clicks"""
        action = self.ui.handle_button_click(mouse_pos)
        
        if action == "new_game":
            print("New Game clicked")
            # Reset game state
            self.board = Board(self.width, self.height)
            self.pieces = Pieces(self.board)
            self.ui.set_current_player("Black")
            self.ui.update_scores(2, 2)
        elif action == "restart":
            print("Restart clicked")
            # Similar to new game for now
            self.board = Board(self.width, self.height)
            self.pieces = Pieces(self.board)
            self.ui.set_current_player("Black")
            self.ui.update_scores(2, 2)
        elif action == "quit":
            print("Quit clicked")
            self.running = False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Try button click first, then board click
                    self.handle_button_click(event.pos)
                    self.handle_board_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update_display(self):
        """Update the entire display"""
        # Clear screen
        self.screen.fill(COLORS['background'])
        
        # Draw all components
        self.ui.draw_header(self.screen)
        self.board.draw(self.screen)
        self.pieces.draw(self.screen)
        self.ui.draw_score_panel(self.screen)
        self.ui.draw_buttons(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update_display()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()