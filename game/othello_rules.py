# othello_multiplayer/game/othello_rules.py

from shared import constants

DIRECTIONS = [
    (0, 1), (1, 1), (1, 0), (1, -1),
    (0, -1), (-1, -1), (-1, 0), (-1, 1)
] # 8 arah: Kanan, Kanan-Bawah, Bawah, ... Kanan-Atas

def is_valid_move(board_state, row, col, color):
    """
    Memeriksa apakah sebuah langkah valid.
    Sebuah langkah valid jika:
    1. Kotak tersebut kosong.
    2. Menempatkan bidak di sana akan membalik setidaknya satu bidak lawan.
    """
    if not (0 <= row < constants.BOARD_HEIGHT and 0 <= col < constants.BOARD_WIDTH) or board_state[row][col] != constants.EMPTY:
        return False

    other_color = constants.WHITE if color == constants.BLACK else constants.BLACK

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        pieces_to_flip_in_this_direction = []

        # Bergerak ke satu arah selama masih di dalam papan dan menemukan bidak lawan
        while (0 <= r < constants.BOARD_HEIGHT and 0 <= c < constants.BOARD_WIDTH) and board_state[r][c] == other_color:
            pieces_to_flip_in_this_direction.append((r, c))
            r, c = r + dr, c + dc
        
        # Jika setelah barisan bidak lawan kita menemukan bidak kita sendiri, maka langkahnya valid
        if (0 <= r < constants.BOARD_HEIGHT and 0 <= c < constants.BOARD_WIDTH) and board_state[r][c] == color:
            if len(pieces_to_flip_in_this_direction) > 0:
                return True # Ditemukan setidaknya satu arah yang valid

    return False # Tidak ada arah yang valid


# game/othello_rules.py

def get_flipped_pieces(board_state, row, col, color):
    """
    Mengembalikan daftar semua bidak yang akan terbalik jika sebuah langkah
    dibuat di (row, col) oleh 'color'.
    Fungsi ini berasumsi bahwa langkah yang diberikan SUDAH VALID.
    """
    # --- PERBAIKAN DIMULAI DI SINI ---
    # Dapatkan ukuran papan dari argumen, bukan dari konstanta global.
    height = len(board_state)
    if height == 0:
        return [] # Papan kosong, tidak ada yang bisa di-flip
    width = len(board_state[0])
    # --- PERBAIKAN SELESAI ---

    other_color = constants.WHITE if color == constants.BLACK else constants.BLACK
    
    all_flipped_pieces = []

    for dr, dc in DIRECTIONS:
        pieces_to_flip_in_this_direction = []
        r, c = row + dr, col + dc

        # Bergerak ke satu arah selama masih di dalam papan dan menemukan bidak lawan
        # --- UBAH BARIS INI ---
        while (0 <= r < height and 0 <= c < width) and board_state[r][c] == other_color:
        # --- DARI constants.BOARD_HEIGHT/WIDTH MENJADI height/width ---
            pieces_to_flip_in_this_direction.append((r, c))
            r, c = r + dr, c + dc
        
        # Jika setelah barisan bidak lawan kita menemukan bidak kita sendiri,
        # maka semua bidak di 'pieces_to_flip_in_this_direction' valid untuk dibalik.
        # --- UBAH BARIS INI JUGA ---
        if (0 <= r < height and 0 <= c < width) and board_state[r][c] == color:
        # --- AGAR KONSISTEN ---
            all_flipped_pieces.extend(pieces_to_flip_in_this_direction)

    return all_flipped_pieces

def get_valid_moves(board_state, color):
    """
    Mengembalikan daftar berisi semua kemungkinan langkah (row, col)
    yang valid untuk pemain dengan 'color' tertentu.
    """
    valid_moves = []
    for r in range(constants.BOARD_HEIGHT):
        for c in range(constants.BOARD_WIDTH):
            if is_valid_move(board_state, r, c, color):
                valid_moves.append((r, c))
    return valid_moves

def calculate_score(board_state):
    """
    Menghitung dan mengembalikan skor (jumlah bidak) untuk kedua pemain
    dalam bentuk dictionary.
    """
    score = {constants.BLACK: 0, constants.WHITE: 0}
    for row in board_state:
        for cell in row:
            if cell == constants.BLACK:
                score[constants.BLACK] += 1
            elif cell == constants.WHITE:
                score[constants.WHITE] += 1
    return score