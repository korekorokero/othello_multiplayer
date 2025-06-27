# server/user_manager.py
import uuid
import threading
from server.protocols import Protocol

class User:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.user_id = str(uuid.uuid4())
        self.username = None
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
    def __init__(self, room_manager):
        self.users = {} # Maps connection to User object
        self.room_manager = room_manager
        self.lock = threading.Lock()

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
            user.username = payload.get("username", "Anonymous")
            user.send(Protocol.user_registered(True, user.user_id))
        
        elif msg_type == "create_room":
            room_code = self.room_manager.create_room(user)
            user.send(Protocol.room_created(room_code))
            # The join automatically sends a room_update
            room = self.room_manager.get_room_by_player(user)
            if room:
                 update_msg = Protocol.room_update(room.code, room.players)
                 user.send(update_msg)

        elif msg_type == "join_room":
            room_code = payload.get("room_code")
            success, message = self.room_manager.join_room(user, room_code)
            user.send(Protocol.room_joined(success, room_code))
            if success:
                room = self.room_manager.get_room_by_player(user)
                # Notify everyone in the room about the new player
                update_msg = Protocol.room_update(room.code, room.players)
                for p in room.players:
                    p.send(update_msg)

        elif msg_type == "make_move":
            room = user.current_room
            if room and room.game_manager:
                room.game_manager.handle_move(user, payload.get("move"))
            else:
                user.send(Protocol.error("You are not in an active game."))

