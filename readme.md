<div align="center">

# 🎮 Othello Multiplayer Game

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 👥 Tim Pengembang

<div align="center">

| Nama | NRP |
|------|-----|
| Nabilah Atika Rahma | 5025221005 |
| Genta Putra Prayoga | 5025221040 |
| Amanda Illona Farrel | 5025221056 |
| Hilmi Fawwaz Sa'ad | 5025221103 |
| Koresy Samuel Parlinggoman Nainggolan | 5025221141 |

</div>


Sebuah implementasi permainan Othello (Reversi) multiplayer real-time dengan sistem room dan autentikasi user. Dikembangkan menggunakan Python dan Pygame dengan arsitektur client-server.

## 🌟 Features

- 🎯 **Multiplayer Real-time**: Dua pemain dapat bermain secara bersamaan dengan sinkronisasi langsung
- 🏠 **Room System**: Sistem room dengan create/join menggunakan Room ID unik
- 👤 **User Authentication**: Sistem register dan login yang aman dengan bcrypt
- 🎨 **Modern UI**: Interface yang clean dan user-friendly menggunakan Pygame
- ⚡ **Auto Game Start**: Game otomatis dimulai ketika 2 pemain bergabung ke room
- 📊 **Player Stats**: Menampilkan informasi pemain, warna piece, dan giliran bermain


## 🚀 Quick Start Guide

### Persyaratan Sistem
- Python 3.8 atau lebih baru
- Windows/Linux/macOS
- Koneksi internet untuk multiplayer

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Menjalankan Server
Buka terminal/command prompt dan jalankan:
```powershell
python server/main.py
```

**Output yang diharapkan:**
```
==================================================
    OTHELLO MULTIPLAYER SERVER
==================================================
Starting server on 0.0.0.0:55555
Press Ctrl+C to stop the server
==================================================
[Server] Server listening on 0.0.0.0:55555
```

⚠️ **Penting**: Jangan tutup terminal server selama bermain!

### 3. Menjalankan Client (2 Terminal untuk Multiplayer)

#### Terminal Client 1:
```powershell
python client/main.py
```

#### Terminal Client 2 (Terminal baru):
```powershell
python client/main.py
```

### 4. Cara Bermain

#### Langkah-langkah untuk memulai game:

1. **Register/Login** (pada kedua client):
   - Pilih "Register" jika belum punya akun
   - Atau "Login" jika sudah punya akun
   - Masukkan username dan password

2. **Client 1 - Membuat Room**:
   - Klik "Create Room" di menu utama
   - Catat **Room ID** yang muncul (contoh: `ROOM-ABC123`)
   - Tunggu pemain kedua bergabung

3. **Client 2 - Bergabung ke Room**:
   - Klik "Join Room" di menu utama
   - Masukkan **Room ID** dari Client 1
   - Klik "Join"

4. **Game Dimulai**:
   - Game akan otomatis dimulai ketika 2 pemain sudah ada di room
   - Pemain pertama (hitam) mulai duluan
   - Klik pada kotak kosong untuk menempatkan piece
   - Giliran akan berganti secara otomatis

#### Aturan Othello:
- Tempatkan piece untuk mengapit piece lawan
- Piece lawan yang terjepit akan berubah warna menjadi milik Anda
- Pemain dengan piece terbanyak di akhir game menang
- Game berakhir ketika board penuh atau tidak ada move yang valid

## 🏗️ Project Structure

