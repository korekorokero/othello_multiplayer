import pygame
import sys
from constants import *
from utils.utils import initialize_pygame, create_fonts
from ui.form_elements import Button
from ui.common_ui import ScreenHeader

class MenuScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.screen = initialize_pygame()
        self.fonts = create_fonts()
        
        # UI Elements
        self.header = ScreenHeader("OTHELLO", "Welcome to the classic strategy game")
        
        # Menu buttons
        button_width = 250
        button_height = 50
        button_x = (width - button_width) // 2
        button_spacing = 70
        
        start_y = 200
        
        self.play_button = Button(button_x, start_y, button_width, button_height, "PLAY ONLINE", "login")
        self.single_button = Button(button_x, start_y + button_spacing, button_width, button_height, "SINGLE PLAYER", "single_player")
        self.register_button = Button(button_x, start_y + 2*button_spacing, button_width, button_height, "REGISTER", "register")
        self.quit_button = Button(button_x, start_y + 3*button_spacing, button_width, button_height, "QUIT", "quit")
        
        self.buttons = [self.play_button, self.single_button, self.register_button, self.quit_button]
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
            
            # Handle button events
            for button in self.buttons:
                action = button.handle_event(event)
                if action:
                    return action
        
        return None
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw header
        self.header.draw(self.screen, self.width)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw game info
        info_font = pygame.font.Font(None, FONT_SMALL)
        info_text = "A classic strategy game for two players"
        info_surface = info_font.render(info_text, True, COLORS['text'])
        info_rect = info_surface.get_rect(center=(self.width // 2, 520))
        self.screen.blit(info_surface, info_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main screen loop"""
        while self.running:
            action = self.handle_events()
            if action:
                return action
            
            self.update_display()
            self.clock.tick(60)
        
        return "quit"