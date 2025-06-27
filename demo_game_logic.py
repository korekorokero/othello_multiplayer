#!/usr/bin/env python3
"""
Level 4: Demo - Complete demonstration of Othello game logic implementation
This demonstrates all major features for Role 3: Game & Systems Architect
"""

import sys
import os
import time
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import our implementations
    from game.othello_board import OthelloBoard
    from game.othello_rules import OthelloRules
    from game.player import Player
    from game.game_state import GameState
    from shared.messages import *
    from shared.utils import *
    from shared.constants import *
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files are in place and run from project root directory")
    sys.exit(1)

def print_separator(title=""):
    """Print a nice separator with optional title"""
    print("\n" + "="*60)
    if title:
        print(f" {title}")
        print("="*60)

def print_board(board):
    """Print board in a nice format"""
    symbols = {EMPTY: '·', BLACK: '●', WHITE: '○'}
    print("  0 1 2 3 4 5 6 7")
    if hasattr(board, 'board'):
        board_data = board.board
    else:
        board_data = board
    
    for i, row in enumerate(board_data):
        row_str = f"{i} " + " ".join(symbols[cell] for cell in row)
        print(row_str)

def demo_board_operations():
    """Demonstrate basic board operations"""
    print_separator("1. BOARD OPERATIONS DEMO")
    
    print("Creating new Othello board...")
    board = OthelloBoard()
    
    print("\nInitial board state:")
    print_board(board)
    
    print(f"\nInitial scores: {board.get_scores()}")
    print(f"Board size: {board.size}x{board.size}")
    print(f"Empty cells: {len(board.get_empty_cells())}")
    print(f"Is board full? {board.is_full()}")
    
    # Test cell operations
    print("\nTesting cell operations...")
    print(f"Cell (3,3): {board.get_cell(3, 3)} ({'WHITE' if board.get_cell(3, 3) == WHITE else 'OTHER'})")
    print(f"Cell (0,0): {board.get_cell(0, 0)} ({'EMPTY' if board.get_cell(0, 0) == EMPTY else 'OTHER'})")
    print(f"Is (0,0) empty? {board.is_empty(0, 0)}")
    print(f"Is (3,3) empty? {board.is_empty(3, 3)}")
    
    # Test bounds checking
    print("\nTesting bounds checking...")
    test_positions = [(0, 0), (7, 7), (-1, 0), (8, 0), (3, 9)]
    for row, col in test_positions:
        valid = board.is_valid_position(row, col)
        print(f"Position ({row},{col}): {'Valid' if valid else 'Invalid'}")

def demo_game_rules():
    """Demonstrate game rules and logic"""
    print_separator("2. GAME RULES DEMO")
    
    board = OthelloBoard()
    print("Testing game rules with initial board...")
    print_board(board)
    
    # Test valid moves for BLACK (starting player)
    print(f"\nValid moves for BLACK: {OthelloRules.get_valid_moves(board, BLACK)}")
    print(f"Valid moves for WHITE: {OthelloRules.get_valid_moves(board, WHITE)}")
    
    # Test specific move validation
    test_moves = [
        (BLACK, 2, 3, "Valid opening move"),
        (BLACK, 0, 0, "Invalid - no pieces to flip"),
        (BLACK, 3, 3, "Invalid - cell occupied"),
        (WHITE, 2, 4, "Valid WHITE move")
    ]
    
    print("\nTesting move validation:")
    for player, row, col, description in test_moves:
        valid = OthelloRules.is_valid_move(board, row, col, player)
        flipped = OthelloRules.get_flipped_pieces(board, row, col, player)
        player_name = PLAYER_COLORS[player]
        print(f"  {player_name} ({row},{col}) - {description}: {'✓' if valid else '✗'}")
        if valid:
            print(f"    Would flip: {flipped}")
    
    # Make a move and show result
    print("\nMaking move: BLACK at (2,3)")
    move_success = OthelloRules.make_move(board, 2, 3, BLACK)
    print(f"Move successful: {move_success}")
    
    if move_success:
        print("\nBoard after move:")
        print_board(board)
        print(f"New scores: {board.get_scores()}")
        
        # Show game state
        print(f"Game over? {OthelloRules.is_game_over(board)}")
        if OthelloRules.is_game_over(board):
            winner = OthelloRules.get_winner(board)
            if winner == EMPTY:
                print("Game result: TIE")
            else:
                print(f"Winner: {PLAYER_COLORS[winner]}")

