import pygame
import sys
from constants import *
from utils.utils import initialize_pygame, create_fonts
from ui.form_elements import InputField, Button, MessageBox
from ui.common_ui import ScreenHeader, BackButton

class RoomScreen:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.screen = initialize_pygame()
        self.fonts = create_fonts()
        
        # UI Elements
        self.header = ScreenHeader("GAME ROOMS", "Join or create a game room")
        self.back_button = BackButton()
        
        # Room creation section
        create_x = 50
        self.room_name_field = InputField(create_x, 150, 250, 40, "Room Name")
        self.room_code_field = InputField(create_x, 200, 250, 40, "Room Code (optional)")
        self.create_room_button = Button(create_x, 250, 250, 40, "CREATE ROOM", "create_room")
        
        # Room joining section
        join_x = 400
        self.join_code_field = InputField(join_x, 150, 250, 40, "Enter Room Code")
        self.join_room_button = Button(join_x, 200, 250, 40, "JOIN ROOM", "join_room")
        self.quick_match_button = Button(join_x, 250, 250, 40, "QUICK MATCH", "quick_match")
        
        # Available rooms list (mock data)
        self.available_rooms = [
            {"name": "Beginner's Room", "code": "ROOM001", "players": "1/2"},
            {"name": "Pro League", "code": "ROOM002", "players": "0/2"},
            {"name": "Quick Game", "code": "ROOM003", "players": "1/2"},
        ]
        
        # Single player option
        self.single_player_button = Button(width//2 - 125, 450, 250, 40, "SINGLE PLAYER", "single_player")
        
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
            
            # Handle UI events
            back_action = self.back_button.handle_event(event)
            if back_action:
                return back_action
            
            # Room creation
            create_action = self.create_room_button.handle_event(event)
            if create_action:
                return self.create_room()
            
            # Room joining
            join_action = self.join_room_button.handle_event(event)
            if join_action:
                return self.join_room()
            
            quick_action = self.quick_match_button.handle_event(event)
            if quick_action:
                return self.quick_match()
            
            # Single player
            single_action = self.single_player_button.handle_event(event)
            if single_action:
                return "single_player"
            
            # Handle room list clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                room_action = self.handle_room_click(event.pos)
                if room_action:
                    return room_action
            
            # Handle form inputs
            self.room_name_field.handle_event(event)
            self.room_code_field.handle_event(event)
            self.join_code_field.handle_event(event)
        
        # Update UI elements
        self.room_name_field.update(dt)
        self.room_code_field.update(dt)
        self.join_code_field.update(dt)
        self.message_box.update(dt)
        
        return None
    
    def create_room(self):
        """Create a new game room"""
        room_name = self.room_name_field.get_text().strip()
        room_code = self.room_code_field.get_text().strip()
        
        if not room_name:
            self.message_box.show("Please enter room name", "error")
            return None
        
        # Generate random code if not provided
        import random
        import string
        if not room_code:
            room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        print(f"Creating room: {room_name} with code: {room_code}")
        self.message_box.show(f"Room created! Code: {room_code}", "success")
        
        # Here you would create room on server and wait for players
        return "waiting_room"
    
    def join_room(self):
        """Join an existing room"""
        room_code = self.join_code_field.get_text().strip()
        
        if not room_code:
            self.message_box.show("Please enter room code", "error")
            return None
        
        # Here you would validate room code with server
        print(f"Joining room: {room_code}")
        self.message_box.show("Joining room...", "info")
        
        return "game"
    
    def quick_match(self):
        """Start quick match"""
        print("Starting quick match...")
        self.message_box.show("Finding opponent...", "info")
        return "game"
    
    def handle_room_click(self, mouse_pos):
        """Handle clicks on available rooms list"""
        rooms_start_y = 320
        room_height = 30
        
        for i, room in enumerate(self.available_rooms):
            room_y = rooms_start_y + i * (room_height + 5)
            room_rect = pygame.Rect(50, room_y, 600, room_height)
            
            if room_rect.collidepoint(mouse_pos):
                print(f"Joining room: {room['name']}")
                self.message_box.show(f"Joining {room['name']}...", "info")
                return "game"
        
        return None
    
    def draw_available_rooms(self):
        """Draw the list of available rooms"""
        # Section title
        title_font = pygame.font.Font(None, FONT_MEDIUM)
        title_surface = title_font.render("Available Rooms:", True, COLORS['text'])
        self.screen.blit(title_surface, (50, 290))
        
        # Room list
        room_font = pygame.font.Font(None, FONT_SMALL)
        rooms_start_y = 320
        
        for i, room in enumerate(self.available_rooms):
            room_y = rooms_start_y + i * 35
            
            # Room background
            room_rect = pygame.Rect(50, room_y, 600, 30)
            pygame.draw.rect(self.screen, COLORS['button'], room_rect)
            pygame.draw.rect(self.screen, COLORS['grid_lines'], room_rect, 1)
            
            # Room info
            room_text = f"{room['name']} - Code: {room['code']} - Players: {room['players']}"
            text_surface = room_font.render(room_text, True, COLORS['text'])
            self.screen.blit(text_surface, (room_rect.x + 10, room_rect.y + 8))
    
    def update_display(self):
        """Update the entire display"""
        self.screen.fill(COLORS['background'])
        
        # Draw header and back button
        self.header.draw(self.screen, self.width)
        self.back_button.draw(self.screen)
        
        # Draw section titles
        section_font = pygame.font.Font(None, FONT_MEDIUM)
        
        create_title = section_font.render("Create Room:", True, COLORS['text'])
        self.screen.blit(create_title, (50, 120))
        
        join_title = section_font.render("Join Room:", True, COLORS['text'])
        self.screen.blit(join_title, (400, 120))
        
        # Draw form elements
        self.room_name_field.draw(self.screen)
        self.room_code_field.draw(self.screen)
        self.create_room_button.draw(self.screen)
        
        self.join_code_field.draw(self.screen)
        self.join_room_button.draw(self.screen)
        self.quick_match_button.draw(self.screen)
        
        # Draw available rooms
        self.draw_available_rooms()
        
        # Draw single player button
        self.single_player_button.draw(self.screen)
        
        # Draw message box
        self.message_box.draw(self.screen, self.width // 2 - 100, 520)
        
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