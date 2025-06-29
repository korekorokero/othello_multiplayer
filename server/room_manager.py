# server/room_manager.py
import random
import string
from server.game_manager import GameManager

class Room:
    def __init__(self, room_code):
        self.code = room_code
        self.players = []
        self.game_manager = None

    def add_player(self, player):
        if len(self.players) < 2:
            self.players.append(player)
            player.current_room = self
            return True
        return False

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
            player.current_room = None
            return True
        return False

    def is_full(self):
        return len(self.players) == 2

    def start_game(self):
        if self.is_full() and not self.game_manager:
            print(f"[Room-{self.code}] Starting game with players: {[p.username for p in self.players]}")
            self.game_manager = GameManager(self.code, self.players)

class RoomManager:
    def __init__(self):
        self.rooms = {} # Maps room_code to Room object

    def create_room(self, player):
        room_code = self._generate_room_code()
        room = Room(room_code)
        self.rooms[room_code] = room
        print(f"[RoomManager] Created room {room_code}")
        self.join_room(player, room_code)
        return room_code

    def join_room(self, player, room_code):
        room = self.rooms.get(room_code)
        if not room:
            return False, "Room not found."
        
        if room.add_player(player):
            print(f"[RoomManager] Player {player.username} joined room {room_code}")
            print(f"[RoomManager] Room {room_code} now has {len(room.players)} players")
            if room.is_full():
                print(f"[RoomManager] Room {room_code} is full, starting game...")
                room.start_game()
            return True, "Joined successfully."
        else:
            return False, "Room is full."

    def leave_room(self, player):
        room = player.current_room
        if room and room.remove_player(player):
            print(f"[RoomManager] Player {player.username} left room {room.code}")
            if not room.players: # If room is empty, delete it
                del self.rooms[room.code]
                print(f"[RoomManager] Room {room.code} is empty and has been deleted.")
            return True
        return False

    def get_room_by_player(self, player):
        return player.current_room

    def _generate_room_code(self, length=5):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if code not in self.rooms:
                return code