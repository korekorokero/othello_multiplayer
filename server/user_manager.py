import uuid
import threading
import os
import json
import hashlib
from datetime import datetime
from server.protocols import Protocol

class User:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.user_id = str(uuid.uuid4())
        self.username = None
        self.score = 0
        self.current_room = None

    def send(self, message):
        """Sends a message to this user's client."""
        try:
            self.connection.sendall(message.encode('utf-8') + b'\n')
        except (BrokenPipeError, ConnectionResetError):
            print(f"Failed to send to {self.username or self.address}. Connection lost.")
            # The main server loop will handle the disconnect.

    def __str__(self):
        return f"User(id={self.user_id}, name={self.username})"

class UserManager:
    def __init__(self):
        self.users = {} # Maps connection to User object
        self.room_manager = None # Will be set by Server after initialization
        self.lock = threading.Lock()
        self.users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        self._init_users_file()

    def _init_users_file(self):
        with self.lock:
            if not os.path.exists(self.users_file):
                # Create data directory if it doesn't exist
                os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
                with open(self.users_file, 'w') as f:
                    json.dump({}, f)

    def _save_user(self, user_data):
        with self.lock:
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
                
                # Read existing users, or start with an empty dict if file doesn't exist/is empty
                try:
                    with open(self.users_file, 'r') as f:
                        users = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    users = {}

                # Add new user and write back, using username as the key
                users[user_data['username']] = user_data
                with open(self.users_file, 'w') as f:
                    json.dump(users, f, indent=4)

            except IOError as e:
                print(f"Error saving user data: {e}")

    def update_user_score(self, username, points_to_add):
        users = self._load_users()
        if username in users:
            users[username]['score'] = users[username].get('score', 0) + points_to_add
            try:
                with open(self.users_file, 'w') as f:
                    json.dump(users, f, indent=4)
                print(f"[UserManager] Updated score for {username}. New score: {users[username]['score']}")
            except IOError as e:
                print(f"[UserManager] Error updating user score: {e}")
        else:
            print(f"[UserManager] User {username} not found, cannot update score.")

    def _load_users(self):
        with self.lock:
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}

    def add_user(self, connection, address):
        user = User(connection, address)
        with self.lock:
            self.users[connection] = user
        print(f"[UserManager] New connection from {address}. Assigned ID: {user.user_id}")
        return user

    def remove_user(self, user):
        with self.lock:
            if user.connection in self.users:
                # Handle leaving a room
                if user.current_room:
                    room = user.current_room
                    self.room_manager.leave_room(user)
                    # Notify other player in the room
                    update_msg = Protocol.room_update(room.code, room.players)
                    for p in room.players:
                        p.send(update_msg)
                
                del self.users[user.connection]
                print(f"[UserManager] Removed user: {user.username or user.address}")

    def handle_message(self, user, message_str):
        """Routes a message from a user to the appropriate handler."""
        message = Protocol.parse_message(message_str)
        if not message:
            user.send(Protocol.error("Invalid message format."))
            return

        msg_type = message.get("type")
        payload = message.get("payload", {})
        
        print(f"[UserManager] Received from {user.username or user.user_id}: type={msg_type}")

        if msg_type == "register_user":
            username = payload.get("username")
            email = payload.get("email")
            password = payload.get("password")

            if not all([username, email, password]):
                user.send(Protocol.error("Username, email, and password are required."))
                return

            users = self._load_users()
            if username in users:
                user.send(Protocol.user_registered(False, None))
                return

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            user.username = username
            user.email = email
            user.password = hashed_password
            user.score = 0
            user.created_at = datetime.now().isoformat()

            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "password": hashed_password, # Storing hashed password
                "score": user.score,
                "created_at": user.created_at
            }
            self._save_user(user_data)

            user.send(Protocol.user_registered(True, user.user_id))

        elif msg_type == "login_user":
            username = payload.get("username")
            password = payload.get("password")

            if not all([username, password]):
                user.send(Protocol.error("Username and password are required."))
                return

            users = self._load_users()
            logged_in_user = None
            hashed_password_input = hashlib.sha256(password.encode()).hexdigest()

            if username in users and users[username]['password'] == hashed_password_input:
                user_data = users[username]
                user.user_id = user_data['user_id']
                user.username = user_data['username']
                user.email = user_data['email']
                user.password = user_data['password']
                user.score = user_data['score']
                user.created_at = user_data.get('created_at')
                logged_in_user = user_data
            
            if logged_in_user:
                user.send(Protocol.user_logged_in(True, logged_in_user))
            else:
                user.send(Protocol.user_logged_in(False))

        elif msg_type == "create_room":
            # Get user_data from payload if provided
            user_data = payload.get("user_data", {})
            if user_data.get("username"):
                user.username = user_data["username"]
            if user_data.get("user_id"):
                user.user_id = user_data["user_id"]
            
            room_code = self.room_manager.create_room(user)
            user.send(Protocol.room_created(room_code))
            # The join automatically sends a room_update
            room = self.room_manager.get_room_by_player(user)
            if room:
                 update_msg = Protocol.room_update(room.code, room.players)
                 user.send(update_msg)

        elif msg_type == "join_room":
            room_code = payload.get("room_code")
            # Get user_data from payload if provided
            user_data = payload.get("user_data", {})
            if user_data.get("username"):
                user.username = user_data["username"]
            if user_data.get("user_id"):
                user.user_id = user_data["user_id"]
            
            success, message = self.room_manager.join_room(user, room_code)
            user.send(Protocol.room_joined(success, room_code))
            if success:
                room = self.room_manager.get_room_by_player(user)
                # Notify everyone in the room about the new player
                update_msg = Protocol.room_update(room.code, room.players)
                for p in room.players:
                    p.send(update_msg)
                print(f"[UserManager] Room {room_code} now has {len(room.players)} players: {[p.username for p in room.players]}")

        elif msg_type == "make_move":
            room = user.current_room
            if room and room.game_manager:
                room.game_manager.handle_move(user, payload.get("move"))
            else:
                user.send(Protocol.error("You are not in an active game."))

