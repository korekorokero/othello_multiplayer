#!/usr/bin/env python3
import sys
import os

# Test basic imports
print("🧪 Testing Othello Core Components...")

try:
    from shared.constants import BLACK, WHITE, EMPTY
    print("✓ Constants imported")
    
    from game.othello_board import OthelloBoard
    board = OthelloBoard()
    print(f"✓ Board created: {board.get_scores()}")
    
    from game.othello_rules import OthelloRules  
    moves = OthelloRules.get_valid_moves(board, BLACK)
    print(f"✓ Rules working: {len(moves)} valid moves")
    
    from game.player import Player
    player = Player("Test", BLACK)
    print(f"✓ Player created: {player}")
    
    from game.game_state import GameState
    game = GameState("test")
    print(f"✓ Game state created: {game.game_id}")
    
    print("\n🎉 ALL BASIC TESTS PASSED!")
    print("✅ Your implementation is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()