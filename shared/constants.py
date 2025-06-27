# othello_multiplayer/shared/constants.py

"""
File ini berisi konstanta fundamental yang digunakan bersama oleh server dan klien.
Memastikan semua bagian dari aplikasi menggunakan nilai yang sama untuk hal-hal
penting seperti representasi bidak dan ukuran papan.
"""

# --- Dimensi Papan Permainan ---
# Ukuran standar untuk Othello adalah 8x8.
BOARD_WIDTH = 8
BOARD_HEIGHT = 8

# --- Representasi Bidak dan Pemain ---
# Menggunakan integer untuk efisiensi dalam logika game dan pengiriman data.
# Ini adalah bagian paling kritikal yang harus disepakati.
EMPTY = 0      # Merepresentasikan kotak kosong di papan
BLACK = 1      # Merepresentasikan bidak hitam (biasanya pemain 1)
WHITE = 2      # Merepresentasikan bidak putih (biasanya pemain 2)