# server/protocols.py
import json

class Protocol:
    @staticmethod
    def create_message(msg_type, payload):
        """Creates a JSON message string."""
        return json.dumps({"type": msg_type, "payload": payload})

    @staticmethod
    def parse_message(data_str):
        """Parses a JSON message string into a dictionary."""
        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return None

    # --- S2C (Server-to-Client) Message Creators ---
    @staticmethod
    def user_registered(success, user_id):
        return Protocol.create_message("user_registered", {"success": success, "user_id": user_id})

    @staticmethod
    def user_logged_in(success, user_data=None):
        payload = {"success": success}
        if user_data:
            payload["user"] = user_data
        return Protocol.create_message("user_logged_in", payload)

    @staticmethod
    def error(message):
        return Protocol.create_message("error", {"message": message})

    @staticmethod
    def room_created(room_code):
        return Protocol.create_message("room_created", {"room_code": room_code})
    
    @staticmethod
    def room_joined(success, room_code):
        return Protocol.create_message("room_joined", {"success": success, "room_code": room_code})

    @staticmethod
    def room_update(room_code, players):
        player_names = [p.username for p in players]
        return Protocol.create_message("room_update", {"room_code": room_code, "players": player_names})

    @staticmethod
    def game_start(players, game_state):
        player_map = {
            "white": players[0].user_id,
            "black": players[1].user_id
        }
        return Protocol.create_message("game_start", {"players": player_map, "game_state": game_state})

    @staticmethod
    def game_update(game_state):
        return Protocol.create_message("game_update", {"game_state": game_state})
    
    @staticmethod
    def game_over(winner, scores):
        return Protocol.create_message("game_over", {"winner": winner, "scores": scores})

