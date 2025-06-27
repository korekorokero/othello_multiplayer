# othello_multiplayer/game/game_state.py

from . import othello_board
from . import othello_rules
from shared import constants

class GameState:
    def __init__(self):
        self.board = othello_board.OthelloBoard()
        self.current_turn = constants.BLACK  # Hitam selalu jalan duluan
        self.scores = othello_rules.calculate_score(self.board.get_board_state())
        self.game_over = False
        self.winner = None

    def make_move(self, row, col):
        """
        Mencoba melakukan langkah. Mengembalikan True jika berhasil, False jika tidak.
        Ini adalah metode utama yang akan dipanggil oleh server.
        """
        board_state = self.board.get_board_state()
        
        if self.game_over or not othello_rules.is_valid_move(board_state, row, col, self.current_turn):
            return False

        # 1. Lakukan langkah dan balik bidak
        self.board.place_piece(row, col, self.current_turn)
        flipped_pieces = othello_rules.get_flipped_pieces(board_state, row, col, self.current_turn)
        for r, c in flipped_pieces:
            self.board.place_piece(r, c, self.current_turn)

        # 2. Ganti giliran
        self.switch_turn()
        
        # 3. Perbarui skor
        self.scores = othello_rules.calculate_score(self.board.get_board_state())
        
        # 4. Periksa kondisi game over
        self._check_game_over()
        
        return True

    def switch_turn(self):
        """Mengganti giliran ke pemain berikutnya."""
        self.current_turn = constants.WHITE if self.current_turn == constants.BLACK else constants.BLACK

    def _check_game_over(self):
        """Memeriksa apakah permainan telah selesai."""
        board_state = self.board.get_board_state()
        
        # Jika pemain saat ini punya langkah, game belum selesai
        if othello_rules.get_valid_moves(board_state, self.current_turn):
            return

        # Jika pemain saat ini tidak punya langkah, cek pemain lain
        self.switch_turn()
        if othello_rules.get_valid_moves(board_state, self.current_turn):
            # Pemain saat ini harus pass/skip, tapi game lanjut
            return

        # Jika kedua pemain tidak punya langkah valid, game over
        self.game_over = True
        if self.scores[constants.BLACK] > self.scores[constants.WHITE]:
            self.winner = constants.BLACK
        elif self.scores[constants.WHITE] > self.scores[constants.BLACK]:
            self.winner = constants.WHITE
        else:
            self.winner = None # Seri