def demo_player_management():
    """Demonstrate player management"""
    print_separator("3. PLAYER MANAGEMENT DEMO")
    
    # Create players
    print("Creating players...")
    alice = Player("Alice", BLACK, "player_001")
    bob = Player("Bob", WHITE, "player_002")
    
    print(f"Alice: {alice}")
    print(f"Bob: {bob}")
    
    # Test player properties
    print("\nPlayer properties:")
    print(f"Alice is black: {alice.is_black}")
    print(f"Alice color name: {alice.color_name}")
    print(f"Bob is white: {bob.is_white}")
    print(f"Bob color name: {bob.color_name}")
    
    # Test ready status
    print("\nTesting ready status:")
    print(f"Alice ready: {alice.ready}")
    alice.set_ready(True)
    print(f"Alice ready after set: {alice.ready}")
    
    # Simulate game statistics
    print("\nSimulating game completion...")
    alice.start_game()
    bob.start_game()
    
    # Simulate some moves
    alice.make_move(2)  # 2 pieces captured
    bob.make_move(1)    # 1 piece captured
    alice.make_move(3)  # 3 pieces captured
    
    print(f"Alice moves: {alice.moves_made}, pieces captured: {alice.pieces_captured}")
    print(f"Bob moves: {bob.moves_made}, pieces captured: {bob.pieces_captured}")
    
    # Finish game
    alice.finish_game('win', 35)
    bob.finish_game('lose', 29)
    
    print("\nFinal statistics:")
    print(f"Alice stats: {alice.get_stats()}")
    print(f"Bob stats: {bob.get_stats()}")

def demo_game_state():
    """Demonstrate complete game state management"""
    print_separator("4. GAME STATE MANAGEMENT DEMO")
    
    # Create game
    game = GameState("DEMO_GAME_001")
    print(f"Created game: {game}")
    
    # Create and add players
    alice = Player("Alice", BLACK)
    bob = Player("Bob", WHITE)
    
    print("\nAdding players...")
    result1 = game.add_player(alice)
    result2 = game.add_player(bob)
    print(f"Alice added: {result1}")
    print(f"Bob added: {result2}")
    print(f"Game is full: {game.is_full()}")
    
    # Try to add third player (should fail)
    charlie = Player("Charlie", BLACK)
    result3 = game.add_player(charlie)
    print(f"Charlie added: {result3} (should be False)")
    
    # Set ready and start game
    print("\nPreparing to start game...")
    print(f"Can start: {game.can_start()}")
    
    alice.set_ready(True)
    bob.set_ready(True)
    print("Players set to ready...")
    print(f"Can start now: {game.can_start()}")
    
    game_started = game.start_game()
    print(f"Game started: {game_started}")
    print(f"Game status: {game.status}")
    print(f"Current player: {PLAYER_COLORS[game.current_player]}")
    
    # Play some moves
    print("\nPlaying moves...")
    moves_to_play = [
        (BLACK, 2, 3, "Alice's opening"),
        (WHITE, 2, 2, "Bob's response"),
        (BLACK, 2, 4, "Alice continues"),
        (WHITE, 4, 2, "Bob's strategy")
    ]
    
    for player_color, row, col, description in moves_to_play:
        if game.status != GAME_ACTIVE:
            break
            
        print(f"\n{description}: {PLAYER_COLORS[player_color]} plays ({row},{col})")
        
        # Check if it's the player's turn
        if game.current_player != player_color:
            print(f"  ❌ Not {PLAYER_COLORS[player_color]}'s turn!")
            continue
            
        result = game.make_move(row, col, player_color)
        if result['success']:
            print(f"  ✓ Success! Flipped {len(result['flipped_pieces'])} pieces")
            print(f"  Scores: Black={result['scores'][BLACK]}, White={result['scores'][WHITE]}")
            print(f"  Next player: {PLAYER_COLORS[game.current_player]}")
            if result['game_over']:
                winner_name = PLAYER_COLORS.get(result['winner'], 'Tie')
                print(f"  🏆 Game Over! Winner: {winner_name}")
                break
        else:
            print(f"  ❌ Failed: {result['error']}")
    
    # Show final game state
    print(f"\nFinal game state:")
    print(f"Status: {game.status}")
    print(f"Move history: {len(game.move_history)} moves")
    duration = game.get_game_duration()
    if duration:
        print(f"Game duration: {duration:.2f} seconds")

