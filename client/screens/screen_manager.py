import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from client.screens.menu_screen import MenuScreen
from client.screens.login_screen import LoginScreen
from client.screens.register_screen import RegisterScreen
from client.screens.room_screen import RoomScreen
from client.screens.profile_screen import ProfileScreen
from client.screens.game_screen import ReversiGame, MultiplayerGameScreen

class ScreenManager:
    def __init__(self):
        self.current_screen = None
        self.running = True
        self.screen_stack = []  # For back navigation
        self.user_data = None  # Store logged-in user data
        self.room_code = None  # Store room code for code screen
        self.network_client = None  # Store network client for multiplayer games
        
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
    
    def set_room_code(self, room_code):
        """Set the room code for the code screen"""
        self.room_code = room_code
    
    def run(self):
        """Main application loop"""
        self.current_screen = "menu"
        
        while self.running:
            if self.current_screen == "menu":
                screen = MenuScreen(user_data=self.user_data)
                action = screen.run()
                
            elif self.current_screen == "login":
                screen = LoginScreen()
                result = screen.run()
                # Handle tuple result from login (action, user_data)
                if isinstance(result, tuple):
                    action, self.user_data = result
                else:
                    action = result
                
            elif self.current_screen == "register":
                screen = RegisterScreen()
                action = screen.run()
                
            elif self.current_screen == "room_select":
                screen = RoomScreen(user_data=self.user_data)  # Pass user_data to RoomScreen
                result = screen.run()
                # Handle tuple result from room screen (action, room_code)
                if isinstance(result, tuple):
                    action, self.room_code = result
                else:
                    action = result
                # Store network client from room screen for multiplayer game
                if hasattr(screen, 'network_client'):
                    self.network_client = screen.network_client
                
            elif self.current_screen == "profile":
                screen = ProfileScreen(user_data=self.user_data)
                action = screen.run()
                
            elif self.current_screen == "single_player" or self.current_screen == "game":
                screen = ReversiGame(board_size=8)
                action = screen.run()
                
            elif self.current_screen == "multiplayer_game":
                # For multiplayer game, use MultiplayerGameScreen with network client
                network_client = getattr(self, 'network_client', None)
                screen = MultiplayerGameScreen(network_client=network_client, user_data=self.user_data)
                action = screen.run()
                
            elif self.current_screen == "code":
                # Handle room code screen - for now redirect to room_select
                # This can be expanded later with a dedicated code screen
                self.current_screen = "room_select"
                continue

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
                
            elif action == "room_screen":
                self.push_screen("room_select")
                
            elif action == "profile":
                self.push_screen("profile")
                
            elif action == "single_player":
                self.push_screen("single_player")
                
            elif action == "game":
                self.push_screen("game")
                
            elif action == "multiplayer_game":
                self.push_screen("multiplayer_game")
                
            elif action == "code":
                self.push_screen("code")
                
            elif action == "continue":
                # Continue from code screen to waiting/game screen
                self.push_screen("multiplayer_game")
                
            # elif action == "guest":
                # Guest can go directly to room selection or single player
                # self.push_screen("room_select")
                
            elif action == "menu":
                self.current_screen = "menu"
                self.screen_stack.clear()
                
            elif action == "quit_account":
                # Clear user data and return to menu
                self.user_data = None
                self.current_screen = "menu"
                self.screen_stack.clear()
                
            else:
                # Unknown action, stay on current screen
                pass
        
        # Cleanup
        pygame.quit()
        sys.exit()