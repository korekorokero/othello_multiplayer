# tests/test_game_logic.py

from shared import constants
from game import othello_rules

def test_initial_valid_moves_for_black():
    # Buat papan awal manual untuk tes
    board = [[constants.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = constants.WHITE
    board[3][4] = constants.BLACK
    board[4][3] = constants.BLACK
    board[4][4] = constants.WHITE

    # Untuk BLACK (1), langkah valid harusnya ada di 4 posisi ini
    assert othello_rules.is_valid_move(board, 2, 3, constants.BLACK) == True
    assert othello_rules.is_valid_move(board, 3, 2, constants.BLACK) == True
    assert othello_rules.is_valid_move(board, 5, 4, constants.BLACK) == True
    assert othello_rules.is_valid_move(board, 4, 5, constants.BLACK) == True

    # Langkah di tempat lain harusnya tidak valid
    assert othello_rules.is_valid_move(board, 0, 0, constants.BLACK) == False
    assert othello_rules.is_valid_move(board, 3, 3, constants.BLACK) == False # Sudah diisi

def test_get_flipped_pieces():
    """
    Tes ini memeriksa apakah fungsi get_flipped_pieces mengembalikan
    daftar bidak yang benar untuk dibalik.
    """
    # 1. Setup: Buat kondisi papan yang spesifik
    board = [
        [0, 0, 0, 0, 0],
        [0, 1, 2, 2, 0],  # Baris 1: BLACK, WHITE, WHITE
        [0, 0, 0, 0, 0],
    ]
    # Kita gunakan papan 5x3 untuk mempermudah
    
    # 2. Action: Pemain Hitam (1) menempatkan bidak di (1, 4)
    # Langkah ini akan mengapit dua bidak Putih (2) di (1, 2) dan (1, 3)
    flipped = othello_rules.get_flipped_pieces(board, 1, 4, constants.BLACK)
    
    # 3. Assert: Periksa apakah hasilnya sesuai harapan
    expected_flipped = [(1, 2), (1, 3)]
    
    # Kita sort untuk memastikan urutan tidak mempengaruhi hasil tes
    assert sorted(flipped) == sorted(expected_flipped)

# tests/test_game_logic.py

# ... (kode tes lain yang sudah ada) ...

def test_calculate_score():
    """Memeriksa apakah skor dihitung dengan benar."""
    # 1. Setup
    board = [
        [1, 2, 2, 1],
        [1, 1, 2, 0],
        [0, 0, 1, 2],
    ]
    
    # 2. Action
    score = othello_rules.calculate_score(board)
    
    # 3. Assert
    expected_score = {constants.BLACK: 5, constants.WHITE: 4}
    assert score == expected_score