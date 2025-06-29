# server/game_manager.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.protocols import Protocol
from game.othello_board import OthelloBoard
from game.othello_rules import OthelloRules
from shared.constants import BLACK, WHITE, EMPTY

class RealOthelloGame:
    """Real Othello game implementation using proper game logic"""
    
    def __init__(self):
        self.board = OthelloBoard()
        self.current_turn = BLACK  # Black always goes first
        self.game_over = False
        self.winner = None
    
    def get_game_state(self):
        """Get current game state in server format"""
        # Convert board to server format (string representation)
        board_state = []
        for row in range(8):
            board_row = []
            for col in range(8):
                cell = self.board.get_cell(row, col)
                if cell == BLACK:
                    board_row.append('black')
                elif cell == WHITE:
                    board_row.append('white')
                else:
                    board_row.append('')
            board_state.append(board_row)
        
        # Calculate scores
        black_count = sum(row.count('black') for row in board_state)
        white_count = sum(row.count('white') for row in board_state)
        
        return {
            'board': board_state,
            'turn': 'black' if self.current_turn == BLACK else 'white',
            'scores': {'black': black_count, 'white': white_count},
            'game_over': self.game_over,
            'winner': self.winner
        }
    
    def make_move(self, move, player_color):
        """Make a move on the board"""
        if self.game_over:
            print(f"Game is over, cannot make move")
            return False
        
        # Convert player color to internal representation
        player = BLACK if player_color == 'black' else WHITE
        
        # Check if it's the player's turn
        if player != self.current_turn:
            print(f"Not {player_color}'s turn (current: {'black' if self.current_turn == BLACK else 'white'})")
            return False
        
        r, c = move
        print(f"Making move: {player_color} at ({r}, {c})")
        
        # Check if move is valid
        if not OthelloRules.is_valid_move(self.board, r, c, player):
            print(f"Invalid move: {player_color} at ({r}, {c})")
            return False
        
        # Get pieces to flip
        flipped_pieces = OthelloRules.get_flipped_pieces(self.board, r, c, player)
        print(f"Flipping {len(flipped_pieces)} pieces: {flipped_pieces}")
        
        # Place the piece
        self.board.set_cell(r, c, player)
        
        # Flip all captured pieces
        for flip_r, flip_c in flipped_pieces:
            self.board.set_cell(flip_r, flip_c, player)
        
        # Switch turns
        self.current_turn = WHITE if self.current_turn == BLACK else BLACK
        
        # Check for game over conditions
        self._check_game_over()
        
        print(f"Move successful, next turn: {'black' if self.current_turn == BLACK else 'white'}")
        return True
    
    def _check_game_over(self):
        """Check if the game is over"""
        # Check if current player has valid moves
        current_has_moves = self._has_valid_moves(self.current_turn)
        
        if not current_has_moves:
            # Switch to other player and check
            other_player = WHITE if self.current_turn == BLACK else BLACK
            other_has_moves = self._has_valid_moves(other_player)
            
            if not other_has_moves:
                # Neither player has moves - game over
                self.game_over = True
                self._determine_winner()
            else:
                # Current player has no moves, switch to other player
                self.current_turn = other_player
    
    def _has_valid_moves(self, player):
        """Check if a player has any valid moves"""
        for row in range(8):
            for col in range(8):
                if OthelloRules.is_valid_move(self.board, row, col, player):
                    return True
        return False
    
    def _determine_winner(self):
        """Determine the winner based on piece count"""
        game_state = self.get_game_state()
        black_score = game_state['scores']['black']
        white_score = game_state['scores']['white']
        
        if black_score > white_score:
            self.winner = 'black'
        elif white_score > black_score:
            self.winner = 'white'
        else:
            self.winner = None  # Tie

class GameManager:
    def __init__(self, room_code, players, user_manager):
        self.room_code = room_code
        self.players = {p.user_id: p for p in players} # map user_id to player object
        self.user_manager = user_manager
        self.game = RealOthelloGame()  # Use real Othello game instead of placeholder
        # In Othello, black always goes first, so assign first player as black
        self.player_colors = {
            players[0].user_id: 'black',   # First player is black (goes first)
            players[1].user_id: 'white'    # Second player is white
        }
        self.start_game()

    def start_game(self):
        """Broadcasts the start of the game to both players."""
        print(f"[GameManager-{self.room_code}] Starting game.")
        print(f"[GameManager-{self.room_code}] Players: {[(p.user_id, p.username) for p in self.players.values()]}")
        print(f"[GameManager-{self.room_code}] Player colors: {self.player_colors}")
        
        initial_state = self.game.get_game_state()
        start_message = Protocol.game_start(list(self.players.values()), initial_state)
        print(f"[GameManager-{self.room_code}] Sending game_start message: {start_message}")
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
        """Announces the end of the game and updates the winner's score."""
        winner_color = self.game.winner
        scores = self.game.get_game_state()['scores']
        
        print(f"[GameManager-{self.room_code}] Game over. Winner: {winner_color}")

        winner_user_id = None
        for user_id, color in self.player_colors.items():
            if color == winner_color:
                winner_user_id = user_id
                break
        
        if winner_user_id:
            winner_player = self.players.get(winner_user_id)
            if winner_player and winner_player.username:
                points = scores[winner_color]
                self.user_manager.update_user_score(winner_player.username, points)

        end_message = Protocol.game_over(winner_color, scores)
        self.broadcast(end_message)

    def broadcast(self, message):
        """Sends a message to all players in the game."""
        for player in self.players.values():
            player.send(message)