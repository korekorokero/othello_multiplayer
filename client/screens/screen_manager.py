import pygame
import sys
from screens.menu_screen import MenuScreen
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.room_screen import RoomScreen
from screens.game_screen import OthelloScreen

class ScreenManager:
    def __init__(self):
        self.current_screen = None
        self.running = True
        self.screen_stack = []  # For back navigation
        
    def push_screen(self, screen_name):
        """Push current screen to stack and switch to new screen"""
        if self.current_screen:
            self.screen_stack.append(self.current_screen)
        self.current_screen = screen_name
    
    def pop_screen(self):
        """Return to previous screen"""
        if self.screen_stack:
            self.current_screen = self.screen_stack.pop()
        else:
            self.current_screen = "menu"
    
    def run(self):
        """Main application loop"""
        self.current_screen = "menu"
        
        while self.running:
            if self.current_screen == "menu":
                screen = MenuScreen()
                action = screen.run()
                
            elif self.current_screen == "login":
                screen = LoginScreen()
                action = screen.run()
                
            elif self.current_screen == "register":
                screen = RegisterScreen()
                action = screen.run()
                
            elif self.current_screen == "room_select":
                screen = RoomScreen()
                action = screen.run()
                
            elif self.current_screen == "single_player" or self.current_screen == "game":
                screen = OthelloScreen()
                action = screen.run()
                
            else:
                print(f"Unknown screen: {self.current_screen}")
                action = "quit"
            
            # Handle screen transitions
            if action == "quit":
                self.running = False
                
            elif action == "back":
                self.pop_screen()
                
            elif action == "login":
                self.push_screen("login")
                
            elif action == "register":
                self.push_screen("register")
                
            elif action == "room_select":
                self.push_screen("room_select")
                
            elif action == "single_player":
                self.push_screen("single_player")
                
            elif action == "game":
                self.push_screen("game")
                
            elif action == "guest":
                # Guest can go directly to room selection or single player
                self.push_screen("room_select")
                
            elif action == "menu":
                self.current_screen = "menu"
                self.screen_stack.clear()
                
            else:
                # Unknown action, stay on current screen
                pass
        
        # Cleanup
        pygame.quit()
        sys.exit()