```
othello_multiplayer/
├── 📁 server/                    # Server components
│   ├── main.py                  # ⚡ Server entry point - JALANKAN INI UNTUK SERVER
│   ├── main_server.py           # Core server implementation
│   ├── room_manager.py          # Room management logic
│   ├── game_manager.py          # Game logic management
│   ├── user_manager.py          # User authentication
│   └── protocols.py             # Communication protocols
├── 📁 client/                    # Client components
│   ├── main.py                  # 🎮 Client entry point - JALANKAN INI UNTUK CLIENT
│   ├── network.py               # Network communication
│   ├── constants.py             # Client constants
│   └── 📁 screens/              # UI screens
│       ├── screen_manager.py    # Screen management
│       ├── login_screen.py      # Login interface
│       ├── register_screen.py   # Registration interface
│       ├── menu_screen.py       # Main menu
│       ├── room_screen.py       # Room interface
│       ├── game_screen.py       # Game interface
│       └── profile_screen.py    # User profile
├── 📁 shared/                    # Shared utilities
│   ├── constants.py             # Shared constants
│   ├── messages.py              # Message protocols
│   └── utils.py                 # Utility functions
├── 📁 game/                      # Game logic
│   ├── othello_board.py         # Board implementation
│   └── othello_rules.py         # Game rules
├── 📁 tests/                     # Test files
├── 📁 data/                      # Data storage
│   └── users.json               # User database
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Technical Details

### Architecture
- **Client-Server Model**: Centralized server dengan multiple clients
- **Real-time Communication**: TCP sockets dengan JSON messaging
- **State Synchronization**: Server sebagai source of truth
- **UI Framework**: Pygame untuk rendering dan event handling

### Dependencies
```python
pygame>=2.5.0          # Game rendering dan UI
json5>=0.9.0           # JSON parsing dengan fitur tambahan
bcrypt>=4.0.0          # Password hashing yang aman
pyperclip>=1.8.0       # Clipboard operations
pytest>=7.1.0         # Testing framework
```

### Network Protocol
- **Port**: 55555 (default)
- **Protocol**: TCP dengan JSON messages
- **Message Format**: 
  ```json
  {
    "type": "message_type",
    "data": { "payload": "data" },
    "timestamp": "ISO_timestamp"
  }
  ```

## 🧪 Testing

Menjalankan test suite:
```powershell
python -m pytest tests/
```

Test cases yang tersedia:
- ✅ Room creation dan joining
- ✅ User authentication
- ✅ Real-time game synchronization  
- ✅ Turn management
- ✅ Score updates
- ✅ Network communication

## 🐛 Troubleshooting

### Server Issues
**Problem**: `Address already in use`
```powershell
# Cek port yang sedang digunakan
netstat -ano | findstr :55555

# Kill process jika perlu (ganti PID)
taskkill /PID <PID> /F
```

**Problem**: Server tidak bisa diakses
- Pastikan firewall mengizinkan port 55555
- Coba jalankan sebagai administrator

### Client Issues
**Problem**: Tidak bisa connect ke server
- Pastikan server sedang berjalan
- Cek IP address di `client/constants.py`
- Pastikan tidak ada firewall yang memblokir

**Problem**: Game tidak sync
- Restart kedua client
- Pastikan koneksi internet stabil

### General Issues
**Problem**: Import error
```powershell
pip install --upgrade -r requirements.txt
```

**Problem**: Pygame tidak ter-install
```powershell
pip install pygame --upgrade
```

## 📚 Development Notes

### Untuk Developer
- Server menggunakan threading untuk handle multiple clients
- Game state disimpan di server untuk konsistensi
- UI menggunakan event-driven programming
- Database users.json untuk development (bisa diganti dengan database real)

### Code Style
- Follow PEP 8 untuk Python code style
- Dokumentasi dengan docstrings
- Error handling dengan try-except blocks
- Logging untuk debugging

## 🤝 Contributing

1. Fork repository ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Authors

**Final Project - Pemrograman Jaringan**
- Developed with ❤️ using Python & Pygame
- Real-time multiplayer gaming experience

---

### 🎯 Pro Tips
- Gunakan 2 monitor untuk testing multiplayer di satu PC
- Room ID otomatis ter-copy ke clipboard saat dibuat
- Server log menampilkan semua aktivitas untuk debugging
- Gunakan `Ctrl+C` untuk stop server dengan graceful shutdown

**Selamat bermain Othello! 🎮**