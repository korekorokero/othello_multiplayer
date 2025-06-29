import pygame
import sys
import random
import string
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from client.constants import *
from client.network import NetworkClient

# Simple UI helper classes
class SimpleInputField:
    def __init__(self, x, y, width, height, placeholder):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, 32)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isalnum() and len(self.text) < 10:  # Limit room code length
                    self.text += event.unicode.upper()
                
    def update(self, dt):
        pass
        
    def draw(self, screen):
        color = (100, 100, 100) if self.active else (70, 70, 70)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        display_text = self.text if self.text else self.placeholder
        text_color = (255, 255, 255) if self.text else (150, 150, 150)
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 10))
        
    def get_text(self):
        return self.text
        
    def clear(self):
        self.text = ""

class SimpleButton:
    def __init__(self, x, y, width, height, text, action, bg_color=None, hover_color=None, text_color=(255, 255, 255), visible=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.bg_color = bg_color or COLORS['button']
        self.hover_color = hover_color or COLORS['button_hover']
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)
        self.hovered = False
        self.visible = visible
        
    def handle_event(self, event):
        if not self.visible:
            return None
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None
        
    def draw(self, screen):
        if not self.visible:
            return
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
        self.timer = 5000  # 5 seconds for room messages
        
    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            
    def draw(self, screen, x, y):
        if self.timer > 0 and self.message:
            color = (0, 255, 0) if self.message_type == "success" else (255, 0, 0) if self.message_type == "error" else (255, 255, 0)
            text_surface = self.font.render(self.message, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)

class RoomScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, user_data=None):
        self.width = width
        self.height = height
        self.user_data = user_data  # Store user data
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Othello - Game Rooms")
        
        # Network client
        self.network_client = NetworkClient()
        
        # Set user data to network client if available
        if self.user_data:
            self.network_client.user_data = self.user_data
            print(f"RoomScreen: User data set - {self.user_data}")
        else:
            print("RoomScreen: No user data provided")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.instruction_font = pygame.font.Font(None, 24)
        
        # Centered layout
        center_x = width // 2
        form_width = 300
        
        # Make Room section
        self.make_room_button = SimpleButton(center_x - form_width//2, 200, form_width, 50, "MAKE ROOM", "make_room")
        
        # Join Room section  
        self.join_code_field = SimpleInputField(center_x - form_width//2, 300, form_width, 40, "Enter Room ID")
        self.join_room_button = SimpleButton(center_x - form_width//2, 360, form_width, 50, "JOIN ROOM", "join_room")
        
        # Start Game button (appears when room is ready)
        self.start_game_button = SimpleButton(center_x - form_width//2, 420, form_width, 50, "START GAME", "start_game", visible=False)
        
        # Share code button (appears after room creation)
        # self.share_code_button = SimpleButton(center_x - form_width//2, 420, form_width, 50, "SHARE CODE", "share_code", visible=False)
        
        # Back button
        self.back_button = SimpleButton(50, 50, 100, 40, "← Back", "back")
        
        # Generated room ID display (initially hidden)
        self.generated_room_id = None
        self.show_room_id = False
        self.room_operation_in_progress = False
        
        # Room status and player info
        self.current_room_code = None
        self.room_players = []
        self.waiting_for_game = False
        
        self.message_box = SimpleMessageBox()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Setup network handlers
        self._setup_network_handlers()
    
    def _setup_network_handlers(self):
        """Setup network message handlers for room events"""
        def on_room_created(room_code):
            self.room_operation_in_progress = False
            if room_code:
                self.generated_room_id = room_code
                self.current_room_code = room_code
                self.show_room_id = True
                self.message_box.show(f"Room created! ID: {room_code}", "success")
                self.waiting_for_game = True
                # self.share_code_button.visible = True  # Show share code button
            else:
                self.message_box.show("Failed to create room", "error")
        
        def on_room_joined(success, room_code):
            self.room_operation_in_progress = False
            if success:
                self.current_room_code = room_code
                self.message_box.show("Successfully joined room!", "success")
                self.join_code_field.clear()
                self.waiting_for_game = True
                # Don't auto-redirect here, wait for room_update or game_start
            else:
                self.message_box.show("Failed to join room. Room may not exist or be full.", "error")
        
        def on_room_update(payload):
            """Handle room update from server"""
            print(f"Room update received: {payload}")
            self._handle_room_update(payload)
        
        def on_game_start(payload):
            """Handle game start from server"""
            print(f"Game start received: {payload}")
            self._handle_game_start(payload)
            # Auto-redirect to game screen immediately
            print("Setting timer for game redirect...")
            pygame.time.set_timer(pygame.USEREVENT + 3, 100)  # 0.1 second delay
        
        # Register network event handlers
        self.network_client.on_room_created = on_room_created
        self.network_client.on_room_joined = on_room_joined
        self.network_client.on_room_update = on_room_update
        self.network_client.on_game_start = on_game_start
        
        # Also register handlers for the message types
        self.network_client.register_handler('room_update', on_room_update)
        self.network_client.register_handler('game_start', on_game_start)
    
    def _handle_room_update(self, payload):
        """Handle room update messages from server"""
        room_code = payload.get('room_code')
        players_data = payload.get('players', [])
        
        print(f"Handling room update: room_code={room_code}, players={players_data}")
        
        if room_code:
            self.current_room_code = room_code
            
            # Extract player names from player data
            if isinstance(players_data, list) and players_data:
                if isinstance(players_data[0], dict):
                    # New format with player objects
                    self.room_players = [p.get('username', 'Unknown') for p in players_data]
                else:
                    # Old format with just names
                    self.room_players = players_data
            else:
                self.room_players = []
            
            print(f"Room players updated: {self.room_players}")
            
            if len(self.room_players) == 1:
                self.message_box.show(f"Waiting for another player... (Room: {room_code})", "info")
                self.waiting_for_game = True
            elif len(self.room_players) == 2:
                self.message_box.show("Room full! Starting game...", "success")
                self.waiting_for_game = True
                self.start_game_button.visible = True  # Show start game button
                # Auto-redirect to game after short delay when room is full
                pygame.time.set_timer(pygame.USEREVENT + 2, 2000)  # 2 second delay
    
    def _handle_game_start(self, payload):
        """Handle game start message from server"""
        print(f"=== GAME START RECEIVED ===")
        print(f"Payload: {payload}")
        
        players = payload.get('players', {})  # {color: user_id}
        player_info = payload.get('player_info', {})  # {color: {user_id, username}}
        game_state = payload.get('game_state', {})
        
        print(f"Players: {players}")
        print(f"Player info: {player_info}")
        print(f"Current user_data: {self.user_data}")
        
        # Store game info for the game screen
        self.network_client.current_game_players = players
        self.network_client.current_game_player_info = player_info
        self.network_client.current_game_state = game_state
        
        print(f"Stored game info in network client:")
        print(f"  - current_game_players: {self.network_client.current_game_players}")
        print(f"  - current_game_player_info: {self.network_client.current_game_player_info}")
        
        self.waiting_for_game = False
        print("=== GAME START PROCESSING COMPLETE ===")
    
    
    def handle_events(self):
        """Handle pygame events"""
        dt = self.clock.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.USEREVENT + 2:
                # Auto-redirect to multiplayer game after successful room join or room full
                print("Timer triggered: redirecting to multiplayer game")
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # Cancel timer
                return "multiplayer_game"
            
            elif event.type == pygame.USEREVENT + 3:
                # Auto-redirect to multiplayer game after game start
                print("Game start timer triggered: redirecting to multiplayer game")
                pygame.time.set_timer(pygame.USEREVENT + 3, 0)  # Cancel timer
                return "multiplayer_game"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_RETURN:
                    # Enter key to join room if room ID is entered
                    if self.join_code_field.get_text().strip():
                        return self.join_room()
            
            # Handle UI events
            back_action = self.back_button.handle_event(event)
            if back_action:
                return back_action
            
            # Make room button
            make_action = self.make_room_button.handle_event(event)
            if make_action:
                return self.make_room()
            
            # Join room button
            join_action = self.join_room_button.handle_event(event)
            if join_action:
                return self.join_room()
            
            # Start game button
            start_action = self.start_game_button.handle_event(event)
            if start_action:
                return "multiplayer_game"
            
            # Share code button
            # share_action = self.share_code_button.handle_event(event)
            # if share_action:
            #     return self.share_room_code()
            
            # Handle form inputs
            self.join_code_field.handle_event(event)
        
        # Update UI elements
        self.join_code_field.update(dt)
        self.message_box.update(dt)
        
        return None
    
    def make_room(self):
        """Create a new game room with server"""
        if self.room_operation_in_progress:
            return None
            
        # Connect to server if not connected
        if not self.network_client.connected:
            self.message_box.show("Connecting to server...", "info")
            if not self.network_client.connect():
                self.message_box.show("Failed to connect to server", "error")
                return None
        
        # Set operation in progress
        self.room_operation_in_progress = True
        self.message_box.show("Creating room...", "info")
        
        # Send room creation request to server
        def room_created_callback(room_code):
            self.room_operation_in_progress = False
            if room_code:
                self.generated_room_id = room_code
                self.current_room_code = room_code
                self.show_room_id = True
                self.message_box.show(f"Room created! ID: {room_code}", "success")
                self.waiting_for_game = True
                # self.share_code_button.visible = True  # Show share code button
            else:
                self.message_box.show("Failed to create room", "error")
        
        self.network_client.create_room(room_created_callback)
        return None
    
    def join_room(self):
        """Join an existing room using room ID"""
        if self.room_operation_in_progress:
            return None
            
        room_id = self.join_code_field.get_text().strip().upper()
        
        if not room_id:
            self.message_box.show("Please enter Room ID", "error")
            return None
        
        if len(room_id) < 4:
            self.message_box.show("Room ID must be at least 4 characters", "error")
            return None
        
        # Connect to server if not connected
        if not self.network_client.connected:
            self.message_box.show("Connecting to server...", "info")
            if not self.network_client.connect():
                self.message_box.show("Failed to connect to server", "error")
                return None
        
        # Set operation in progress
        self.room_operation_in_progress = True
        self.message_box.show("Joining room...", "info")
        
        # Send join room request to server
        def room_joined_callback(success, room_code):
            self.room_operation_in_progress = False
            if success:
                self.current_room_code = room_code
                self.message_box.show("Successfully joined room!", "success")
                self.join_code_field.clear()
                # Don't auto-redirect here, wait for room_update or game_start
            else:
                self.message_box.show("Failed to join room. Room may not exist or be full.", "error")
        
        self.network_client.join_room(room_id, room_joined_callback)
        return None
    
    def share_room_code(self):
        """Navigate to code sharing screen"""
        if not self.generated_room_id:
            return None
        
        # Return tuple with action and room code for screen manager
        return ("code", self.generated_room_id)
    
    def draw_room_status(self):
        """Draw current room status and players"""
        if self.current_room_code and self.waiting_for_game:
            # Room status display
            status_y = 520
            status_rect = pygame.Rect(self.width//2 - 200, status_y, 400, 80)
            
            # Background
            pygame.draw.rect(self.screen, COLORS['button'], status_rect)
            pygame.draw.rect(self.screen, COLORS['grid_lines'], status_rect, 2)
            
            # Room code
            room_text = self.subtitle_font.render(f"Room: {self.current_room_code}", True, COLORS['text'])
            room_rect = room_text.get_rect(center=(status_rect.centerx, status_rect.y + 20))
            self.screen.blit(room_text, room_rect)
            
            # Players status
            if len(self.room_players) == 1:
                player_text = f"Players: {', '.join(self.room_players)} (Waiting for another player...)"
            else:
                player_text = f"Players: {', '.join(self.room_players)} (Ready to start!)"
            
            player_surface = self.instruction_font.render(player_text, True, COLORS['text'])
            player_rect = player_surface.get_rect(center=(status_rect.centerx, status_rect.y + 45))
            self.screen.blit(player_surface, player_rect)
    
    def draw_room_id_display(self):
        """Draw the generated room ID if available"""
        if self.show_room_id and self.generated_room_id:
            # Room ID display box
            display_y = 450
            display_rect = pygame.Rect(self.width//2 - 150, display_y, 300, 60)
            
            # Background
            pygame.draw.rect(self.screen, COLORS['button'], display_rect)
            pygame.draw.rect(self.screen, COLORS['grid_lines'], display_rect, 2)
            
            # Title
            title_text = self.subtitle_font.render("Your Room ID:", True, COLORS['text'])
            title_rect = title_text.get_rect(center=(display_rect.centerx, display_rect.y + 15))
            self.screen.blit(title_text, title_rect)
            
            # Room ID
            id_text = self.title_font.render(self.generated_room_id, True, COLORS['text'])
            id_rect = id_text.get_rect(center=(display_rect.centerx, display_rect.y + 40))
            self.screen.blit(id_text, id_rect)
    
    def draw_instructions(self):
        """Draw helpful instructions"""
        # Make room instruction
        make_text = "Click 'MAKE ROOM' to create a new game room"
        make_surface = self.instruction_font.render(make_text, True, COLORS['text'])
        make_rect = make_surface.get_rect(center=(self.width//2, 170))
        self.screen.blit(make_surface, make_rect)
        
        # Join room instruction (with vertical spacing)
        join_text = "Enter a 5-character Room ID to join an existing room"
        join_surface = self.instruction_font.render(join_text, True, COLORS['text'])
        join_rect = join_surface.get_rect(center=(self.width//2, 280))
        self.screen.blit(join_surface, join_rect)
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw header
        title_text = self.title_font.render("GAME ROOMS", True, COLORS['text'])
        subtitle_text = self.subtitle_font.render("Create or join a game room", True, COLORS['text'])
        
        title_rect = title_text.get_rect(center=(self.width // 2, 60))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 100))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Draw instructions
        self.draw_instructions()
        
        # Draw buttons and input field
        self.make_room_button.draw(self.screen)
        self.join_code_field.draw(self.screen)
        self.join_room_button.draw(self.screen)
        self.start_game_button.draw(self.screen)  # Draw start game button
        # self.share_code_button.draw(self.screen)  # Draw share code button
        
        # Draw room ID display if room was created
        self.draw_room_id_display()
        
        # Draw room status if in a room
        self.draw_room_status()
        
        # Draw message box
        self.message_box.draw(self.screen, self.width // 2, 620)
        
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