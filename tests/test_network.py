# tests/test_network.py
"""
Unit tests for network communication and message protocols
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.messages import *
from shared.utils import *
from shared.constants import *

class TestMessageProtocol:
    """Test cases for message protocol"""
    
    def test_message_creation(self):
        """Test basic message creation"""
        msg = Message(MSG_LOGIN, {"username": "test", "password": "pass"})
        
        assert msg.type == MSG_LOGIN
        assert msg.data["username"] == "test"
        assert msg.data["password"] == "pass"
    
    def test_message_serialization(self):
        """Test message to/from dict conversion"""
        msg = Message(MSG_CREATE_ROOM, {"player_id": "123"})
        
        # Convert to dict
        msg_dict = msg.to_dict()
        assert msg_dict["type"] == MSG_CREATE_ROOM
        assert msg_dict["data"]["player_id"] == "123"
        
        # Create from dict
        new_msg = Message.from_dict(msg_dict)
        assert new_msg.type == msg.type
        assert new_msg.data == msg.data
    
    def test_predefined_message_creators(self):
        """Test predefined message creation functions"""
        # Login message
        login_msg = create_login_message("user123", "password123")
        assert login_msg.type == MSG_LOGIN
        assert login_msg.data["username"] == "user123"
        assert login_msg.data["password"] == "password123"
        
        # Move message
        move_msg = create_move_message(3, 4)
        assert move_msg.type == MSG_MAKE_MOVE
        assert move_msg.data["row"] == 3
        assert move_msg.data["col"] == 4
        
        # Room join message
        join_msg = create_join_room_message("ABC123")
        assert join_msg.type == MSG_JOIN_ROOM
        assert join_msg.data["room_code"] == "ABC123"
        
        # Error message
        error_msg = create_error_message(ERROR_INVALID_MOVE, "Invalid position")
        assert error_msg.type == MSG_ERROR
        assert error_msg.data["error_code"] == ERROR_INVALID_MOVE
        assert error_msg.data["description"] == "Invalid position"
    
    def test_game_state_message(self):
        """Test game state message creation"""
        board = [[0 for _ in range(8)] for _ in range(8)]
        scores = {BLACK: 10, WHITE: 8}
        valid_moves = [(2, 3), (3, 2)]
        
        game_msg = create_game_state_message(
            board, BLACK, scores, valid_moves, GAME_ACTIVE
        )
        
        assert game_msg.type == MSG_GAME_STATE
        assert game_msg.data["current_player"] == BLACK
        assert game_msg.data["scores"] == scores
        assert game_msg.data["valid_moves"] == valid_moves
        assert game_msg.data["game_status"] == GAME_ACTIVE

class TestUtilityFunctions:
    """Test cases for shared utility functions"""
    
    def test_message_serialization(self):
        """Test JSON serialization/deserialization"""
        test_data = {
            "type": MSG_MAKE_MOVE,
            "data": {"row": 3, "col": 4, "player": BLACK}
        }
        
        # Serialize
        json_str = serialize_message(test_data)
        assert isinstance(json_str, str)
        
        # Deserialize
        restored_data = deserialize_message(json_str)
        assert restored_data == test_data
        
        # Test invalid JSON
        try:
            deserialize_message("invalid json {")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_room_code_generation(self):
        """Test room code generation and validation"""
        # Generate room codes
        codes = [generate_room_code() for _ in range(100)]
        
        # Check all codes have correct length
        assert all(len(code) == ROOM_CODE_LENGTH for code in codes)
        
        # Check all codes use valid characters
        for code in codes:
            assert all(c in ROOM_CODE_CHARS for c in code)
        
        # Check codes are reasonably unique (no duplicates in 100 tries)
        assert len(set(codes)) == 100
    
    def test_room_code_validation(self):
        """Test room code validation"""
        # Valid codes
        assert validate_room_code("ABC123") == True
        assert validate_room_code("DEFGHI") == True
        assert validate_room_code("123456") == True
        
        # Invalid codes
        assert validate_room_code("") == False
        assert validate_room_code("ABC12") == False  # Too short
        assert validate_room_code("ABC1234") == False  # Too long
        assert validate_room_code("ABC12O") == False  # Contains 'O'
        assert validate_room_code("ABC12I") == False  # Contains 'I'
        assert validate_room_code("ABC120") == False  # Contains '0'
        assert validate_room_code(None) == False
    
    def test_username_validation(self):
        """Test username validation"""
        # Valid usernames
        valid, msg = validate_username("user123")
        assert valid == True
        
        valid, msg = validate_username("test_user")
        assert valid == True
        
        valid, msg = validate_username("user-name")
        assert valid == True
        
        # Invalid usernames
        valid, msg = validate_username("")
        assert valid == False
        assert "empty" in msg.lower()
        
        valid, msg = validate_username("ab")
        assert valid == False
        assert "3 characters" in msg
        
        valid, msg = validate_username("a" * 25)
        assert valid == False
        assert "20 characters" in msg
        
        valid, msg = validate_username("user@name")
        assert valid == False
        assert "letters, numbers" in msg
    
    def test_password_validation(self):
        """Test password validation"""
        # Valid passwords
        valid, msg = validate_password("password123")
        assert valid == True
        
        valid, msg = validate_password("MyPass!")
        assert valid == True
        
        # Invalid passwords
        valid, msg = validate_password("")
        assert valid == False
        assert "empty" in msg.lower()
        
        valid, msg = validate_password("short")
        assert valid == False
        assert "6 characters" in msg
        
        valid, msg = validate_password("a" * 55)
        assert valid == False
        assert "50 characters" in msg
    
    def test_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        assert validate_coordinates(0, 0) == True
        assert validate_coordinates(3, 4) == True
        assert validate_coordinates(7, 7) == True
        
        # Invalid coordinates
        assert validate_coordinates(-1, 0) == False
        assert validate_coordinates(0, -1) == False
        assert validate_coordinates(8, 0) == False
        assert validate_coordinates(0, 8) == False
        assert validate_coordinates(10, 10) == False
    
    def test_player_utilities(self):
        """Test player-related utility functions"""
        # Test opposite player
        assert get_opposite_player(BLACK) == WHITE
        assert get_opposite_player(WHITE) == BLACK
        
        # Test score difference
        scores = {BLACK: 15, WHITE: 10}
        assert calculate_score_difference(scores) == 5
        
        scores = {BLACK: 8, WHITE: 12}
        assert calculate_score_difference(scores) == -4
        
        scores = {BLACK: 10, WHITE: 10}
        assert calculate_score_difference(scores) == 0
    
    def test_time_formatting(self):
        """Test time formatting utility"""
        assert format_game_time(0) == "00:00"
        assert format_game_time(30) == "00:30"
        assert format_game_time(60) == "01:00"
        assert format_game_time(125) == "02:05"
        assert format_game_time(3661) == "61:01"
    
    def test_board_utilities(self):
        """Test board-related utilities"""
        # Test empty board
        empty_board = [[EMPTY for _ in range(8)] for _ in range(8)]
        assert is_board_full(empty_board) == False
        
        # Test full board
        full_board = [[BLACK for _ in range(8)] for _ in range(8)]
        assert is_board_full(full_board) == True
        
        # Test partial board
        partial_board = [[BLACK for _ in range(8)] for _ in range(8)]
        partial_board[0][0] = EMPTY
        assert is_board_full(partial_board) == False
        
        # Test deep copy
        original = [[1, 2], [3, 4]]
        copied = deep_copy_board(original)
        copied[0][0] = 99
        assert original[0][0] == 1  # Original unchanged
        assert copied[0][0] == 99   # Copy changed

class TestNetworkConstants:
    """Test network-related constants and configurations"""
    
    def test_message_types_completeness(self):
        """Test that all message types are defined"""
        # Client to server messages
        client_messages = [
            MSG_LOGIN, MSG_REGISTER, MSG_CREATE_ROOM, MSG_JOIN_ROOM,
            MSG_LEAVE_ROOM, MSG_MAKE_MOVE, MSG_READY, MSG_CHAT,
            MSG_DISCONNECT, MSG_PING
        ]
        
        # Server to client messages
        server_messages = [
            MSG_LOGIN_RESPONSE, MSG_REGISTER_RESPONSE, MSG_ROOM_CREATED,
            MSG_ROOM_JOINED, MSG_ROOM_LEFT, MSG_ROOM_ERROR, MSG_GAME_STATE,
            MSG_GAME_START, MSG_GAME_END, MSG_MOVE_RESULT, MSG_INVALID_MOVE,
            MSG_PLAYER_JOINED, MSG_PLAYER_LEFT, MSG_CHAT_MESSAGE,
            MSG_ERROR, MSG_PONG
        ]
        
        # Check all are strings
        all_messages = client_messages + server_messages
        assert all(isinstance(msg, str) for msg in all_messages)
        
        # Check no duplicates
        assert len(set(all_messages)) == len(all_messages)
    
    def test_error_codes(self):
        """Test error code definitions"""
        error_codes = [
            ERROR_INVALID_CREDENTIALS, ERROR_USER_EXISTS, ERROR_ROOM_NOT_FOUND,
            ERROR_ROOM_FULL, ERROR_ALREADY_IN_ROOM, ERROR_NOT_IN_ROOM,
            ERROR_GAME_NOT_ACTIVE, ERROR_NOT_YOUR_TURN, ERROR_INVALID_MOVE,
            ERROR_CONNECTION_LOST, ERROR_SERVER_FULL
        ]
        
        # Check all are strings
        assert all(isinstance(code, str) for code in error_codes)
        
        # Check no duplicates
        assert len(set(error_codes)) == len(error_codes)
    
    def test_game_constants(self):
        """Test game-related constants"""
        assert BOARD_SIZE == 8
        assert TOTAL_CELLS == 64
        assert BLACK == 1
        assert WHITE == 2
        assert EMPTY == 0
        assert STARTING_PLAYER == BLACK
        
        # Check directions array
        assert len(DIRECTIONS) == 8
        assert (-1, -1) in DIRECTIONS  # Up-left
        assert (1, 1) in DIRECTIONS    # Down-right
        assert (0, 1) in DIRECTIONS    # Right
        assert (0, -1) in DIRECTIONS   # Left

def run_network_tests():
    """Run all network tests manually"""
    test_classes = [TestMessageProtocol, TestUtilityFunctions, TestNetworkConstants]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                print(f"Running {test_method}...", end=' ')
                getattr(test_instance, test_method)()
                print("PASSED")
                passed_tests += 1
            except Exception as e:
                print(f"FAILED: {e}")
    
    print(f"\n=== Network Test Results ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    run_network_tests()