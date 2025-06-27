# server/game_manager.py
from server.protocols import Protocol

# --- PLACEHOLDER ---
# This class will be replaced by the real game logic from Role 3.
# For now, it provides a mock interface for the server to use.
class PlaceholderOthelloGame:
    def __init__(self):
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.board[3][3], self.board[4][4] = 'white', 'white'
        self.board[3][4], self.board[4][3] = 'black', 'black'
        self.current_turn = 'black'
        self.game_over = False
        self.winner = None
        self.scores = {'black': 2, 'white': 2}

    def get_game_state(self):
        return {
            'board': self.board, 'turn': self.current_turn,
            'scores': self.scores, 'game_over': self.game_over, 'winner': self.winner
        }

    def make_move(self, move, player_color):
        if self.game_over or player_color != self.current_turn:
            return False
        
        r, c = move
        if self.board[r][c] == '':
            self.board[r][c] = player_color
            self.scores[player_color] += 1
            self.current_turn = 'white' if self.current_turn == 'black' else 'black'
            
            # Simple game over condition for placeholder
            if self.scores['black'] + self.scores['white'] > 10:
                self.game_over = True
                self.winner = 'black' if self.scores['black'] > self.scores['white'] else 'white'

            return True
        return False

class GameManager:
    def __init__(self, room_code, players):
        self.room_code = room_code
        self.players = {p.user_id: p for p in players} # map user_id to player object
        self.game = PlaceholderOthelloGame()
        self.player_colors = {
            players[0].user_id: 'white',
            players[1].user_id: 'black'
        }
        self.start_game()

    def start_game(self):
        """Broadcasts the start of the game to both players."""
        print(f"[GameManager-{self.room_code}] Starting game.")
        initial_state = self.game.get_game_state()
        start_message = Protocol.game_start(list(self.players.values()), initial_state)
        self.broadcast(start_message)

    def handle_move(self, player, move_data):
        """Handles a move request from a player."""
        player_color = self.player_colors.get(player.user_id)
        if not player_color:
            player.send(Protocol.error("You are not a player in this game."))
            return

        if self.game.make_move(move_data, player_color):
            print(f"[GameManager-{self.room_code}] Player {player.username} made a valid move.")
            self.broadcast_game_update()
            if self.game.game_over:
                self.end_game()
        else:
            print(f"[GameManager-{self.room_code}] Player {player.username} made an invalid move.")
            player.send(Protocol.error("Invalid move."))

    def broadcast_game_update(self):
        """Sends the current game state to both players."""
        update_message = Protocol.game_update(self.game.get_game_state())
        self.broadcast(update_message)

    def end_game(self):
        """Announces the end of the game."""
        print(f"[GameManager-{self.room_code}] Game over. Winner: {self.game.winner}")
        end_message = Protocol.game_over(self.game.winner, self.game.scores)
        self.broadcast(end_message)

    def broadcast(self, message):
        """Sends a message to all players in the game."""
        for player in self.players.values():
            player.send(message)