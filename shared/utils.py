# shared/utils.py
"""
Shared utility functions used by both client and server
"""

import json
import random
import string
from typing import Dict, Any, Optional
from .constants import ROOM_CODE_CHARS, ROOM_CODE_LENGTH

def serialize_message(message_dict: Dict[str, Any]) -> str:
    """
    Serialize a message dictionary to JSON string
    
    Args:
        message_dict: Dictionary containing message data
        
    Returns:
        JSON string representation of the message
    """
    try:
        return json.dumps(message_dict, separators=(',', ':'))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize message: {e}")

def deserialize_message(message_str: str) -> Dict[str, Any]:
    """
    Deserialize a JSON string to message dictionary
    
    Args:
        message_str: JSON string containing message data
        
    Returns:
        Dictionary representation of the message
    """
    try:
        return json.loads(message_str)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Failed to deserialize message: {e}")

def generate_room_code() -> str:
    """
    Generate a unique room code for game sessions
    
    Returns:
        6-character alphanumeric room code
    """
    return ''.join(random.choices(ROOM_CODE_CHARS, k=ROOM_CODE_LENGTH))

def validate_room_code(room_code: str) -> bool:
    """
    Validate if a room code has the correct format
    
    Args:
        room_code: Room code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not room_code or len(room_code) != ROOM_CODE_LENGTH:
        return False
    
    return all(c in ROOM_CODE_CHARS for c in room_code.upper())

def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format and requirements
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 20:
        return False, "Username must be no more than 20 characters long"
    
    if not username.replace('_', '').replace('-', '').isalnum():
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength requirements
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 50:
        return False, "Password must be no more than 50 characters long"
    
    return True, ""

def validate_coordinates(row: int, col: int, board_size: int = 8) -> bool:
    """
    Validate if coordinates are within board bounds
    
    Args:
        row: Row coordinate (0-based)
        col: Column coordinate (0-based)
        board_size: Size of the board (default 8)
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return 0 <= row < board_size and 0 <= col < board_size

def get_opposite_player(player: int) -> int:
    """
    Get the opposite player color
    
    Args:
        player: Current player (1 for BLACK, 2 for WHITE)
        
    Returns:
        Opposite player color
    """
    from .constants import BLACK, WHITE
    return WHITE if player == BLACK else BLACK

def format_game_time(seconds: int) -> str:
    """
    Format game time in seconds to MM:SS format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def calculate_score_difference(scores: Dict[int, int]) -> int:
    """
    Calculate the score difference between players
    
    Args:
        scores: Dictionary with player scores
        
    Returns:
        Score difference (positive if BLACK leads, negative if WHITE leads)
    """
    from .constants import BLACK, WHITE
    return scores.get(BLACK, 0) - scores.get(WHITE, 0)

def is_board_full(board: list) -> bool:
    """
    Check if the game board is completely filled
    
    Args:
        board: 2D list representing the game board
        
    Returns:
        True if board is full, False otherwise
    """
    from .constants import EMPTY
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True

def deep_copy_board(board: list) -> list:
    """
    Create a deep copy of the game board
    
    Args:
        board: 2D list representing the game board
        
    Returns:
        Deep copy of the board
    """
    return [row[:] for row in board]