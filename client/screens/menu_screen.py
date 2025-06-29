import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from client.constants import *

# Simple UI helper classes
class SimpleButton:
    def __init__(self, x, y, width, height, text, action, bg_color=None, hover_color=None, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.bg_color = bg_color or COLORS['button']
        self.hover_color = hover_color or COLORS['button_hover']
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)
        self.hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None
        
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class MenuScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, user_data=None):
        self.width = width
        self.height = height
        self.user_data = user_data  # Store user data if logged in
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Othello - Main Menu")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.user_font = pygame.font.Font(None, 28)
        
        # Menu buttons with improved spacing
        button_width = 300
        button_height = 50
        button_x = (width - button_width) // 2
        button_spacing = 70
        start_y = 220
        
        # Create different menus based on login status
        if self.user_data:
            # Logged in user menu
            self.play_button = SimpleButton(button_x, start_y, button_width, button_height, "MULTI PLAYER", "room_select")
            self.single_player_button = SimpleButton(button_x, start_y + button_spacing, button_width, button_height, "SINGLE PLAYER", "single_player")
            self.profile_button = SimpleButton(button_x, start_y + 2*button_spacing, button_width, button_height, "PROFILE", "profile")
            self.logout_button = SimpleButton(button_x, start_y + 3*button_spacing, button_width, button_height, "LOGOUT", "quit_account",
                                              bg_color=(255, 182, 193), hover_color=(255, 105, 180), text_color=(139, 0, 0))
            
            self.buttons = [self.play_button, self.single_player_button, self.profile_button, self.logout_button]
        else:
            # Guest/Not logged in menu
            self.login_button = SimpleButton(button_x, start_y, button_width, button_height, "LOGIN", "login")
            self.register_button = SimpleButton(button_x, start_y + button_spacing, button_width, button_height, "REGISTER", "register")
            self.quit_button = SimpleButton(button_x, start_y + 3*button_spacing, button_width, button_height, "QUIT", "quit", 
                                          bg_color=(255, 182, 193), hover_color=(255, 105, 180), text_color=(139, 0, 0))
            
            self.buttons = [self.login_button, self.register_button, self.quit_button]
            
            # Add login required message
            self.login_required_text = self.subtitle_font.render("User harus login", True, (255, 100, 100))  # Red text
        
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
        
        # Draw title and subtitle
        title_text = self.title_font.render("OTHELLO", True, COLORS['text'])
        subtitle_text = self.subtitle_font.render("Welcome to the classic strategy game", True, COLORS['text'])
        
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 120))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw user info if logged in
        if self.user_data:
            welcome_text = f"Welcome back, {self.user_data.get('username', 'Player')}!"
            user_surface = self.user_font.render(welcome_text, True, (255, 255, 0))  # Yellow text
            user_rect = user_surface.get_rect(center=(self.width // 2, 160))
            self.screen.blit(user_surface, user_rect)
        
        # Draw all buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw game info at bottom
        info_text = "A classic strategy game for two players"
        info_surface = self.subtitle_font.render(info_text, True, COLORS['text'])
        info_rect = info_surface.get_rect(center=(self.width // 2, self.height - 50))
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