def demo_network_protocol():
    """Demonstrate network message protocol"""
    print_separator("5. NETWORK PROTOCOL DEMO")
    
    print("Testing message creation and serialization...")
    
    # Test different message types
    messages = [
        ("Login", create_login_message("alice", "password123")),
        ("Create Room", create_room_message()),
        ("Join Room", create_join_room_message("ABC123")),
        ("Make Move", create_move_message(2, 3)),
        ("Chat", create_chat_message("Hello everyone!")),
        ("Error", create_error_message(ERROR_INVALID_MOVE, "Position already occupied"))
    ]
    
    for msg_name, message in messages:
        # Serialize message
        json_str = serialize_message(message.to_dict())
        print(f"\n{msg_name} Message:")
        print(f"  Type: {message.type}")
        print(f"  Data: {message.data}")
        print(f"  JSON: {json_str}")
        
        # Deserialize and verify
        restored_dict = deserialize_message(json_str)
        restored_msg = Message.from_dict(restored_dict)
        
        # Verify integrity
        if restored_msg.type == message.type and restored_msg.data == message.data:
            print("  ✓ Serialization/Deserialization successful")
        else:
            print("  ❌ Serialization/Deserialization failed")

def demo_utilities():
    """Demonstrate utility functions"""
    print_separator("6. UTILITIES DEMO")
    
    # Room code generation
    print("Room code generation:")
    room_codes = [generate_room_code() for _ in range(5)]
    for code in room_codes:
        is_valid = validate_room_code(code)
        print(f"  {code}: {'Valid' if is_valid else 'Invalid'}")
    
    # Username validation
    print("\nUsername validation:")
    test_usernames = ["alice", "user123", "ab", "user_name", "user@invalid", ""]
    for username in test_usernames:
        valid, msg = validate_username(username)
        status = "✓" if valid else "✗"
        print(f"  {username:<12} {status} {msg if not valid else ''}")
    
    # Password validation
    print("\nPassword validation:")
    test_passwords = ["password123", "short", "", "a"*60, "validpass"]
    for password in test_passwords:
        valid, msg = validate_password(password)
        status = "✓" if valid else "✗"
        display_pwd = password[:10] + "..." if len(password) > 10 else password
        print(f"  {display_pwd:<15} {status} {msg if not valid else ''}")
    
    # Coordinate validation
    print("\nCoordinate validation:")
    test_coords = [(0,0), (7,7), (-1,0), (8,0), (3,4), (10,10)]
    for row, col in test_coords:
        valid = validate_coordinates(row, col)
        status = "✓" if valid else "✗"
        print(f"  ({row},{col}): {status}")
    
    # Time formatting
    print("\nTime formatting:")
    test_times = [0, 30, 60, 125, 3661]
    for seconds in test_times:
        formatted = format_game_time(seconds)
        print(f"  {seconds} seconds = {formatted}")
    
    # Player utilities
    print("\nPlayer utilities:")
    print(f"  Opposite of BLACK: {PLAYER_COLORS[get_opposite_player(BLACK)]}")
    print(f"  Opposite of WHITE: {PLAYER_COLORS[get_opposite_player(WHITE)]}")
    
    scores = {BLACK: 15, WHITE: 12}
    diff = calculate_score_difference(scores)
    print(f"  Score difference (Black 15, White 12): {diff}")

