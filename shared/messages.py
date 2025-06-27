# shared/messages.py
"""
Network message types and structures for client-server communication
"""

# Message types - Client to Server
MSG_LOGIN = "login"
MSG_REGISTER = "register"
MSG_CREATE_ROOM = "create_room"
MSG_JOIN_ROOM = "join_room"
MSG_LEAVE_ROOM = "leave_room"
MSG_MAKE_MOVE = "make_move"
MSG_READY = "ready"
MSG_CHAT = "chat"
MSG_DISCONNECT = "disconnect"
MSG_PING = "ping"

# Message types - Server to Client
MSG_LOGIN_RESPONSE = "login_response"
MSG_REGISTER_RESPONSE = "register_response"
MSG_ROOM_CREATED = "room_created"
MSG_ROOM_JOINED = "room_joined"
MSG_ROOM_LEFT = "room_left"
MSG_ROOM_ERROR = "room_error"
MSG_GAME_STATE = "game_state"
MSG_GAME_START = "game_start"
MSG_GAME_END = "game_end"
MSG_MOVE_RESULT = "move_result"
MSG_INVALID_MOVE = "invalid_move"
MSG_PLAYER_JOINED = "player_joined"
MSG_PLAYER_LEFT = "player_left"
MSG_CHAT_MESSAGE = "chat_message"
MSG_ERROR = "error"
MSG_PONG = "pong"

# Error codes
ERROR_INVALID_CREDENTIALS = "invalid_credentials"
ERROR_USER_EXISTS = "user_exists"
ERROR_ROOM_NOT_FOUND = "room_not_found"
ERROR_ROOM_FULL = "room_full"
ERROR_ALREADY_IN_ROOM = "already_in_room"
ERROR_NOT_IN_ROOM = "not_in_room"
ERROR_GAME_NOT_ACTIVE = "game_not_active"
ERROR_NOT_YOUR_TURN = "not_your_turn"
ERROR_INVALID_MOVE = "invalid_move"
ERROR_CONNECTION_LOST = "connection_lost"
ERROR_SERVER_FULL = "server_full"

class Message:
    """Base message class for structured communication"""
    
    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data if data is not None else {}
        
    def to_dict(self):
        """Convert message to dictionary for JSON serialization"""
        return {
            "type": self.type,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, msg_dict):
        """Create message from dictionary"""
        return cls(msg_dict.get("type"), msg_dict.get("data", {}))

# Predefined message creators for common operations
def create_login_message(username, password):
    return Message(MSG_LOGIN, {
        "username": username,
        "password": password
    })

def create_register_message(username, password):
    return Message(MSG_REGISTER, {
        "username": username,
        "password": password
    })

def create_room_message():
    return Message(MSG_CREATE_ROOM)

def create_join_room_message(room_code):
    return Message(MSG_JOIN_ROOM, {
        "room_code": room_code
    })

def create_move_message(row, col):
    return Message(MSG_MAKE_MOVE, {
        "row": row,
        "col": col
    })

def create_ready_message():
    return Message(MSG_READY)

def create_chat_message(text):
    return Message(MSG_CHAT, {
        "text": text
    })

def create_error_message(error_code, description=""):
    return Message(MSG_ERROR, {
        "error_code": error_code,
        "description": description
    })

def create_game_state_message(board, current_player, scores, valid_moves, game_status):
    return Message(MSG_GAME_STATE, {
        "board": board,
        "current_player": current_player,
        "scores": scores,
        "valid_moves": valid_moves,
        "game_status": game_status
    })

def create_move_result_message(success, board, scores, flipped_pieces, current_player):
    return Message(MSG_MOVE_RESULT, {
        "success": success,
        "board": board,
        "scores": scores,
        "flipped_pieces": flipped_pieces,
        "current_player": current_player
    })

def create_game_end_message(winner, final_scores, reason):
    return Message(MSG_GAME_END, {
        "winner": winner,
        "final_scores": final_scores,
        "reason": reason
    })