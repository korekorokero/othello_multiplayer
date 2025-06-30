import pygame
import requests
import json
import sys
import time
import threading
from typing import Optional, Dict, List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
BOARD_SIZE = 480
CELL_SIZE = BOARD_SIZE // 8
BOARD_OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = 150

# Colors
BLACK = (34, 34, 34)
WHITE = (236, 240, 241)
GREEN = (46, 204, 113)
DARK_GREEN = (39, 174, 96)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
ORANGE = (243, 156, 18)
GRAY = (149, 165, 166)
LIGHT_GRAY = (189, 195, 199)

class OthelloPygameClient:
    def __init__(self, server_host='localhost', server_port=8889):
        self.server_url = f"http://{server_host}:{server_port}"
        self.session_id = None
        self.game_id = None
        self.player_name = ""
        self.game_state = None
        self.available_games = []
        
        # Game states
        self.state = "LOGIN"  # LOGIN, LOBBY, GAME
        self.last_update = 0
        self.update_interval = 2.0  # Update every 2 seconds
        
        # Pygame setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Othello Pygame Client")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Input handling
        self.input_text = ""
        self.input_active = True
        
        # Message system
        self.message = ""
        self.message_color = RED
        self.message_time = 0
        
        # Running flag
        self.running = True
        
    def check_server(self) -> bool:
        """Check if server is accessible"""
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def show_message(self, text: str, color=RED, duration=3.0):
        """Show a temporary message"""
        self.message = text
        self.message_color = color
        self.message_time = time.time() + duration
    
    def register_player(self, name: str) -> bool:
        """Register player with server"""
        try:
            print(f"[DEBUG] Registering player: {name}")
            response = requests.get(f"{self.server_url}/api/register/{name}", timeout=10)
            print(f"[DEBUG] Register response status: {response.status_code}")
            print(f"[DEBUG] Register response text: {response.text}")
            
            data = response.json()
            
            if data.get('success'):
                self.session_id = data['session_id']
                self.player_name = name
                self.state = "LOBBY"
                self.show_message(f"Welcome, {name}!", GREEN)
                print(f"[DEBUG] Successfully registered with session_id: {self.session_id}")
                return True
            else:
                error_msg = data.get('message', 'Registration failed')
                self.show_message(error_msg)
                print(f"[DEBUG] Registration failed: {error_msg}")
                return False
        except Exception as e:
            error_msg = f"Connection error: {e}"
            self.show_message(error_msg)
            print(f"[DEBUG] Exception during registration: {e}")
            return False
    
    def create_game(self) -> bool:
        """Create a new game"""
        try:
            data = {'session_id': self.session_id}
            print(f"[DEBUG] Creating game with data: {data}")
            
            response = requests.post(f"{self.server_url}/api/creategame", 
                                   json=data, headers={'Content-Type': 'application/json'})
            
            print(f"[DEBUG] Create game response status: {response.status_code}")
            print(f"[DEBUG] Create game response text: {response.text}")
            
            result = response.json()
            
            if result.get('success'):
                self.game_id = result['game_id']
                self.state = "GAME"
                self.show_message("Game created! Waiting for opponent...", GREEN)
                print(f"[DEBUG] Successfully created game: {self.game_id}")
                return True
            else:
                error_msg = result.get('message', 'Failed to create game')
                self.show_message(error_msg)
                print(f"[DEBUG] Failed to create game: {error_msg}")
                return False
        except Exception as e:
            error_msg = f"Error creating game: {e}"
            self.show_message(error_msg)
            print(f"[DEBUG] Exception creating game: {e}")
            return False
    
    def join_game(self, game_id: str) -> bool:
        """Join an existing game"""
        try:
            data = {'session_id': self.session_id, 'game_id': game_id}
            print(f"[DEBUG] Sending join request: {data}")
            
            response = requests.post(f"{self.server_url}/api/joingame", 
                                   json=data, headers={'Content-Type': 'application/json'})
            
            print(f"[DEBUG] Join response status: {response.status_code}")
            print(f"[DEBUG] Join response text: {response.text}")
            
            result = response.json()
            
            if result.get('success'):
                self.game_id = game_id
                self.state = "GAME"
                self.show_message("Joined game successfully!", GREEN)
                print(f"[DEBUG] Successfully joined game: {game_id}")
                return True
            else:
                error_msg = result.get('message', 'Failed to join game')
                self.show_message(error_msg)
                print(f"[DEBUG] Failed to join game: {error_msg}")
                return False
        except Exception as e:
            error_msg = f"Error joining game: {e}"
            self.show_message(error_msg)
            print(f"[DEBUG] Exception joining game: {e}")
            return False
    
    def make_move(self, row: int, col: int) -> bool:
        """Make a move in the game"""
        try:
            data = {
                'session_id': self.session_id,
                'game_id': self.game_id,
                'row': row,
                'col': col
            }
            response = requests.post(f"{self.server_url}/api/makemove", 
                                   json=data, headers={'Content-Type': 'application/json'})
            result = response.json()
            
            if result.get('success'):
                self.show_message("Move successful!", GREEN, 1.0)
                return True
            else:
                self.show_message(result.get('message', 'Invalid move'))
                return False
        except Exception as e:
            self.show_message(f"Error making move: {e}")
            return False
    
    def leave_game(self) -> bool:
        """Leave current game"""
        try:
            data = {'session_id': self.session_id}
            response = requests.post(f"{self.server_url}/api/leavegame", 
                                   json=data, headers={'Content-Type': 'application/json'})
            
            self.game_id = None
            self.game_state = None
            self.state = "LOBBY"
            self.show_message("Left game", GREEN)
            return True
        except Exception as e:
            self.show_message(f"Error leaving game: {e}")
            return False
    
    def update_lobby(self):
        """Update available games list"""
        try:
            print(f"[DEBUG] Updating lobby...")
            response = requests.get(f"{self.server_url}/api/lobby", timeout=5)
            print(f"[DEBUG] Lobby response status: {response.status_code}")
            
            data = response.json()
            print(f"[DEBUG] Lobby data: {data}")
            
            if data.get('success'):
                self.available_games = data['games']
                print(f"[DEBUG] Found {len(self.available_games)} available games")
            else:
                print(f"[DEBUG] Lobby update failed: {data.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"[DEBUG] Exception updating lobby: {e}")
            # Don't show error message for polling failures
    
    def update_game_state(self):
        """Update current game state"""
        if not self.session_id:
            return
            
        try:
            response = requests.get(f"{self.server_url}/api/gamestate/{self.session_id}")
            data = response.json()
            
            if data.get('success'):
                self.game_state = data['game_state']
        except Exception as e:
            pass  # Silent fail for polling
    
    def handle_board_click(self, pos: Tuple[int, int]):
        """Handle clicks on the game board"""
        if self.state != "GAME" or not self.game_state:
            return
        
        if not self.game_state.get('my_turn', False):
            self.show_message("It's not your turn!")
            return
        
        x, y = pos
        
        # Check if click is within board bounds
        if (BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + BOARD_SIZE and
            BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + BOARD_SIZE):
            
            # Calculate board position
            col = (x - BOARD_OFFSET_X) // CELL_SIZE
            row = (y - BOARD_OFFSET_Y) // CELL_SIZE
            
            # Convert to 1-based indexing for server
            self.make_move(row + 1, col + 1)
    
    def handle_lobby_click(self, pos: Tuple[int, int]):
        """Handle clicks in lobby"""
        x, y = pos
        
        # Create game button
        if 50 <= x <= 200 and 200 <= y <= 240:
            self.create_game()
        
        # Refresh button
        if 220 <= x <= 320 and 200 <= y <= 240:
            self.update_lobby()
            self.show_message("Lobby refreshed", GREEN, 1.0)
        
        # Join game buttons
        start_y = 300
        for i, game in enumerate(self.available_games):
            button_y = start_y + i * 50
            if 300 <= x <= 400 and button_y <= y <= button_y + 40:
                print(f"[DEBUG] Attempting to join game: {game['id']} by {game['creator']}")
                self.join_game(game['id'])
                break
    
    def draw_login_screen(self):
        """Draw login screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render("🔴⚫ Othello Client ⚫🔴", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instruction = self.font.render("Enter your name:", True, WHITE)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH//2, 200))
        self.screen.blit(instruction, instruction_rect)
        
        # Input box
        input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, 250, 300, 40)
        pygame.draw.rect(self.screen, WHITE, input_box, 2)
        pygame.draw.rect(self.screen, BLACK if self.input_active else GRAY, 
                        (input_box.x + 2, input_box.y + 2, input_box.width - 4, input_box.height - 4))
        
        # Input text
        text_surface = self.font.render(self.input_text, True, WHITE)
        self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        
        # Enter button
        enter_btn = pygame.Rect(WINDOW_WIDTH//2 - 75, 320, 150, 40)
        pygame.draw.rect(self.screen, BLUE, enter_btn)
        enter_text = self.font.render("Enter", True, WHITE)
        enter_text_rect = enter_text.get_rect(center=enter_btn.center)
        self.screen.blit(enter_text, enter_text_rect)
        
        # Server status
        server_ok = self.check_server()
        status_color = GREEN if server_ok else RED
        status_text = "Server: Connected" if server_ok else "Server: Disconnected"
        status_surface = self.small_font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (10, WINDOW_HEIGHT - 30))
    
    def draw_lobby_screen(self):
        """Draw lobby screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render(f"Welcome, {self.player_name}!", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Create game button
        create_btn = pygame.Rect(50, 200, 150, 40)
        pygame.draw.rect(self.screen, GREEN, create_btn)
        create_text = self.font.render("Create Game", True, WHITE)
        create_text_rect = create_text.get_rect(center=create_btn.center)
        self.screen.blit(create_text, create_text_rect)
        
        # Refresh button
        refresh_btn = pygame.Rect(220, 200, 100, 40)
        pygame.draw.rect(self.screen, BLUE, refresh_btn)
        refresh_text = self.font.render("Refresh", True, WHITE)
        refresh_text_rect = refresh_text.get_rect(center=refresh_btn.center)
        self.screen.blit(refresh_text, refresh_text_rect)
        
        # Available games
        games_title = self.font.render("Available Games:", True, WHITE)
        self.screen.blit(games_title, (50, 260))
        
        if not self.available_games:
            no_games = self.small_font.render("No games available. Create one!", True, GRAY)
            self.screen.blit(no_games, (50, 290))
        else:
            for i, game in enumerate(self.available_games):
                y_pos = 300 + i * 50
                
                # Game info
                game_text = f"Game by {game['creator']} ({game['players']}/2)"
                game_surface = self.small_font.render(game_text, True, WHITE)
                self.screen.blit(game_surface, (50, y_pos + 10))
                
                # Join button
                join_btn = pygame.Rect(300, y_pos, 100, 40)
                pygame.draw.rect(self.screen, BLUE, join_btn)
                join_text = self.small_font.render("Join", True, WHITE)
                join_text_rect = join_text.get_rect(center=join_btn.center)
                self.screen.blit(join_text, join_text_rect)
    
    def draw_game_screen(self):
        """Draw game screen"""
        self.screen.fill(BLACK)
        
        if not self.game_state:
            waiting = self.font.render("Loading game...", True, WHITE)
            waiting_rect = waiting.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(waiting, waiting_rect)
            return
        
        # Game info
        info_y = 20
        
        # Game status
        if self.game_state.get('game_over'):
            winner = self.game_state.get('winner')
            if winner == 0:
                status_text = "Game Over - Tie!"
            elif winner == self.game_state.get('my_color'):
                status_text = "Game Over - You Win!"
            else:
                status_text = "Game Over - You Lose!"
            status_color = ORANGE
        elif self.game_state.get('players_count', 0) < 2:
            status_text = "Waiting for opponent..."
            status_color = ORANGE
        elif self.game_state.get('my_turn'):
            status_text = "Your Turn"
            status_color = GREEN
        else:
            status_text = "Opponent's Turn"
            status_color = GRAY
        
        status_surface = self.font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (20, info_y))
        
        # Player info
        color_text = "Black" if self.game_state.get('my_color') == 1 else "White"
        player_surface = self.small_font.render(f"You: {color_text}", True, WHITE)
        self.screen.blit(player_surface, (20, info_y + 40))
        
        opponent = self.game_state.get('opponent_name', 'Waiting...')
        opponent_surface = self.small_font.render(f"Opponent: {opponent}", True, WHITE)
        self.screen.blit(opponent_surface, (20, info_y + 65))
        
        # Score
        score = self.game_state.get('score', [0, 0])
        score_surface = self.small_font.render(f"Black: {score[0]}  White: {score[1]}", True, WHITE)
        self.screen.blit(score_surface, (20, info_y + 90))
        
        # Leave button
        leave_btn = pygame.Rect(WINDOW_WIDTH - 120, 20, 100, 30)
        pygame.draw.rect(self.screen, RED, leave_btn)
        leave_text = self.small_font.render("Leave", True, WHITE)
        leave_text_rect = leave_text.get_rect(center=leave_btn.center)
        self.screen.blit(leave_text, leave_text_rect)
        
        # Draw board
        self.draw_board()
    
    def draw_board(self):
        """Draw the Othello board"""
        if not self.game_state:
            return
        
        board = self.game_state.get('board', [])
        valid_moves = self.game_state.get('valid_moves', [])
        
        # Board background
        board_rect = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(self.screen, GREEN, board_rect)
        
        # Draw cells and pieces
        for row in range(8):
            for col in range(8):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                
                # Cell border
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, DARK_GREEN, cell_rect, 2)
                
                # Check if valid move
                is_valid_move = [row + 1, col + 1] in valid_moves
                if is_valid_move and self.game_state.get('my_turn'):
                    pygame.draw.rect(self.screen, ORANGE, cell_rect)
                    pygame.draw.rect(self.screen, DARK_GREEN, cell_rect, 2)
                
                # Draw piece
                if row < len(board) and col < len(board[row]):
                    piece = board[row][col]
                    if piece in [1, 2]:  # 1 = black, 2 = white
                        center_x = x + CELL_SIZE // 2
                        center_y = y + CELL_SIZE // 2
                        radius = CELL_SIZE // 2 - 5
                        
                        color = BLACK if piece == 1 else WHITE
                        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
                        pygame.draw.circle(self.screen, DARK_GREEN, (center_x, center_y), radius, 2)
    
    def draw_message(self):
        """Draw temporary message"""
        if self.message and time.time() < self.message_time:
            message_surface = self.font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
            
            # Background for better readability
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, self.message_color, bg_rect, 2)
            
            self.screen.blit(message_surface, message_rect)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == "LOGIN":
                    if event.key == pygame.K_RETURN:
                        if self.input_text.strip():
                            self.register_player(self.input_text.strip())
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 20:  # Limit name length
                            self.input_text += event.unicode
                
                elif self.state == "GAME":
                    if event.key == pygame.K_ESCAPE:
                        self.leave_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == "LOGIN":
                        # Check enter button
                        enter_btn = pygame.Rect(WINDOW_WIDTH//2 - 75, 320, 150, 40)
                        if enter_btn.collidepoint(event.pos) and self.input_text.strip():
                            self.register_player(self.input_text.strip())
                    
                    elif self.state == "LOBBY":
                        self.handle_lobby_click(event.pos)
                    
                    elif self.state == "GAME":
                        # Check leave button
                        leave_btn = pygame.Rect(WINDOW_WIDTH - 120, 20, 100, 30)
                        if leave_btn.collidepoint(event.pos):
                            self.leave_game()
                        else:
                            self.handle_board_click(event.pos)
    
    def update(self):
        """Update game state"""
        current_time = time.time()
        
        if current_time - self.last_update > self.update_interval:
            if self.state == "LOBBY":
                self.update_lobby()
            elif self.state == "GAME":
                self.update_game_state()
            
            self.last_update = current_time
    
    def run(self):
        """Main game loop"""
        print("🔴⚫ OTHELLO PYGAME CLIENT ⚫🔴")
        print("=" * 50)
        print(f"🔍 Connecting to server: {self.server_url}")
        
        if not self.check_server():
            print(f"❌ Cannot connect to server at {self.server_url}")
            print("💡 Make sure the server is running: python server.py")
            return
        
        print("✅ Connected to server successfully!")
        print("🎮 Game window opened. Enter your name to start playing.")
        print("=" * 50)
        
        while self.running:
            self.handle_events()
            self.update()
            
            # Draw based on current state
            if self.state == "LOGIN":
                self.draw_login_screen()
            elif self.state == "LOBBY":
                self.draw_lobby_screen()
            elif self.state == "GAME":
                self.draw_game_screen()
            
            self.draw_message()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Othello Pygame Client')
    parser.add_argument('--host', '-H', default='localhost', 
                       help='Server hostname (default: localhost)')
    parser.add_argument('--port', '-p', type=int, default=8889, 
                       help='Server port (default: 8889)')
    
    args = parser.parse_args()
    
    try:
        client = OthelloPygameClient(args.host, args.port)
        client.run()
    except KeyboardInterrupt:
        print("\n🛑 Client interrupted by user")
    except Exception as e:
        print(f"❌ Client error: {e}")

if __name__ == "__main__":
    main()