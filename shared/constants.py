# shared/constants.py
"""
Game constants shared between client and server
"""

# Board dimensions
BOARD_SIZE = 8
BOARD_DIMENSIONS = (BOARD_SIZE, BOARD_SIZE)
TOTAL_CELLS = BOARD_SIZE * BOARD_SIZE

# Player colors
EMPTY = 0
BLACK = 1
WHITE = 2
PLAYER_COLORS = {
    BLACK: "Black",
    WHITE: "White"
}

# Starting player
STARTING_PLAYER = BLACK

# Directions for checking valid moves (8 directions)
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),  # Up-left, Up, Up-right
    (0, -1),           (0, 1),   # Left, Right
    (1, -1),  (1, 0),  (1, 1)    # Down-left, Down, Down-right
]

# Game states
GAME_WAITING = "waiting"
GAME_ACTIVE = "active"
GAME_FINISHED = "finished"
GAME_PAUSED = "paused"

# Game result types
RESULT_WIN = "win"
RESULT_LOSE = "lose"
RESULT_DRAW = "draw"
RESULT_DISCONNECT = "disconnect"

# Network configuration
DEFAULT_SERVER_HOST = "localhost"
DEFAULT_SERVER_PORT = 8888
MAX_PLAYERS_PER_ROOM = 2
ROOM_CODE_LENGTH = 6

# Message buffer size
BUFFER_SIZE = 4096

# Timeouts (in seconds)
CONNECTION_TIMEOUT = 30
MOVE_TIMEOUT = 60
RECONNECTION_TIMEOUT = 300

# Room code characters (alphanumeric, excluding confusing characters)
ROOM_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ123456789"  # No I, O, 0 to avoid confusion