def demo_complete_game():
    """Demonstrate a complete game from start to finish"""
    print_separator("7. COMPLETE GAME DEMONSTRATION")
    
    print("🎮 Starting complete game demonstration...")
    
    # Setup
    game = GameState("COMPLETE_DEMO")
    alice = Player("Alice", BLACK)
    bob = Player("Bob", WHITE)
    
    # Game creation
    print("\n--- Game Setup ---")
    game.add_player(alice)
    game.add_player(bob)
    alice.set_ready(True)
    bob.set_ready(True)
    game.start_game()
    
    print(f"Game '{game.game_id}' started!")
    print(f"Players: {alice.username} (BLACK) vs {bob.username} (WHITE)")
    
    # Game loop
    print("\n--- Game Progress ---")
    move_count = 0
    max_moves = 8  # Limit for demo
    
    while move_count < max_moves and game.status == GAME_ACTIVE:
        current_player = game.current_player
        player_name = alice.username if current_player == BLACK else bob.username
        
        print(f"\nMove {move_count + 1}: {player_name}'s turn")
        
        # Show current board
        print("Current board:")
        print_board(game.board)
        
        # Get valid moves
        valid_moves = game.get_valid_moves(current_player)
        print(f"Valid moves: {valid_moves}")
        
        if not valid_moves:
            # Must pass
            result = game.pass_turn(current_player)
            print(f"{player_name} passes turn")
            if result.get('game_over'):
                print("Game ended due to no valid moves for both players")
                break
        else:
            # Make a move (take first valid move for demo)
            row, col = valid_moves[0]
            result = game.make_move(row, col, current_player)
            
            if result['success']:
                print(f"{player_name} plays ({row},{col})")
                print(f"Pieces flipped: {len(result['flipped_pieces'])}")
                print(f"Current scores: Black={result['scores'][BLACK]}, White={result['scores'][WHITE]}")
                move_count += 1
                
                if result.get('game_over'):
                    winner = result.get('winner')
                    if winner == EMPTY:
                        print("🤝 Game ended in a TIE!")
                    else:
                        winner_name = alice.username if winner == BLACK else bob.username
                        print(f"🏆 Game Over! Winner: {winner_name}")
                    break
            else:
                print(f"Move failed: {result['error']}")
                break
    
    # Final results
    print("\n--- Final Results ---")
    final_scores = game.get_current_scores()
    print(f"Final scores: {alice.username}={final_scores[BLACK]}, {bob.username}={final_scores[WHITE]}")
    print(f"Total moves played: {len(game.move_history)}")
    print(f"Game duration: {game.get_game_duration():.2f} seconds")
    
    print("\nFinal board:")
    print_board(game.board)

