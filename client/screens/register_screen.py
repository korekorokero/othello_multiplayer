import pygame
import sys
from constants import *
from utils.utils import initialize_pygame, create_fonts
from ui.form_elements import InputField, Button, MessageBox
from ui.common_ui import ScreenHeader, BackButton

class RegisterScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.screen = initialize_pygame()
        self.fonts = create_fonts()
        
        # UI Elements
        self.header = ScreenHeader("OTHELLO REGISTER", "Create a new account")
        self.back_button = BackButton()
        
        # Form elements
        form_width = 300
        form_x = (width - form_width) // 2
        
        self.username_field = InputField(form_x, 180, form_width, 40, "Username")
        self.email_field = InputField(form_x, 230, form_width, 40, "Email")
        self.password_field = InputField(form_x, 280, form_width, 40, "Password")
        self.confirm_password_field = InputField(form_x, 330, form_width, 40, "Confirm Password")
        
        self.register_button = Button(form_x, 390, form_width, 40, "REGISTER", "register")
        self.login_button = Button(form_x, 440, form_width, 40, "Go to Login", "login")
        
        self.message_box = MessageBox("")
        
        self.clock = pygame.time.Clock()
        self.running = True
    
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
                    return self.attempt_register()
            
            # Handle UI events
            back_action = self.back_button.handle_event(event)
            if back_action:
                return back_action
            
            register_action = self.register_button.handle_event(event)
            if register_action == "register":
                return self.attempt_register()
            
            login_action = self.login_button.handle_event(event)
            if login_action:
                return login_action
            
            # Handle form inputs
            self.username_field.handle_event(event)
            self.email_field.handle_event(event)
            self.password_field.handle_event(event)
            self.confirm_password_field.handle_event(event)
        
        # Update UI elements
        self.username_field.update(dt)
        self.email_field.update(dt)
        self.password_field.update(dt)
        self.confirm_password_field.update(dt)
        self.message_box.update(dt)
        
        return None
    
    def attempt_register(self):
        """Attempt to register with provided information"""
        username = self.username_field.get_text().strip()
        email = self.email_field.get_text().strip()
        password = self.password_field.get_text().strip()
        confirm_password = self.confirm_password_field.get_text().strip()
        
        # Validation
        if not username:
            self.message_box.show("Please enter username", "error")
            return None
        
        if len(username) < 3:
            self.message_box.show("Username must be at least 3 characters", "error")
            return None
        
        if not email or "@" not in email:
            self.message_box.show("Please enter valid email", "error")
            return None
        
        if len(password) < 6:
            self.message_box.show("Password must be at least 6 characters", "error")
            return None
        
        if password != confirm_password:
            self.message_box.show("Passwords do not match", "error")
            return None
        
        # Here you would normally register with server
        print(f"Register attempt: {username}, {email}")
        self.message_box.show("Registration successful!", "success")
        
        # Clear form
        self.username_field.clear()
        self.email_field.clear()
        self.password_field.clear()
        self.confirm_password_field.clear()
        
        return "login"
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw all UI elements
        self.header.draw(self.screen, self.width)
        self.back_button.draw(self.screen)
        
        self.username_field.draw(self.screen)
        self.email_field.draw(self.screen)
        self.password_field.draw(self.screen)
        self.confirm_password_field.draw(self.screen)
        
        self.register_button.draw(self.screen)
        self.login_button.draw(self.screen)
        
        self.message_box.draw(self.screen, self.width // 2 - 100, 500)
        
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