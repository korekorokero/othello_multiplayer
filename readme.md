# FP Progjar Othello-Multiplayer

## Overview
Aplikasi Othello Multiplayer dengan fitur room system yang memungkinkan dua pemain bermain secara online real-time.

## Features
- ✅ **Multiplayer Gaming**: Dua pemain dapat bermain bersamaan secara online
- ✅ **Room System**: Sistem room dengan create/join menggunakan Room ID
- ✅ **Real-time Updates**: Gerakan dan skor diperbarui secara real-time
- ✅ **Player Information**: Menampilkan nama pemain, warna piece, dan giliran bermain
- ✅ **Auto Game Start**: Game otomatis dimulai ketika 2 pemain masuk room
- ✅ **User Authentication**: System register dan login
- ✅ **Modern UI**: Interface yang clean dan user-friendly

## Quick Start

### 1. Start Server
```powershell
python run_server.py
```

### 2. Start Clients (2 terminals)
```powershell
cd client
python main.py
```

### 3. Play Game
1. Register/Login pada kedua client
2. Client 1: Create room → dapatkan Room ID
3. Client 2: Join room menggunakan Room ID
4. Game otomatis dimulai!

## Project Structure
```
othello_multiplayer/
├── server/                 # Server components
│   ├── main_server.py     # Main server entry point
│   ├── room_manager.py    # Room management logic
│   ├── game_manager.py    # Game logic management
│   ├── user_manager.py    # User authentication
│   └── protocols.py       # Communication protocols
├── client/                 # Client components
│   ├── main.py           # Client entry point
│   ├── network.py        # Network communication
│   ├── screens/          # UI screens
│   └── ui/               # UI components
├── shared/                # Shared utilities
├── tests/                 # Test files
└── run_server.py         # Server launcher
```

## Technical Details
- **Language**: Python 3.x
- **UI Framework**: Pygame
- **Network**: TCP Sockets with JSON messaging
- **Architecture**: Client-Server with real-time synchronization

## Documentation
- See `MULTIPLAYER_INTEGRATION.md` for detailed integration guide
- See `notes.md` for development notes

## Test Cases
✅ Room creation dan joining
✅ User authentication
✅ Real-time game synchronization
✅ Turn management
✅ Score updates
✅ Player information display

## Authors
Final Project - Pemrograman Jaringan