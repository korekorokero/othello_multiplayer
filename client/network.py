# client/network.py
import socket
import json
import threading
import time
from typing import Callable, Optional

class NetworkClient:
    """Handles network communication with the game server"""
    
    def __init__(self, host='localhost', port=55555):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        self.receive_thread = None
        self.response_handlers = {}
        self.user_data = None
        
        # Game state information
        self.current_game_players = None
        self.current_game_player_info = None
        self.current_game_state = None
        self.current_room_code = None
        
    def connect(self) -> bool:
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            print(f"Connected to server at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        print("Disconnected from server")
    
    def _receive_messages(self):
        """Thread function to receive messages from server"""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.socket.recv(1024*1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self._handle_message(line.strip())
                        
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                break
        
        self.connected = False
        self.running = False
    
    def _handle_message(self, message_str: str):
        """Handle incoming message from server"""
        try:
            message = json.loads(message_str)
            msg_type = message.get('type')
            payload = message.get('payload', {})
            
            print(f"Received message: {msg_type}")
            
            # Handle specific message types
            if msg_type in self.response_handlers:
                self.response_handlers[msg_type](payload)
            
            # Handle room update messages
            if msg_type == 'room_update' and hasattr(self, 'on_room_update'):
                self.on_room_update(payload)
            
            # Handle game start messages
            if msg_type == 'game_start' and hasattr(self, 'on_game_start'):
                self.current_game_players = payload.get('players', {})
                self.current_game_player_info = payload.get('player_info', {})
                self.current_game_state = payload.get('game_state', {})
                self.on_game_start(payload)
            
            # Handle game update messages
            if msg_type == 'game_update' and hasattr(self, 'on_game_update'):
                self.current_game_state = payload.get('game_state', {})
                self.on_game_update(payload)
            
            # Handle move result messages  
            if msg_type == 'move_made' and hasattr(self, 'on_move_made'):
                self.on_move_made(payload)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")
    
    def send_message(self, msg_type: str, payload: dict = None):
        """Send a message to the server"""
        if not self.connected:
            print("Not connected to server")
            return False
        
        try:
            message = {
                'type': msg_type,
                'payload': payload if payload else {}
            }
            
            message_str = json.dumps(message) + '\n'
            self.socket.sendall(message_str.encode('utf-8'))
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.response_handlers[msg_type] = handler
    
    def remove_handler(self, msg_type: str):
        """Remove a handler for a specific message type"""
        if msg_type in self.response_handlers:
            del self.response_handlers[msg_type]
    
    def register_user(self, username: str, email: str, password: str, callback: Callable):
        """Register a new user"""
        def handle_response(payload):
            success = payload.get('success', False)
            user_id = payload.get('user_id')
            callback(success, user_id)
        
        self.register_handler('user_registered', handle_response)
        return self.send_message('register_user', {
            'username': username,
            'email': email,
            'password': password
        })
    
    def login_user(self, username: str, password: str, callback: Callable):
        """Login user"""
        def handle_response(payload):
            success = payload.get('success', False)
            user_data = payload.get('user') if success else None  # Changed from 'user_data' to 'user'
            if success and user_data:
                self.user_data = user_data
            callback(success, user_data)
        
        self.register_handler('user_logged_in', handle_response)
        return self.send_message('login_user', {
            'username': username,
            'password': password
        })
    
    def create_room(self, callback: Callable):
        """Create a new game room"""
        def handle_response(payload):
            room_code = payload.get('room_code')
            callback(room_code)
        
        # Include user info in create room request
        payload = {}
        if self.user_data:
            payload['user_data'] = self.user_data
            print(f"Creating room with user data: {self.user_data}")
        
        self.register_handler('room_created', handle_response)
        return self.send_message('create_room', payload)
    
    def join_room(self, room_code: str, callback: Callable):
        """Join an existing game room"""
        def handle_response(payload):
            success = payload.get('success', False)
            room_code = payload.get('room_code')
            callback(success, room_code)
        
        # Include user info in join room request
        payload = {'room_code': room_code}
        if self.user_data:
            payload['user_data'] = self.user_data
            print(f"Joining room with user data: {self.user_data}")
        
        self.register_handler('room_joined', handle_response)
        return self.send_message('join_room', payload)
    
    def make_move(self, row: int, col: int, callback: Callable = None):
        """Make a game move"""
        def handle_response(payload):
            if callback:
                callback(payload)
        
        if callback:
            self.register_handler('move_result', handle_response)
        
        # Send move in the format expected by server - as list [row, col] in 0-based indexing
        move_data = [row - 1, col - 1]  # Convert to 0-based indexing for server
        print(f"Sending move to server: row={row}, col={col}, move_data={move_data}")
        return self.send_message('make_move', {'move': move_data})

# Global network client instance
network_client = NetworkClient()
