import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from client.constants import *
from client.network import NetworkClient

# Simple UI helper classes (same as register_screen)
class SimpleInputField:
    def __init__(self, x, y, width, height, placeholder, is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, 32)
        self.is_password = is_password
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
                
    def update(self, dt):
        pass
        
    def draw(self, screen):
        color = (100, 100, 100) if self.active else (70, 70, 70)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        if self.text:
            display_text = "*" * len(self.text) if self.is_password else self.text
            text_color = (255, 255, 255)
        else:
            display_text = self.placeholder
            text_color = (150, 150, 150)
            
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 10))
        
    def get_text(self):
        return self.text
        
    def clear(self):
        self.text = ""

class SimpleButton:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
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
        color = COLORS['button_hover'] if self.hovered else COLORS['button']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
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

class LoginScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Othello - Login")
        
        # Network client
        self.network_client = NetworkClient()
        
        # Form elements with improved spacing
        form_width = 300
        form_x = (width - form_width) // 2
        
        # Input fields with better vertical spacing (12px between each)
        self.username_field = SimpleInputField(form_x, 190, form_width, 40, "Username")
        self.password_field = SimpleInputField(form_x, 242, form_width, 40, "Password", is_password=True)
        
        # Menu buttons with improved spacing
        button_width = 300
        button_height = 50
        button_x = (width - button_width) // 2
        button_spacing = 80
        start_y = 200
        
        # Add more spacing before buttons (90px gap)
        self.login_button = SimpleButton(button_x, start_y + 2*button_spacing, button_width, button_height, "LOGIN", "login")
        
        # Consistent gap between buttons (20px each)
        self.register_button = SimpleButton(button_x, start_y + 3*button_spacing, button_width, button_height, "Go to Register", "register")
        self.back_button = SimpleButton(50, 50, 100, 40, "← Back", "back")
        
        self.message_box = SimpleMessageBox()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.next_screen = None
        self.login_in_progress = False
        self.logged_in_user_data = None
    
    def handle_events(self):
        """Handle pygame events"""
        dt = self.clock.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_RETURN:
                    return self.attempt_login()
            
            # Handle UI events
            back_action = self.back_button.handle_event(event)
            if back_action:
                return back_action
            
            login_action = self.login_button.handle_event(event)
            if login_action == "login":
                return self.attempt_login()
            
            register_action = self.register_button.handle_event(event)
            if register_action:
                return register_action
            
            
            # Handle form inputs
            self.username_field.handle_event(event)
            self.password_field.handle_event(event)
        
        # Update UI elements
        self.username_field.update(dt)
        self.password_field.update(dt)
        self.message_box.update(dt)
        
        return None
    
    def attempt_login(self):
        """Attempt to login with provided credentials"""
        if self.login_in_progress:
            return None
            
        username = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        
        if not username:
            self.message_box.show("Please enter username", "error")
            return None
        
        if not password:
            self.message_box.show("Please enter password", "error")
            return None
        
        # Connect to server if not connected
        if not self.network_client.connected:
            self.message_box.show("Connecting to server...", "info")
            if not self.network_client.connect():
                self.message_box.show("Failed to connect to server", "error")
                return None
        
        # Set login in progress
        self.login_in_progress = True
        self.message_box.show("Logging in...", "info")
        
        # Send login request to server
        def login_callback(success, user_data):
            self.login_in_progress = False
            if success:
                self.logged_in_user_data = user_data
                self.message_box.show("Login successful!", "success")
                self.next_screen = "menu"  # Changed from "profile" to "menu"
                self.running = False  # Stop the loop to return to menu
            else:
                self.message_box.show("Invalid username or password", "error")
        
        self.network_client.login_user(username, password, login_callback)
        return None
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw header
        title_text = self.title_font.render("OTHELLO LOGIN", True, COLORS['text'])
        subtitle_text = self.subtitle_font.render("Enter your credentials to play", True, COLORS['text'])
        
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 120))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw all UI elements
        self.back_button.draw(self.screen)
        
        self.username_field.draw(self.screen)
        self.password_field.draw(self.screen)
        
        self.login_button.draw(self.screen)
        self.register_button.draw(self.screen)
        
        # Draw message box
        self.message_box.draw(self.screen, self.width // 2, 530)
        
        pygame.display.flip()
    
    def run(self):
        """Main screen loop"""
        while self.running:
            action = self.handle_events()
            if action:
                # If login was successful, return tuple with user data
                if action == "menu" and self.logged_in_user_data:
                    return ("menu", self.logged_in_user_data)
                return action
            
            # Check if login completed successfully
            if self.next_screen == "menu" and self.logged_in_user_data:
                return ("menu", self.logged_in_user_data)
            
            self.update_display()
            self.clock.tick(60)
        
        # If login was successful, return to menu with user data
        if self.logged_in_user_data:
            return ("menu", self.logged_in_user_data)
        
        return "quit"