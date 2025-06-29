import socket
import selectors
import types
import pygame
import threading
import json
import sys
from board import Board

class GameClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.connected = False
        self.game_state = None
        self.player_num = 0
        self.player_name = ""
        self.opponent_name = ""
        self.my_turn = False
        self.valid_moves = []
        self.board = Board()
        self.game_over = False
        self.winner = 0
        self.message = ""
        self.waiting_for_name = True
        self.name_input = ""
        self.name_submitted = False
        
        # Initialize pygame
        pygame.init()
        self.WINDOW_SIZE = 400
        self.BOARD_SIZE = 8
        self.CELL_SIZE = self.WINDOW_SIZE // self.BOARD_SIZE
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE + 250, self.WINDOW_SIZE + 100))
        pygame.display.set_caption("Othello Multiplayer")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 128, 0)
        self.GRAY = (128, 128, 128)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
    def get_player_name(self):
        """Get player name through a simple input dialog"""
        name_screen = True
        input_text = ""
        cursor_visible = True
        cursor_timer = 0
        
        while name_screen:
            cursor_timer += 1
            if cursor_timer > 30:  # Blink cursor every 30 frames
                cursor_visible = not cursor_visible
                cursor_timer = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(input_text.strip()) > 0:
                        self.player_name = input_text.strip()
                        return self.player_name
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isprintable() and len(input_text) < 20:
                        input_text += event.unicode
            
            # Draw name input screen
            self.screen.fill(self.GREEN)
            
            # Title
            title_text = self.large_font.render("Welcome to Othello!", True, self.WHITE)
            title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 150))
            self.screen.blit(title_text, title_rect)
            
            # Instructions
            inst_text = self.font.render("Enter your name:", True, self.WHITE)
            inst_rect = inst_text.get_rect(center=(self.screen.get_width()//2, 250))
            self.screen.blit(inst_text, inst_rect)
            
            # Input box
            input_box = pygame.Rect(self.screen.get_width()//2 - 150, 300, 300, 40)
            pygame.draw.rect(self.screen, self.WHITE, input_box)
            pygame.draw.rect(self.screen, self.BLACK, input_box, 2)
            
            # Input text
            text_surface = self.font.render(input_text, True, self.BLACK)
            self.screen.blit(text_surface, (input_box.x + 5, input_box.y + 8))
            
            # Cursor
            if cursor_visible and len(input_text) < 20:
                cursor_x = input_box.x + 5 + text_surface.get_width()
                pygame.draw.line(self.screen, self.BLACK, 
                               (cursor_x, input_box.y + 5), 
                               (cursor_x, input_box.y + 35), 2)
            
            # Submit instruction
            submit_text = self.small_font.render("Press Enter to continue", True, self.WHITE)
            submit_rect = submit_text.get_rect(center=(self.screen.get_width()//2, 380))
            self.screen.blit(submit_text, submit_rect)
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
        
        return None
        
    def start_connection(self):
        print(f'Connecting to server {self.host}:{self.port}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        
        try:
            sock.connect_ex((self.host, self.port))
        except Exception as e:
            print(f'Error connecting to server: {e}')
            return False
        
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            outb=b'',
            should_close=False
        )
        
        self.sel.register(sock, events, data=data)
        self.connected = True
        
        # Send player name to server
        if self.player_name:
            self.send_name(self.player_name)
        
        return True
        
    def send_name(self, name):
        """Send player name to server"""
        if not self.connected:
            return
            
        for key in self.sel.get_map().values():
            if hasattr(key, 'data'):
                message = f"NAME:{name}\n"
                key.data.outb += message.encode('utf-8')
                break
        
    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(2048)
            if recv_data:
                message = recv_data.decode('utf-8')
                self.parse_server_message(message)
            else:
                print('Server closed connection')
                data.should_close = True
        
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                try:
                    sent = sock.send(data.outb)
                    data.outb = data.outb[sent:]
                except BrokenPipeError:
                    print('Connection to server lost')
                    data.should_close = True
        
        if data.should_close:
            print('Closing connection')
            self.sel.unregister(sock)
            sock.close()
            self.connected = False

    def parse_server_message(self, message):
        """Parse server message and update game state"""
        self.message = message
        print(f"DEBUG: Received message: {message[:200]}...")  # Debug print
        
        # Parse player assignment
        if "You are Player" in message:
            if "Player 1" in message:
                self.player_num = 1
            else:
                self.player_num = 2
        
        # Parse opponent name
        if "Opponent:" in message:
            try:
                opponent_line = [line for line in message.split('\n') if 'Opponent:' in line][0]
                self.opponent_name = opponent_line.split('Opponent: ')[1].strip()
            except:
                pass
        
        # Parse turn information - IMPROVED
        if f"{self.player_name}, your turn!" in message or "Your turn!" in message:
            self.my_turn = True
            print(f"DEBUG: It's my turn! Player {self.player_num}")
        else:
            # Check if it's specifically NOT our turn
            if "Waiting for" in message and self.player_name not in message.split("Waiting for")[1].split("to move")[0]:
                self.my_turn = False
            elif f"Player {3-self.player_num}" in message and "to move" in message:
                self.my_turn = False
            elif self.opponent_name and f"{self.opponent_name}" in message and "to move" in message:
                self.my_turn = False
            
        # Parse valid moves - IMPROVED
        if "Valid moves:" in message:
            try:
                moves_line = [line for line in message.split('\n') if 'Valid moves:' in line][0]
                moves_str = moves_line.split('Valid moves: ')[1].strip()
                print(f"DEBUG: Parsing valid moves: {moves_str}")
                
                # Handle different formats
                if moves_str.startswith('[') and moves_str.endswith(']'):
                    self.valid_moves = eval(moves_str)
                else:
                    # Try to parse manually if eval fails
                    import re
                    tuples = re.findall(r'\((\d+),\s*(\d+)\)', moves_str)
                    self.valid_moves = [(int(row), int(col)) for row, col in tuples]
                
                print(f"DEBUG: Valid moves parsed: {self.valid_moves}")
            except Exception as e:
                print(f"DEBUG: Error parsing valid moves: {e}")
                self.valid_moves = []
        
        # Parse current player
        if "Current player:" in message:
            try:
                player_line = [line for line in message.split('\n') if 'Current player:' in line][0]
                if "Player 1" in player_line or "Black" in player_line:
                    self.board._current_player = 1
                else:
                    self.board._current_player = 2
            except:
                pass
        
        # Parse board state from ASCII representation
        self.parse_board_from_ascii(message)
        
        # Parse game over
        if "GAME OVER" in message:
            self.game_over = True
            if "YOU WIN" in message:
                self.winner = self.player_num
            elif "YOU LOSE" in message:
                self.winner = 3 - self.player_num
            else:
                self.winner = 0

    def parse_board_from_ascii(self, message):
        """Parse board state from ASCII board representation"""
        lines = message.split('\n')
        
        # Find the board section (look for lines with │)
        board_lines = []
        for line in lines:
            if '│' in line and any(c in line for c in ['●', '○', ' ']):
                board_lines.append(line)
        
        # Parse each board line
        if len(board_lines) >= 8:  # We should have 8 rows
            for i, line in enumerate(board_lines[:8]):
                # Extract pieces from the line
                # Format: "1│ ● │   │ ○ │..."
                cells = line.split('│')[1:-1]  # Remove row numbers
                for j, cell in enumerate(cells[:8]):  # Take first 8 cells
                    cell = cell.strip()
                    if '●' in cell:
                        self.board._grid[i][j] = 1  # Black
                    elif '○' in cell:
                        self.board._grid[i][j] = 2  # White
                    else:
                        self.board._grid[i][j] = 0  # Empty

    def send_move(self, row, col):
        """Send move to server"""
        if not self.connected:
            return
            
        for key in self.sel.get_map().values():
            if hasattr(key, 'data'):
                message = f"{row},{col}\n"
                key.data.outb += message.encode('utf-8')
                break

    def draw_board(self):
        """Draw the game board"""
        # Fill background
        self.screen.fill(self.GREEN)
        
        # Draw grid lines
        for i in range(self.BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(self.screen, self.BLACK, 
                           (i * self.CELL_SIZE, 0), 
                           (i * self.CELL_SIZE, self.WINDOW_SIZE), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, self.BLACK, 
                           (0, i * self.CELL_SIZE), 
                           (self.WINDOW_SIZE, i * self.CELL_SIZE), 2)
        
        # Draw pieces
        grid = self.board.get_grid()
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                center_x = col * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = row * self.CELL_SIZE + self.CELL_SIZE // 2
                radius = self.CELL_SIZE // 3
                
                if grid[row][col] == 1:  # Black piece
                    pygame.draw.circle(self.screen, self.BLACK, 
                                     (center_x, center_y), radius)
                elif grid[row][col] == 2:  # White piece
                    pygame.draw.circle(self.screen, self.WHITE, 
                                     (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, self.BLACK, 
                                     (center_x, center_y), radius, 2)
        
        # Highlight valid moves - IMPROVED DEBUG
        print(f"DEBUG: my_turn={self.my_turn}, valid_moves={self.valid_moves}")
        if self.my_turn and self.valid_moves:
            print(f"DEBUG: Drawing {len(self.valid_moves)} valid moves")
            for move_row, move_col in self.valid_moves:
                center_x = (move_col - 1) * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = (move_row - 1) * self.CELL_SIZE + self.CELL_SIZE // 2
                print(f"DEBUG: Drawing yellow dot at ({center_x}, {center_y}) for move ({move_row}, {move_col})")
                
                # Draw larger, more visible indicator
                pygame.draw.circle(self.screen, self.YELLOW, 
                                 (center_x, center_y), 12)
                pygame.draw.circle(self.screen, self.RED, 
                                 (center_x, center_y), 12, 3)
        elif self.my_turn:
            print("DEBUG: It's my turn but no valid moves")
        elif self.valid_moves:
            print("DEBUG: Valid moves exist but not my turn")
        else:
            print("DEBUG: Not my turn and no valid moves")

    def draw_info(self):
        """Draw game information"""
        info_x = self.WINDOW_SIZE + 10
        y_offset = 20
        
        # Player names and colors - FIXED
        if self.player_num == 1:
            player_text = f"You: {self.player_name} (Black)"
            player_color = self.BLACK
        else:
            player_text = f"You: {self.player_name} (White)" 
            player_color = self.WHITE  # FIXED: Changed from GRAY to WHITE
            
        text = self.font.render(player_text, True, player_color)
        # Add background for white text visibility
        if self.player_num == 2:
            text_rect = text.get_rect()
            text_rect.topleft = (info_x, y_offset)
            pygame.draw.rect(self.screen, self.BLACK, text_rect.inflate(4, 2))
            
        self.screen.blit(text, (info_x, y_offset))
        y_offset += 35
        
        # Opponent info
        if self.opponent_name:
            opponent_player_num = 3 - self.player_num
            if opponent_player_num == 1:
                opponent_text = f"Opponent: {self.opponent_name} (Black)"
                opponent_color = self.BLACK
            else:
                opponent_text = f"Opponent: {self.opponent_name} (White)"
                opponent_color = self.WHITE
                
            text = self.small_font.render(opponent_text, True, opponent_color)
            # Add background for white text visibility
            if opponent_player_num == 2:
                text_rect = text.get_rect()
                text_rect.topleft = (info_x, y_offset)
                pygame.draw.rect(self.screen, self.BLACK, text_rect.inflate(4, 2))
                
            self.screen.blit(text, (info_x, y_offset))
            y_offset += 35
        
        # Current turn
        current_player = self.board.get_current_player()
        if self.my_turn and not self.game_over:
            turn_text = "Your Turn!"
            turn_color = self.BLUE
        elif not self.game_over:
            opponent_name = self.opponent_name if self.opponent_name else f"Player {3-self.player_num}"
            turn_text = f"{opponent_name}'s Turn"
            turn_color = self.RED
        else:
            turn_text = "Game Over"
            turn_color = self.RED
            
        text = self.small_font.render(turn_text, True, turn_color)
        self.screen.blit(text, (info_x, y_offset))
        y_offset += 30
        
        # Score
        black_score, white_score = self.board.get_score()
        score_text = f"Black: {black_score}"
        text = self.small_font.render(score_text, True, self.BLACK)
        self.screen.blit(text, (info_x, y_offset))
        y_offset += 25
        
        score_text = f"White: {white_score}"
        text = self.small_font.render(score_text, True, self.WHITE)
        # Add background for white text visibility
        text_rect = text.get_rect()
        text_rect.topleft = (info_x, y_offset)
        pygame.draw.rect(self.screen, self.BLACK, text_rect.inflate(4, 2))
        self.screen.blit(text, (info_x, y_offset))
        y_offset += 35
        
        # Game over message
        if self.game_over:
            if self.winner == self.player_num:
                result_text = "YOU WIN!"
                result_color = self.BLUE
            elif self.winner == 0:
                result_text = "TIE GAME!"
                result_color = self.YELLOW
            else:
                result_text = "YOU LOSE!"
                result_color = self.RED
                
            text = self.font.render(result_text, True, result_color)
            self.screen.blit(text, (info_x, y_offset))
        
        # Valid moves count
        elif self.valid_moves:
            moves_text = f"Valid moves: {len(self.valid_moves)}"
            text = self.small_font.render(moves_text, True, self.BLACK)
            self.screen.blit(text, (info_x, y_offset + 50))

    def handle_click(self, pos):
        """Handle mouse click on board"""
        print(f"DEBUG: Click at {pos}, my_turn={self.my_turn}, game_over={self.game_over}")
        
        if not self.my_turn or self.game_over:
            print(f"DEBUG: Click ignored - not my turn or game over")
            return
            
        x, y = pos
        if x >= self.WINDOW_SIZE or y >= self.WINDOW_SIZE:
            print(f"DEBUG: Click outside board area")
            return
            
        col = x // self.CELL_SIZE + 1  # Convert to 1-based
        row = y // self.CELL_SIZE + 1  # Convert to 1-based
        
        print(f"DEBUG: Clicked on board position ({row}, {col})")
        print(f"DEBUG: Valid moves: {self.valid_moves}")
        
        # Check if it's a valid move
        if (row, col) in self.valid_moves:
            print(f"DEBUG: Valid move clicked! Sending ({row}, {col})")
            self.send_move(row, col)
            self.my_turn = False  # Prevent multiple clicks
        else:
            print(f"DEBUG: Invalid move clicked - ({row}, {col}) not in {self.valid_moves}")

    def update_board_from_message(self):
        """Update local board state from server message - now handled in parse_server_message"""
        # Board parsing is now done in parse_server_message method
        pass

    def run(self):
        # Get player name first
        if self.get_player_name() is None:
            return
            
        if not self.start_connection():
            return
        
        # Start network thread
        network_thread = threading.Thread(target=self.network_loop)
        network_thread.daemon = True
        network_thread.start()
        
        # Main pygame loop
        clock = pygame.time.Clock()
        running = True
        
        while running and self.connected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Update board state from server messages
            self.update_board_from_message()
            
            # Draw everything
            self.draw_board()
            self.draw_info()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        self.sel.close()

    def network_loop(self):
        """Network handling loop"""
        while self.connected:
            try:
                events = self.sel.select(timeout=0.1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask)
                        
                # Check if we still have connections
                if not self.sel.get_map():
                    break
                    
            except Exception as e:
                print(f"Network error: {e}")
                break

if __name__ == '__main__':
    client = GameClient()
    print("=== Othello Pygame Multiplayer Client ===")
    print("Instructions:")
    print("- Enter your name when prompted")
    print("- Click on valid moves (yellow dots)")
    print("- Wait for your turn")
    print("- Close window to quit")
    print("=" * 40)
    
    client.run()