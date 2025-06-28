import pygame
import sys
from constants import *
from utils.utils import initialize_pygame, create_fonts
from ui.form_elements import InputField, Button, MessageBox
from ui.common_ui import ScreenHeader, BackButton

class LoginScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.screen = initialize_pygame()
        self.fonts = create_fonts()
        
        # UI Elements
        self.header = ScreenHeader("OTHELLO LOGIN", "Enter your credentials to play")
        self.back_button = BackButton()
        
        # Form elements
        form_width = 300
        form_x = (width - form_width) // 2
        
        self.username_field = InputField(form_x, 200, form_width, 40, "Username")
        self.password_field = InputField(form_x, 260, form_width, 40, "Password")
        
        self.login_button = Button(form_x, 320, form_width, 40, "LOGIN", "login")
        self.register_button = Button(form_x, 370, form_width, 40, "Go to Register", "register")
        self.guest_button = Button(form_x, 420, form_width, 40, "Play as Guest", "guest")
        
        self.message_box = MessageBox("")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.next_screen = None
    
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
            
            guest_action = self.guest_button.handle_event(event)
            if guest_action:
                return guest_action
            
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
        username = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        
        if not username:
            self.message_box.show("Please enter username", "error")
            return None
        
        if not password:
            self.message_box.show("Please enter password", "error")
            return None
        
        # Here you would normally validate with server
        # For demo, accept any non-empty credentials
        print(f"Login attempt: {username}")
        self.message_box.show("Login successful!", "success")
        
        # Return action to go to room selection
        return "room_select"
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw all UI elements
        self.header.draw(self.screen, self.width)
        self.back_button.draw(self.screen)
        
        self.username_field.draw(self.screen)
        self.password_field.draw(self.screen)
        
        self.login_button.draw(self.screen)
        self.register_button.draw(self.screen)
        self.guest_button.draw(self.screen)
        
        self.message_box.draw(self.screen, self.width // 2 - 100, 480)
        
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