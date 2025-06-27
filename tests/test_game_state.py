# tests/test_game_state.py

from game.game_state import GameState
from shared import constants

def test_initial_state():
    """Memeriksa apakah kondisi awal game sudah benar."""
    game_state = GameState()
    
    assert game_state.current_turn == constants.BLACK
    assert game_state.game_over == False
    assert game_state.winner is None
    # Skor awal di Othello adalah 2-2
    assert game_state.scores == {constants.BLACK: 2, constants.WHITE: 2}

def test_make_valid_move():
    """
    Tes ini memeriksa seluruh alur make_move untuk sebuah langkah yang valid:
    1. Bidak ditempatkan dengan benar.
    2. Bidak lawan dibalik dengan benar.
    3. Giliran berpindah.
    4. Skor diperbarui.
    """
    # 1. Setup
    game_state = GameState() # Mulai dari game baru
    
    # 2. Action
    # Lakukan langkah valid pertama untuk pemain Hitam di (2, 3)
    move_result = game_state.make_move(2, 3)
    
    # 3. Assert - Periksa semua perubahan state
    assert move_result == True # Metode harus mengembalikan True (sukses)
    
    # Giliran harus pindah ke Putih
    assert game_state.current_turn == constants.WHITE
    
    # Bidak baru harus ada di (2, 3)
    assert game_state.board.board[2][3] == constants.BLACK
    
    # Bidak lawan yang diapit di (3, 3) harusnya sudah dibalik menjadi Hitam
    assert game_state.board.board[3][3] == constants.BLACK
    
    # Skor harusnya berubah dari {B:2, W:2} menjadi {B:4, W:1}
    assert game_state.scores == {constants.BLACK: 4, constants.WHITE: 1}
    
    assert game_state.game_over == False

def test_make_invalid_move():
    """Tes ini memastikan tidak ada state yang berubah jika langkah tidak valid."""
    # 1. Setup
    game_state = GameState()
    initial_scores = game_state.scores.copy()
    
    # 2. Action
    # Mencoba menempatkan bidak di (0, 0) yang merupakan langkah tidak valid di awal
    move_result = game_state.make_move(0, 0)
    
    # 3. Assert
    assert move_result == False # Metode harus mengembalikan False (gagal)
    
    # Giliran TIDAK BOLEH berubah
    assert game_state.current_turn == constants.BLACK
    
    # Skor TIDAK BOLEH berubah
    assert game_state.scores == initial_scores
    
    # Kotak (0, 0) harus tetap kosong
    assert game_state.board.board[0][0] == constants.EMPTY