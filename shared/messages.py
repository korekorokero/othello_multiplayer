# othello_multiplayer/shared/messages.py

"""
File ini mendefinisikan "kontrak" atau API untuk komunikasi antara klien dan server.
Setiap tipe pesan didefinisikan sebagai sebuah konstanta string untuk menghindari
kesalahan ketik (typo) dan memastikan konsistensi.

Struktur payload yang direkomendasikan ditulis sebagai komentar untuk setiap pesan.

Notasi:
C2S (Client-to-Server): Pesan yang dikirim dari klien ke server.
S2C (Server-to-Client): Pesan yang dikirim dari server ke klien.
"""

# --- A. Manajemen Room & Sesi ---

# C2S: Klien meminta server untuk membuat room baru.
# Payload: {} (kosong)
C2S_CREATE_ROOM = "c2s_create_room"

# C2S: Klien meminta untuk bergabung ke room yang sudah ada menggunakan kode.
# Payload: {"room_code": "ABCDE"}
C2S_JOIN_ROOM = "c2s_join_room"

# S2C: Server mengirim informasi terbaru tentang sebuah room.
# Dikirim saat room berhasil dibuat atau saat ada perubahan pemain (join/leave).
# Payload: {"room_code": "ABCDE", "players": [{"username": "PemainA", "color": 1}, ...]}
S2C_ROOM_UPDATE = "s2c_room_update"


# --- B. Alur Game Inti ---

# S2C: Server memberitahu semua klien di room bahwa game dimulai.
# Ini adalah pemicu bagi klien untuk beralih ke layar permainan.
# Payload: {"board": [[...]], "starting_player": 1}
S2C_GAME_START = "s2c_game_start"

# C2S: Klien mengirimkan aksi langkah/gerakan mereka ke server.
# Ini adalah satu-satunya aksi utama yang dilakukan pemain selama giliran mereka.
# Payload: {"row": 5, "col": 4}
C2S_MAKE_MOVE = "c2s_make_move"

# S2C: Server menyiarkan (broadcast) keadaan game terbaru ke semua klien.
# Ini adalah pesan yang paling sering dikirim selama permainan.
# Payload: {"board": [[...]], "current_turn": 2, "scores": {"1": 10, "2": 15}}
S2C_GAME_UPDATE = "s2c_game_update"

# S2C: Server memberitahu semua klien bahwa permainan telah berakhir.
# Payload: {"winner": 1, "scores": {"1": 40, "2": 24}}
# 'winner' bisa berisi null/None jika hasilnya seri.
S2C_GAME_OVER = "s2c_game_over"


# --- C. Feedback & Error ---

# S2C: Server mengirim pesan error ke klien tertentu.
# Digunakan untuk memberitahu aksi yang tidak valid atau masalah lainnya.
# Payload: {"message": "Deskripsi error di sini"}
S2C_ERROR = "s2c_error"