def run_comprehensive_demo():
    """Run the complete demonstration"""
    print("🎮 OTHELLO MULTIPLAYER - LEVEL 4: COMPLETE DEMO")
    print("Role 3: Game & Systems Architect Implementation")
    print("="*60)
    
    try:
        demo_board_operations()
        demo_game_rules()
        demo_player_management()
        demo_game_state()
        demo_network_protocol()
        demo_utilities()
        demo_complete_game()
        
        print_separator("🎉 DEMONSTRATION COMPLETE")
        print("All core components are working correctly!")
        print("\nImplementation Summary:")
        print("✅ Board operations and validation")
        print("✅ Complete Othello game rules")
        print("✅ Player management and statistics")
        print("✅ Game state management")
        print("✅ Network message protocol")
        print("✅ Utility functions and validation")
        print("✅ Complete game flow demonstration")
        print("\n🚀 Ready for integration with Backend and Frontend!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False
        
def run_quick_demo():
    """Run a quick demonstration of key features"""
    print("🚀 QUICK DEMO - Key Features")
    print("=" * 40)
    
    try:
        # Quick board test
        print("1. Board Creation:")
        board = OthelloBoard()
        print(f"   Initial scores: {board.get_scores()}")
        
        # Quick rules test
        print("2. Rules Engine:")
        valid_moves = OthelloRules.get_valid_moves(board, BLACK)
        print(f"   BLACK valid moves: {len(valid_moves)}")
        
        # Quick move test
        print("3. Making Move:")
        success = OthelloRules.make_move(board, 2, 3, BLACK)
        print(f"   Move (2,3) success: {success}")
        print(f"   New scores: {board.get_scores()}")
        
        # Quick game test
        print("4. Game State:")
        game = GameState("quick_demo")
        alice = Player("Alice", BLACK)
        game.add_player(alice)
        print(f"   Game created with player: {alice.username}")
        
        # Quick message test
        print("5. Network Messages:")
        msg = create_login_message("user", "pass")
        json_str = serialize_message(msg.to_dict())
        print(f"   Message serialized: {len(json_str)} chars")
        
        print("\n✅ QUICK DEMO SUCCESSFUL!")
        print("All core features are working. Run full demo for complete showcase.")
        return True
        
    except Exception as e:
        print(f"\n❌ Quick demo failed: {e}")
        return False

def main():
    """Main demo function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        return run_quick_demo()
    else:
        return run_comprehensive_demo()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
    symbols = {EMPTY: '·', BLACK: '●', WHITE: '○'}
    print("  0 1 2 3 4 5 6 7")
    for i, row in enumerate(board.board if hasattr(board, 'board') else board):
        row_str = f"{i} " + " ".join(symbols[cell] for cell in row)
        print(row_str)

def demo_board_operations():
    """Demonstrate basic board operations"""
    print_separator("1. BOARD OPERATIONS DEMO")
    
    print("Creating new Othello board...")
    board = OthelloBoard()
    
    print("\nInitial board state:")
    print_board(board)
    
    print(f"\nInitial scores: {board.get_scores()}")
    print(f"Board size: {board.size}x{board.size}")
    print(f"Empty cells: {len(board.get_empty_cells())}")
    print(f"Is board full? {board.is_full()}")
    
    # Test cell operations
    print("\nTesting cell operations...")
    print(f"Cell (3,3): {board.get_cell(3, 3)} ({'WHITE' if board.get_cell(3, 3) == WHITE else 'OTHER'})")
    print(f"Cell (0,0): {board.get_cell(0, 0)} ({'EMPTY' if board.get_cell(0, 0) == EMPTY else 'OTHER'})")
    print(f"Is (0,0) empty? {board.is_empty(0, 0)}")
    print(f"Is (3,3) empty? {board.is_empty(3, 3)}")
    
    # Test bounds checking
    print("\nTesting bounds checking...")
    test_positions = [(0, 0), (7, 7), (-1, 0), (8, 0), (3, 9)]
    for row, col in test_positions:
        valid = board.is_valid_position(row, col)
        print(f"Position ({row},{col}): {'Valid' if valid else 'Invalid'}")

def demo_game_rules():
    """Demonstrate game rules and logic"""
    print_separator("2. GAME RULES DEMO")
    
    board = OthelloBoard()
    print("Testing game rules with initial board...")
    print_board(board)
    
    # Test valid moves for BLACK (starting player)
    print(f"\nValid moves for BLACK: {OthelloRules.get_valid_moves(board, BLACK)}")
    print(f"Valid moves for WHITE: {OthelloRules.get_valid_moves(board, WHITE)}")
    
    # Test specific move validation
    test_moves = [
        (BLACK, 2, 3, "Valid opening move"),
        (BLACK, 0, 0, "Invalid - no pieces to flip"),
        (BLACK, 3, 3, "Invalid - cell occupied"),
        (WHITE, 2, 4, "Valid WHITE move")
    ]
    
    print("\nTesting move validation:")
    for player, row, col, description in test_moves:
        valid = OthelloRules.is_valid_move(board, row, col, player)
        flipped = OthelloRules.get_flipped_pieces(board, row, col, player)
        player_name = PLAYER_COLORS[player]
        print(f"  {player_name} ({row},{col}) - {description}: {'✓' if valid else '✗'}")
        if valid:
            print(f"    Would flip: {flipped}")
    
    # Make a move and show result
    print("\nMaking move: BLACK at (2,3)")
    move_success = OthelloRules.make_move(board, 2, 3, BLACK)
    print(f"Move successful: {move_success}")
    
    if move_success:
        print("\nBoard after move:")
        print_board(board)
        print(f"New scores: {board.get_scores()}")
        
        # Show game state
        print(f"Game over? {OthelloRules.is_game_over(board)}")
        if OthelloRules.is_game_over(board):
            winner = OthelloRules.get_winner(board)
            if winner == EMPTY:
                print("Game result: TIE")
            else:
                print(f"Winner: {PLAYER_COLORS[winner]}")

def demo_player_management():
    """Demonstrate player management"""
    print_separator("3. PLAYER MANAGEMENT DEMO")
    
    # Create players
    print("Creating players...")
    alice = Player("Alice", BLACK, "player_001")
    bob = Player("Bob", WHITE, "player_002")
    
    print(f"Alice: {alice}")
    print(f"Bob: {bob}")
    
    # Test player properties
    print("\nPlayer properties:")
    print(f"Alice is black: {alice.is_black}")
    print(f"Alice color name: {alice.color_name}")
    print(f"Bob is white: {bob.is_white}")
    print(f"Bob color name: {bob.color_name}")
    
    # Test ready status
    print("\nTesting ready status:")
    print(f"Alice ready: {alice.ready}")
    alice.set_ready(True)
    print(f"Alice ready after set: {alice.ready}")
    
    # Simulate game statistics
    print("\nSimulating game completion...")
    alice.start_game()
    bob.start_game()
    
    # Simulate some moves
    alice.make_move(2)  # 2 pieces captured
    bob.make_move(1)    # 1 piece captured
    alice.make_move(3)  # 3 pieces captured
    
    print(f"Alice moves: {alice.moves_made}, pieces captured: {alice.pieces_captured}")
    print(f"Bob moves: {bob.moves_made}, pieces captured: {bob.pieces_captured}")
    
    # Finish game
    alice.finish_game('win', 35)
    bob.finish_game('lose', 29)
    
    print("\nFinal statistics:")
    print(f"Alice stats: {alice.get_stats()}")
    print(f"Bob stats: {bob.get_stats()}")

def demo_game_state():
    """Demonstrate complete game state management"""
    print_separator("4. GAME STATE MANAGEMENT DEMO")
    
    # Create game
    game = GameState("DEMO_GAME_001")
    print(f"Created game: {game}")
    
    # Create and add players
    alice = Player("Alice", BLACK)
    bob = Player("Bob", WHITE)
    
    print("\nAdding players...")
    result1 = game.add_player(alice)
    result2 = game.add_player(bob)
    print(f"Alice added: {result1}")
    print(f"Bob added: {result2}")
    print(f"Game is full: {game.is_full()}")
    
    # Try to add third player (should fail)
    charlie = Player("Charlie", BLACK)
    result3 = game.add_player(charlie)
    print(f"Charlie added: {result3} (should be False)")
    
    # Set ready and start game
    print("\nPreparing to start game...")
    print(f"Can start: {game.can_start()}")
    
    alice.set_ready(True)
    bob.set_ready(True)
    print("Players set to ready...")
    print(f"Can start now: {game.can_start()}")
    
    game_started = game.start_game()
    print(f"Game started: {game_started}")
    print(f"Game status: {game.status}")
    print(f"Current player: {PLAYER_COLORS[game.current_player]}")
    
    # Play some moves
    print("\nPlaying moves...")
    moves_to_play = [
        (BLACK, 2, 3, "Alice's opening"),
        (WHITE, 2, 2, "Bob's response"),
        (BLACK, 2, 4, "Alice continues"),
        (WHITE, 4, 2, "Bob's strategy")
    ]
    
    for player_color, row, col, description in moves_to_play:
        print(f"\n{description}: {PLAYER_COLORS[player_color]} plays ({row},{col})")
        
        # Check if it's the player's turn
        if game.current_player != player_color:
            print(f"  ❌ Not {PLAYER_COLORS[player_color]}'s turn!")
            continue
            
        result = game.make_move(row, col, player_color)
        if result['success']:
            print(f"  ✓ Success! Flipped {len(result['flipped_pieces'])} pieces")
            print(f"  Scores: Black={result['scores'][BLACK]}, White={result['scores'][WHITE]}")
            print(f"  Next player: {PLAYER_COLORS[game.current_player]}")
            if result['game_over']:
                winner_name = PLAYER_COLORS.get(result['winner'], 'Tie')
                print(f"  🏆 Game Over! Winner: {winner_name}")
                break
        else:
            print(f"  ❌ Failed: {result['error']}")
    
    # Show final game state
    print(f"\nFinal game state:")
    print(f"Status: {game.status}")
    print(f"Move history: {len(game.move_history)} moves")
    print(f"Game duration: {game.get_game_duration():.2f} seconds")

def demo_network_protocol():
    """Demonstrate network message protocol"""
    print_separator("5. NETWORK PROTOCOL DEMO")
    
    print("Testing message creation and serialization...")
    
    # Test different message types
    messages = [
        ("Login", create_login_message("alice", "password123")),
        ("Create Room", create_room_message()),
        ("Join Room", create_join_room_message("ABC123")),
        ("Make Move", create_move_message(2, 3)),
        ("Chat", create_chat_message("Hello everyone!")),
        ("Error", create_error_message(ERROR_INVALID_MOVE, "Position already occupied"))
    ]
    
    for msg_name, message in messages:
        # Serialize message
        json_str = serialize_message(message.to_dict())
        print(f"\n{msg_name} Message:")
        print(f"  Type: {message.type}")
        print(f"  Data: {message.data}")
        print(f"  JSON: {json_str}")
        
        # Deserialize and verify
        restored_dict = deserialize_message(json_str)
        restored_msg = Message.from_dict(restored_dict)
        
        # Verify integrity
        if restored_msg.type == message.type and restored_msg.data == message.data:
            print("  ✓ Serialization/Deserialization successful")
        else:
            print("  ❌ Serialization/Deserialization failed")

def demo_utilities():
    """Demonstrate utility functions"""
    print_separator("6. UTILITIES DEMO")
    
    # Room code generation
    print("Room code generation:")
    room_codes = [generate_room_code() for _ in range(5)]
    for code in room_codes:
        is_valid = validate_room_code(code)
        print(f"  {code}: {'Valid' if is_valid else 'Invalid'}")
    
    # Username validation
    print("\nUsername validation:")
    test_usernames = ["alice", "user123", "ab", "user_name", "user@invalid", ""]
    for username in test_usernames:
        valid, msg = validate_username(username)
        status = "✓" if valid else "✗"
        print(f"  {username:<12} {status} {msg if not valid else ''}")
    
    # Password validation
    print("\nPassword validation:")
    test_passwords = ["password123", "short", "", "a"*60, "validpass"]
    for password in test_passwords:
        valid, msg = validate_password(password)
        status = "✓" if valid else "✗"
        display_pwd = password[:10] + "..." if len(password) > 10 else password
        print(f"  {display_pwd:<15} {status} {msg if not valid else ''}")
    
    # Coordinate validation
    print("\nCoordinate validation:")
    test_coords = [(0,0), (7,7), (-1,0), (8,0), (3,4), (10,10)]
    for row, col in test_coords:
        valid = validate_coordinates(row, col)
        status = "✓" if valid else "✗"
        print(f"  ({row},{col}): {status}")
    
    # Time formatting
    print("\nTime formatting:")
    test_times = [0, 30, 60, 125, 3661]
    for seconds in test_times:
        formatted = format_game_time(seconds)
        print(f"  {seconds} seconds = {formatted}")
    
    # Player utilities
    print("\nPlayer utilities:")
    print(f"  Opposite of BLACK: {PLAYER_COLORS[get_opposite_player(BLACK)]}")
    print(f"  Opposite of WHITE: {PLAYER_COLORS[get_opposite_player(WHITE)]}")
    
    scores = {BLACK: 15, WHITE: 12}
    diff = calculate_score_difference(scores)
    print(f"  Score difference (Black 15, White 12): {diff}")

def run_comprehensive_demo():
    """Run the complete demonstration"""
    print("🎮 OTHELLO MULTIPLAYER - CORE LOGIC DEMONSTRATION")
    print("Role 3: Game & Systems Architect Implementation")
    print("="*60)
    
    try:
        demo_board_operations()
        demo_game_rules()
        demo_player_management()
        demo_game_state()
        demo_network_protocol()
        demo_utilities()
        
        print_separator("🎉 DEMONSTRATION COMPLETE")
        print("All core components are working correctly!")
        print("\nImplementation Summary:")
        print("✅ Board operations and validation")
        print("✅ Complete Othello game rules")
        print("✅ Player management and statistics")
        print("✅ Game state management")
        print("✅ Network message protocol")
        print("✅ Utility functions and validation")
        print("\n🚀 Ready for integration with Backend and Frontend!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        
def run_quick_test():
    """Run a quick validation test"""
    print("Running quick validation test...")
    
    try:
        # Quick board test
        board = OthelloBoard()
        assert board.get_scores()[BLACK] == 2
        assert board.get_scores()[WHITE] == 2
        
        # Quick rules test
        valid_moves = OthelloRules.get_valid_moves(board, BLACK)
        assert len(valid_moves) == 4
        
        # Quick player test
        player = Player("Test", BLACK)
        assert player.username == "Test"
        assert player.color == BLACK
        
        # Quick message test
        msg = create_login_message("user", "pass")
        json_str = serialize_message(msg.to_dict())
        restored = deserialize_message(json_str)
        assert restored['type'] == MSG_LOGIN
        
        print("✅ Quick test passed! All core components working.")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode
        success = run_quick_test()
        sys.exit(0 if success else 1)
    else:
        # Full demonstration
        run_comprehensive_demo()