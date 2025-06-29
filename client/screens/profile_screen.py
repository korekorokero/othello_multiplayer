import pygame
import sys
import os
from datetime import datetime
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

class SimpleMessageBox:
    def __init__(self):
        self.message = ""
        self.message_type = "info"
        self.timer = 0
        self.font = pygame.font.Font(None, 28)
        
    def show(self, message, msg_type="info"):
        self.message = message
        self.message_type = msg_type
        self.timer = 3000  # 3 seconds
        
    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            
    def draw(self, screen, x, y):
        if self.timer > 0 and self.message:
            color = (0, 255, 0) if self.message_type == "success" else (255, 0, 0) if self.message_type == "error" else (255, 255, 0)
            text_surface = self.font.render(self.message, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)

class ProfileScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, user_data=None):
        self.width = width
        self.height = height
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Othello - Profile")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.section_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 24)
        
        # Use real user data if provided, otherwise use default
        if user_data:
            self.user_data = {
                'username': user_data.get('username', 'Unknown'),
                'email': user_data.get('email', 'unknown@example.com'),
                'created_at': user_data.get('created_at', '2024-01-01T00:00:00Z'),
                'score': user_data.get('score', 0),
                'games_played': user_data.get('games_played', 0),
                'games_won': user_data.get('games_won', 0),
                'games_lost': user_data.get('games_lost', 0),
                'games_drawn': user_data.get('games_drawn', 0),
                'win_rate': user_data.get('win_rate', 0.0)
            }
        else:
            # Default data for demonstration
            self.user_data = {
                'username': 'Player123',  
                'email': 'player123@example.com',
                'created_at': '2024-01-15T10:30:00Z',
                'score': 1250,
                'games_played': 45,
                'games_won': 28,
                'games_lost': 15,
                'games_drawn': 2,
                'win_rate': 62.2
            }
        
        # Profile card dimensions
        self.card_width = 500
        self.card_height = 400
        self.card_x = (width - self.card_width) // 2
        self.card_y = 140
        
        # Buttons
        button_width = 200
        button_height = 50
        button_x = (width - button_width) // 2
        button_spacing = 60
        
        self.play_button = SimpleButton(button_x, self.card_y + self.card_height + 30, 
                                       button_width, button_height, "PLAY GAME", "room_select")
        
        self.back_button = SimpleButton(button_x, self.card_y + self.card_height + 30 + button_spacing,
                                       button_width, button_height, "BACK TO MENU", "back")
        
        # self.quit_button = SimpleButton(button_x, self.card_y + self.card_height + 30 + 2*button_spacing,
        #                                button_width, button_height, "QUIT ACCOUNT", "quit_account",
        #                                bg_color=(255, 182, 193), hover_color=(255, 105, 180), text_color=(139, 0, 0))
        
        self.message_box = SimpleMessageBox()
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def format_date(self, date_string):
        """Format ISO date string to readable format"""
        try:
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return date_obj.strftime("%B %d, %Y")
        except:
            return "Unknown"
    
    def draw_profile_card(self):
        """Draw the profile information card"""
        # Card background - using solid colors instead of RGBA
        card_rect = pygame.Rect(self.card_x, self.card_y, self.card_width, self.card_height)
        
        # Light gray background for the card
        pygame.draw.rect(self.screen, (240, 240, 240), card_rect)
        # Dark border
        pygame.draw.rect(self.screen, (50, 50, 50), card_rect, 3)
        
        # Profile information
        info_x = self.card_x + 30
        info_y = self.card_y + 30
        line_height = 35
        
        # Profile sections
        sections = [
            ("ACCOUNT INFORMATION", [
                f"Username: {self.user_data['username']}",
                f"Email: {self.user_data['email']}",
                f"Member Since: {self.format_date(self.user_data['created_at'])}"
            ]),
            ("GAME STATISTICS", [
                f"Current Score: {self.user_data['score']} points",
                f"Games Played: {self.user_data['games_played']}",
                f"Games Won: {self.user_data['games_won']}",
                f"Games Lost: {self.user_data['games_lost']}",
                f"Games Drawn: {self.user_data['games_drawn']}",
                f"Win Rate: {self.user_data['win_rate']}%"
            ])
        ]
        
        current_y = info_y
        
        for section_title, section_items in sections:
            # Section title with blue color for contrast
            title_surface = self.section_font.render(section_title, True, (0, 100, 200))  # Blue color
            self.screen.blit(title_surface, (info_x, current_y))
            current_y += line_height
            
            # Section items with dark text
            for item in section_items:
                item_surface = self.info_font.render(item, True, (50, 50, 50))  # Dark gray text
                self.screen.blit(item_surface, (info_x + 20, current_y))
                current_y += line_height - 5
            
            current_y += 15  # Extra space between sections
    
    def handle_events(self):
        """Handle pygame events"""
        dt = self.clock.get_time()
        
        for event in pygame.event.get():
            # if event.type == pygame.QUIT:
            #     self.running = False
            #     return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "room_select"
            
            # Handle UI events
            play_action = self.play_button.handle_event(event)
            if play_action:
                return play_action
            
            back_action = self.back_button.handle_event(event)
            if back_action:
                return back_action
                
            # quit_action = self.quit_button.handle_event(event)
            # if quit_action:
            #     return quit_action
        
        # Update UI elements
        self.message_box.update(dt)
        
        return None
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw header
        title_text = self.title_font.render("PLAYER PROFILE", True, COLORS['text'])
        subtitle_text = self.subtitle_font.render("Welcome to your gaming dashboard!", True, COLORS['text'])
        
        title_rect = title_text.get_rect(center=(self.width // 2, 60))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 100))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw profile card
        self.draw_profile_card()
        
        # Draw buttons
        self.play_button.draw(self.screen)
        self.back_button.draw(self.screen)
        # self.quit_button.draw(self.screen)
        
        # Draw message box if needed
        self.message_box.draw(self.screen, self.width // 2, self.height - 50)
        
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
    
    def set_user_data(self, user_data):
        """Update user data for the profile screen"""
        self.user_data = user_data