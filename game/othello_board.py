# othello_multiplayer/game/othello_board.py
from shared import constants

class OthelloBoard:
    def __init__(self):
        self.width = constants.BOARD_WIDTH
        self.height = constants.BOARD_HEIGHT
        self.board = self._create_initial_board()

    def _create_initial_board(self):
        # ... (kode dari sebelumnya, tidak perlu diubah)
        board = [[constants.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        mid_w, mid_h = self.width // 2, self.height // 2
        board[mid_h - 1][mid_w - 1] = constants.WHITE
        board[mid_h - 1][mid_w] = constants.BLACK
        board[mid_h][mid_w - 1] = constants.BLACK
        board[mid_h][mid_w] = constants.WHITE
        return board

    def get_board_state(self):
        return [row[:] for row in self.board]

    # --- TAMBAHKAN METODE DI BAWAH INI ---

    def place_piece(self, row, col, color):
        """Menempatkan bidak di posisi (row, col) tanpa validasi."""
        if self.is_on_board(row, col):
            self.board[row][col] = color
        else:
            # Sebaiknya tidak pernah terjadi jika logika validasi benar
            raise ValueError("Move is outside of the board boundaries.")

    def is_on_board(self, row, col):
        """Memeriksa apakah sebuah posisi berada di dalam papan."""
        return 0 <= row < self.height and 0 <= col < self.width