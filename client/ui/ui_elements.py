import pygame
from constants import *

class UIElements:
    def __init__(self, screen_width, screen_height, fonts, board_info):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fonts = fonts
        self.board_info = board_info
        
        # Game state for display
        self.current_player = "Black"
        self.score_black = 2
        self.score_white = 2
        
        # Button setup
        self.buttons = self._setup_buttons()
    
    def _setup_buttons(self):
        """Setup button positions and properties"""
        button_y = self.board_info['y'] + self.board_info['height'] + 90
        
        return [
            {
                "text": "New Game",
                "rect": pygame.Rect(self.board_info['x'], button_y, BUTTON_WIDTH, BUTTON_HEIGHT),
                "action": "new_game"
            },
            {
                "text": "Restart", 
                "rect": pygame.Rect(self.board_info['x'] + BUTTON_WIDTH + BUTTON_SPACING, 
                                  button_y, BUTTON_WIDTH, BUTTON_HEIGHT),
                "action": "restart"
            },
            {
                "text": "Quit",
                "rect": pygame.Rect(self.board_info['x'] + 2 * (BUTTON_WIDTH + BUTTON_SPACING), 
                                  button_y, BUTTON_WIDTH, BUTTON_HEIGHT),
                "action": "quit"
            }
        ]
    
    def draw_header(self, screen):
        """Draw the game header with title and current player"""
        # Game title
        title_text = self.fonts['large'].render("OTHELLO", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 30))
        screen.blit(title_text, title_rect)
        
        # Current player indicator
        player_text = f"Current Player: {self.current_player}"
        player_surface = self.fonts['medium'].render(player_text, True, COLORS['text'])
        player_rect = player_surface.get_rect(center=(self.screen_width // 2, 55))
        screen.blit(player_surface, player_rect)
    
    def draw_score_panel(self, screen):
        """Draw the score panel"""
        panel_y = self.board_info['y'] + self.board_info['height'] + 20
        
        # Score background
        score_rect = pygame.Rect(self.board_info['x'], panel_y, self.board_info['width'], 60)
        pygame.draw.rect(screen, COLORS['button'], score_rect)
        pygame.draw.rect(screen, COLORS['grid_lines'], score_rect, 2)
        
        # Black score
        black_text = f"Black: {self.score_black}"
        black_surface = self.fonts['medium'].render(black_text, True, COLORS['text'])
        black_rect = black_surface.get_rect(center=(self.board_info['x'] + self.board_info['width'] // 4, panel_y + 30))
        screen.blit(black_surface, black_rect)
        
        # White score
        white_text = f"White: {self.score_white}"
        white_surface = self.fonts['medium'].render(white_text, True, COLORS['text'])
        white_rect = white_surface.get_rect(center=(self.board_info['x'] + 3 * self.board_info['width'] // 4, panel_y + 30))
        screen.blit(white_surface, white_rect)
    
    def draw_buttons(self, screen):
        """Draw game control buttons"""
        for button in self.buttons:
            # Button background
            pygame.draw.rect(screen, COLORS['button'], button['rect'])
            pygame.draw.rect(screen, COLORS['grid_lines'], button['rect'], 2)
            
            # Button text
            text_surface = self.fonts['small'].render(button['text'], True, COLORS['text'])
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect)
    
    def handle_button_click(self, mouse_pos):
        """Handle button click events and return action"""
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                return button['action']
        return None
    
    def update_scores(self, black_score, white_score):
        """Update the displayed scores"""
        self.score_black = black_score
        self.score_white = white_score
    
    def set_current_player(self, player):
        """Set the current player for display"""
        self.current_player = player