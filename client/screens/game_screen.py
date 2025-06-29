import pygame
import sys
from functools import reduce
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from client.network import NetworkClient
from client.constants import *

class Board:
    def __init__(self, size=8):
        self._current_player = 1  # 1 = black, 2 = white
        if size % 2 != 0:
            size = size + 1
        
        # Initialize empty board
        self._grid = [[0 for _ in range(size)] for _ in range(size)]
        
        # Place initial pieces
        half = size // 2
        self._grid[half-1][half-1] = 2    # white
        self._grid[half][half] = 2        # white
        self._grid[half-1][half] = 1      # black
        self._grid[half][half-1] = 1      # black
        
        self._size = size

    def get_display(self):
        """Return string representation of the board"""
        # Column headers - perfectly aligned
        output = "\n   " + " ".join(f"{n+1:^3}" for n in range(self._size)) + "\n"
        
        # Top border
        output += "  ┌" + "───┬" * (self._size-1) + "───┐\n"
        
        # Rows with content
        for i, row in enumerate(self._grid):
            # Row number and content
            output += f"{i+1:2}│"
            for cell in row:
                if cell == 0:
                    output += "   │"
                elif cell == 1:
                    output += " ● │"  # black
                else:
                    output += " ○ │"  # white
            output += f"{i+1:2}\n"
            
            # Row separator (except last row)
            if i < self._size - 1:
                output += "  ├" + "───┼" * (self._size-1) + "───┤\n"
        
        # Bottom border
        output += "  └" + "───┴" * (self._size-1) + "───┘\n"
        
        # Column footers - perfectly aligned
        output += "   " + " ".join(f"{n+1:^3}" for n in range(self._size)) + "\n\n"
        
        # Game info
        player_symbol = "●" if self._current_player == 1 else "○"
        player_name = "Black" if self._current_player == 1 else "White"
        output += f"Current player: {player_name} ({player_symbol})\n"
        
        # Score
        black_count = sum(row.count(1) for row in self._grid)
        white_count = sum(row.count(2) for row in self._grid)
        output += f"Score - Black: {black_count}, White: {white_count}\n"
        
        return output

    def is_valid_move(self, row, col):
        """Check if move is valid"""
        if not self._is_on_board(row, col) or self._grid[row-1][col-1] != 0:
            return False
        
        return len(self._get_flippable_directions(row, col)) > 0

    def make_move(self, row, col):
        """Make a move if valid"""
        if not self.is_valid_move(row, col):
            return False
        
        # Place the piece
        self._grid[row-1][col-1] = self._current_player
        
        # Flip pieces in all valid directions
        directions = self._get_flippable_directions(row, col)
        for dr, dc in directions:
            self._flip_pieces(row, col, dr, dc)
        
        # Switch players
        self._current_player = 3 - self._current_player  # 1->2, 2->1
        return True

    def get_valid_moves(self):
        """Get list of all valid moves for current player"""
        moves = []
        for row in range(1, self._size + 1):
            for col in range(1, self._size + 1):
                if self.is_valid_move(row, col):
                    moves.append((row, col))
        return moves

    def is_game_over(self):
        """Check if game is over"""
        # Game over if no valid moves for both players
        current_has_moves = len(self.get_valid_moves()) > 0
        
        if not current_has_moves:
            # Switch player temporarily to check if other player has moves
            original_player = self._current_player
            self._current_player = 3 - self._current_player
            other_has_moves = len(self.get_valid_moves()) > 0
            self._current_player = original_player
            
            if not other_has_moves:
                return True
            else:
                # Current player has no moves, skip turn
                self._current_player = 3 - self._current_player
                return False
        
        return False

    def get_winner(self):
        """Get winner (1=black, 2=white, 0=tie)"""
        black_count = sum(row.count(1) for row in self._grid)
        white_count = sum(row.count(2) for row in self._grid)
        
        if black_count > white_count:
            return 1
        elif white_count > black_count:
            return 2
        else:
            return 0

    def get_current_player(self):
        """Get current player (1=black, 2=white)"""
        return self._current_player

    def get_score(self):
        """Get current score as (black_count, white_count)"""
        black_count = sum(row.count(1) for row in self._grid)
        white_count = sum(row.count(2) for row in self._grid)
        return black_count, white_count

    def get_grid(self):
        """Get the current grid state"""
        return self._grid

    def get_size(self):
        """Get board size"""
        return self._size

    def _is_on_board(self, row, col):
        """Check if position is on board"""
        return 1 <= row <= self._size and 1 <= col <= self._size

    def _get_flippable_directions(self, row, col):
        """Get all directions where pieces can be flipped"""
        directions = []
        
        # Check all 8 directions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                if self._can_flip_in_direction(row, col, dr, dc):
                    directions.append((dr, dc))
        
        return directions

    def _can_flip_in_direction(self, row, col, dr, dc):
        """Check if pieces can be flipped in given direction"""
        r, c = row + dr, col + dc
        found_opponent = False
        
        while self._is_on_board(r, c):
            cell_value = self._grid[r-1][c-1]
            
            if cell_value == 0:  # Empty cell
                return False
            elif cell_value == self._current_player:  # Own piece
                return found_opponent
            else:  # Opponent piece
                found_opponent = True
                r, c = r + dr, c + dc
        
        return False

    def _flip_pieces(self, row, col, dr, dc):
        """Flip pieces in given direction"""
        r, c = row + dr, col + dc
        
        while self._is_on_board(r, c):
            cell_value = self._grid[r-1][c-1]
            
            if cell_value == self._current_player:
                break
            else:
                self._grid[r-1][c-1] = self._current_player
                r, c = r + dr, c + dc


class ReversiGame:
    def __init__(self, board_size=8):
        pygame.init()
        
        # Game settings
        self.board_size = board_size
        self.cell_size = 60
        self.board_margin = 50
        self.sidebar_width = 250
        
        # Calculate window dimensions
        self.board_width = self.cell_size * self.board_size
        self.board_height = self.cell_size * self.board_size
        self.window_width = self.board_width + self.board_margin * 2 + self.sidebar_width
        self.window_height = self.board_height + self.board_margin * 2
        
        # Colors
        self.COLORS = {
            'background': (34, 139, 34),  # Forest green
            'board': (0, 100, 0),         # Dark green
            'grid_line': (0, 50, 0),      # Very dark green
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'valid_move': (255, 255, 0),  # Yellow
            'text': (255, 255, 255),
            'sidebar': (60, 60, 60),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150)
        }
        
        # Initialize pygame
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Reversi/Othello")
        self.clock = pygame.time.Clock()
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.board = Board(board_size)
        self.show_valid_moves = True
        self.game_over = False
        
        # Buttons
        self.restart_button = pygame.Rect(self.window_width - 180, 50, 150, 40)
        self.toggle_hints_button = pygame.Rect(self.window_width - 180, 100, 150, 40)

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def handle_click(self, pos):
        """Handle mouse clicks"""
        x, y = pos
        
        # Check if click is on restart button
        if self.restart_button.collidepoint(pos):
            self.restart_game()
            return
        
        # Check if click is on toggle hints button
        if self.toggle_hints_button.collidepoint(pos):
            self.show_valid_moves = not self.show_valid_moves
            return
        
        # Check if click is on the board
        if (self.board_margin <= x <= self.board_margin + self.board_width and
            self.board_margin <= y <= self.board_margin + self.board_height):
            
            # Convert pixel coordinates to board coordinates
            col = (x - self.board_margin) // self.cell_size + 1
            row = (y - self.board_margin) // self.cell_size + 1
            
            # Make move if valid
            if not self.game_over and self.board.is_valid_move(row, col):
                self.board.make_move(row, col)
                
                # Check if game is over
                if self.board.is_game_over():
                    self.game_over = True

    def restart_game(self):
        """Restart the game"""
        self.board = Board(self.board_size)
        self.game_over = False

    def draw(self):
        """Draw the game"""
        # Clear screen
        self.screen.fill(self.COLORS['background'])
        
        # Draw board
        self.draw_board()
        
        # Draw pieces
        self.draw_pieces()
        
        # Draw valid moves if enabled
        if self.show_valid_moves and not self.game_over:
            self.draw_valid_moves()
        
        # Draw sidebar
        self.draw_sidebar()
        
        # Draw buttons
        self.draw_buttons()

    def draw_board(self):
        """Draw the game board"""
        board_rect = pygame.Rect(
            self.board_margin, 
            self.board_margin, 
            self.board_width, 
            self.board_height
        )
        pygame.draw.rect(self.screen, self.COLORS['board'], board_rect)
        
        # Draw grid lines
        for i in range(self.board_size + 1):
            # Vertical lines
            x = self.board_margin + i * self.cell_size
            pygame.draw.line(
                self.screen, 
                self.COLORS['grid_line'], 
                (x, self.board_margin), 
                (x, self.board_margin + self.board_height), 
                2
            )
            
            # Horizontal lines
            y = self.board_margin + i * self.cell_size
            pygame.draw.line(
                self.screen, 
                self.COLORS['grid_line'], 
                (self.board_margin, y), 
                (self.board_margin + self.board_width, y), 
                2
            )

    def draw_pieces(self):
        """Draw game pieces"""
        grid = self.board.get_grid()
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if grid[row][col] != 0:
                    # Calculate center of cell
                    center_x = self.board_margin + col * self.cell_size + self.cell_size // 2
                    center_y = self.board_margin + row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 3
                    
                    # Choose color
                    color = self.COLORS['black'] if grid[row][col] == 1 else self.COLORS['white']
                    
                    # Draw piece
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
                    
                    # Draw border for white pieces
                    if grid[row][col] == 2:
                        pygame.draw.circle(self.screen, self.COLORS['black'], (center_x, center_y), radius, 2)

    def draw_valid_moves(self):
        """Draw valid move indicators"""
        valid_moves = self.board.get_valid_moves()
        
        for row, col in valid_moves:
            # Convert to 0-based indexing for drawing
            row_idx = row - 1
            col_idx = col - 1
            
            center_x = self.board_margin + col_idx * self.cell_size + self.cell_size // 2
            center_y = self.board_margin + row_idx * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 6
            
            pygame.draw.circle(self.screen, self.COLORS['valid_move'], (center_x, center_y), radius)

    def draw_sidebar(self):
        """Draw game information sidebar"""
        sidebar_x = self.board_margin + self.board_width + 20
        
        # Current player
        current_player = self.board.get_current_player()
        player_name = "Black" if current_player == 1 else "White"
        player_color = self.COLORS['black'] if current_player == 1 else self.COLORS['white']
        
        if not self.game_over:
            text = self.font.render(f"Current Player:", True, self.COLORS['text'])
            self.screen.blit(text, (sidebar_x, 150))
            
            text = self.font.render(player_name, True, player_color)
            self.screen.blit(text, (sidebar_x, 180))
            
            # Draw player indicator circle
            pygame.draw.circle(self.screen, player_color, (sidebar_x + 120, 190), 15)
            if current_player == 2:  # White piece needs border
                pygame.draw.circle(self.screen, self.COLORS['black'], (sidebar_x + 120, 190), 15, 2)
        
        # Score
        black_score, white_score = self.board.get_score()
        
        text = self.font.render("Score:", True, self.COLORS['text'])
        self.screen.blit(text, (sidebar_x, 230))
        
        text = self.small_font.render(f"Black: {black_score}", True, self.COLORS['text'])
        self.screen.blit(text, (sidebar_x, 260))
        
        text = self.small_font.render(f"White: {white_score}", True, self.COLORS['text'])
        self.screen.blit(text, (sidebar_x, 280))
        
        # Game over message
        if self.game_over:
            winner = self.board.get_winner()
            if winner == 0:
                text = self.font.render("Tie Game!", True, self.COLORS['text'])
            else:
                winner_name = "Black" if winner == 1 else "White"
                text = self.font.render(f"{winner_name} Wins!", True, self.COLORS['text'])
            
            self.screen.blit(text, (sidebar_x, 320))
        
        # Valid moves count
        if not self.game_over:
            valid_moves_count = len(self.board.get_valid_moves())
            text = self.small_font.render(f"Valid moves: {valid_moves_count}", True, self.COLORS['text'])
            self.screen.blit(text, (sidebar_x, 350))

    def draw_buttons(self):
        """Draw UI buttons"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Restart button
        color = self.COLORS['button_hover'] if self.restart_button.collidepoint(mouse_pos) else self.COLORS['button']
        pygame.draw.rect(self.screen, color, self.restart_button)
        pygame.draw.rect(self.screen, self.COLORS['text'], self.restart_button, 2)
        
        text = self.small_font.render("Restart Game", True, self.COLORS['text'])
        text_rect = text.get_rect(center=self.restart_button.center)
        self.screen.blit(text, text_rect)
        
        # Toggle hints button
        color = self.COLORS['button_hover'] if self.toggle_hints_button.collidepoint(mouse_pos) else self.COLORS['button']
        pygame.draw.rect(self.screen, color, self.toggle_hints_button)
        pygame.draw.rect(self.screen, self.COLORS['text'], self.toggle_hints_button, 2)
        
        hints_text = "Hide Hints" if self.show_valid_moves else "Show Hints"
        text = self.small_font.render(hints_text, True, self.COLORS['text'])
        text_rect = text.get_rect(center=self.toggle_hints_button.center)
        self.screen.blit(text, text_rect)


class MultiplayerGameScreen:
    def __init__(self, network_client=None, user_data=None):
        pygame.init()
        
        # Network setup
        self.network_client = network_client or NetworkClient()
        self.user_data = user_data
        
        # Game settings
        self.board_size = 8
        self.cell_size = 60
        self.board_margin = 50
        self.sidebar_width = 250
        
        # Calculate window dimensions
        self.board_width = self.cell_size * self.board_size
        self.board_height = self.cell_size * self.board_size
        self.window_width = self.board_width + self.board_margin * 2 + self.sidebar_width
        self.window_height = self.board_height + self.board_margin * 2
        
        # Colors
        self.COLORS = {
            'background': (34, 139, 34),  # Forest green
            'board': (0, 100, 0),         # Dark green
            'grid_line': (0, 50, 0),      # Very dark green
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'valid_move': (255, 255, 0),  # Yellow
            'text': (255, 255, 255),
            'sidebar': (60, 60, 60),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'your_turn': (0, 255, 0),
            'opponent_turn': (255, 0, 0)
        }
        
        # Initialize pygame
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Othello - Multiplayer")
        self.clock = pygame.time.Clock()
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Game state
        self.board = Board(self.board_size)
        self.game_over = False
        self.waiting_for_opponent = False
        self.your_turn = False
        self.your_piece = 1  # Will be set by server (1=black, 2=white)
        self.opponent_name = "Opponent"
        self.your_name = self.user_data.get('username', 'You') if self.user_data else "You"
        
        # Game info from server
        self.game_players = {}
        self.game_player_info = {}
        self.game_state = {}
        
        # UI elements
        self.back_button = pygame.Rect(self.window_width - 180, 50, 150, 40)
        self.surrender_button = pygame.Rect(self.window_width - 180, 100, 150, 40)
        
        # Initialize multiplayer game
        self.setup_multiplayer_game()
    
    def setup_multiplayer_game(self):
        """Setup multiplayer game from network client data"""
        if hasattr(self.network_client, 'current_game_players'):
            self.game_players = getattr(self.network_client, 'current_game_players', {}) or {}
        else:
            self.game_players = {}
            
        if hasattr(self.network_client, 'current_game_player_info'):
            self.game_player_info = getattr(self.network_client, 'current_game_player_info', {}) or {}
        else:
            self.game_player_info = {}
            
        if hasattr(self.network_client, 'current_game_state'):
            self.game_state = getattr(self.network_client, 'current_game_state', {}) or {}
        else:
            self.game_state = {}
        
        print(f"Setting up multiplayer game:")
        print(f"  Players: {self.game_players}")
        print(f"  Player info: {self.game_player_info}")
        print(f"  User data: {self.user_data}")
        
        # Determine your piece color and opponent
        if self.user_data and 'username' in self.user_data and self.game_players:
            username = self.user_data['username']
            user_id = self.user_data.get('user_id')
            print(f"Looking for user: {username} (ID: {user_id})")
            
            # Find your color based on user_id or username
            your_color = None
            for color, pid in self.game_players.items():
                print(f"Checking color {color} with player ID {pid}")
                if pid == user_id:
                    your_color = color
                    print(f"Matched by user_id: {color}")
                    break
                elif color in self.game_player_info:
                    info_username = self.game_player_info[color].get('username')
                    print(f"  {color} player info: {self.game_player_info[color]}")
                    if info_username == username:
                        your_color = color
                        print(f"Matched by username: {color}")
                        break
            
            if your_color:
                self.your_piece = 1 if your_color == 'black' else 2  # 1=black, 2=white
                self.your_turn = (self.board.get_current_player() == self.your_piece)
                print(f"You are playing as {your_color} (piece {self.your_piece})")
                print(f"Your turn: {self.your_turn}")
                
                # Find opponent name
                if self.game_player_info:
                    for color, info in self.game_player_info.items():
                        if color != your_color:
                            self.opponent_name = info.get('username', 'Opponent') if info else 'Opponent'
                            print(f"Opponent is {self.opponent_name} playing as {color}")
                            break

                    for color, info in self.game_player_info.items():
                            if color != your_color:
                                self.opponent_name = info.get('username', 'Opponent')
                                print(f"Opponent is {self.opponent_name} playing as {color}")
                                break
                            
                # No longer waiting for opponent since game started
                self.waiting_for_opponent = False
            else:
                print("Could not determine your color, defaulting to black")
                self.your_piece = 1  # Default to black
                self.your_turn = True  # Black goes first
                self.waiting_for_opponent = True
        else:
            print("No user data available")
            self.your_piece = 1  # Default to black
            self.your_turn = True  # Black goes first
            self.waiting_for_opponent = True
        
        # If no game info from server, default to player 1 (black) going first
        if not self.game_player_info and self.user_data:
            self.your_piece = 1  # Default to black
            self.your_turn = True  # Black goes first
            print("No game info from server, defaulting to black piece")
        
        # Setup network callbacks
        self.setup_network_callbacks()
    
    def setup_network_callbacks(self):
        """Setup network event callbacks"""
        def on_game_update(payload):
            """Handle game update from server"""
            print(f"=== GAME UPDATE RECEIVED ===")
            print(f"Payload: {payload}")
            
            game_state = payload.get('game_state', {})
            if game_state:
                self.update_board_from_server(game_state)
        
        def on_move_made(payload):
            row = payload.get('row')
            col = payload.get('col')
            player = payload.get('player')
            
            if row is not None and col is not None:
                # Update board state
                if self.board.is_valid_move(row, col):
                    self.board.make_move(row, col)
                    self.your_turn = (self.board.get_current_player() == self.your_piece)
                    self.waiting_for_opponent = not self.your_turn
                    
                    # Check if game is over
                    if self.board.is_game_over():
                        self.game_over = True
        
        def on_game_over(payload):
            winner = payload.get('winner')
            self.game_over = True
        
        def on_opponent_disconnected(payload):
            self.game_over = True
            self.opponent_name = "Disconnected"
        
        # Set callbacks if methods exist
        self.network_client.on_game_update = on_game_update
        if hasattr(self.network_client, 'on_move_made'):
            self.network_client.on_move_made = on_move_made
        if hasattr(self.network_client, 'on_game_over'):
            self.network_client.on_game_over = on_game_over
        if hasattr(self.network_client, 'on_opponent_disconnected'):
            self.network_client.on_opponent_disconnected = on_opponent_disconnected
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "quit"
                
                elif event.type == pygame.USEREVENT + 1:
                    # Fallback: simulate opponent turn
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer
                    self.your_turn = True
                    self.waiting_for_opponent = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        action = self.handle_click(event.pos)
                        if action:
                            return action
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        return "back"
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        x, y = pos
        
        # Check if click is on back button
        if self.back_button.collidepoint(pos):
            return "back"
        
        # Check if click is on surrender button
        if self.surrender_button.collidepoint(pos):
            self.surrender_game()
            return "back"
        
        # Check if click is on the board (only if it's your turn)
        if (self.your_turn and not self.game_over and
            self.board_margin <= x <= self.board_margin + self.board_width and
            self.board_margin <= y <= self.board_margin + self.board_height):
            
            # Convert pixel coordinates to board coordinates
            col = (x - self.board_margin) // self.cell_size + 1
            row = (y - self.board_margin) // self.cell_size + 1
            
            # Make move if valid
            if self.board.is_valid_move(row, col):
                self.make_multiplayer_move(row, col)
        
        return None
    
    def make_multiplayer_move(self, row, col):
        """Make a move in multiplayer game"""
        if not self.your_turn or self.game_over:
            print(f"Cannot make move - your_turn: {self.your_turn}, game_over: {self.game_over}")
            return
        
        # Validate move locally first
        if not self.board.is_valid_move(row, col):
            print(f"Invalid move: row={row}, col={col}")
            return
        
        print(f"Making multiplayer move: row={row}, col={col}")
        
        # Send move to server if network client is available
        if self.network_client and hasattr(self.network_client, 'make_move'):
            try:
                self.network_client.make_move(row, col)
                print(f"Move sent to server successfully")
                
                # Don't update local board here - wait for server response
                self.your_turn = False
                self.waiting_for_opponent = True
                print(f"Waiting for server response...")
                
            except Exception as e:
                print(f"Failed to send move to server: {e}")
                # If server communication fails, revert state
                self.your_turn = True
                self.waiting_for_opponent = False
        else:
            print("No network client available - making local move")
            # Fallback: make local move if no network
            if self.board.make_move(row, col):
                self.your_turn = False
                self.waiting_for_opponent = True
                
                # Check if game is over
                if self.board.is_game_over():
                    self.game_over = True
                    
            # Simulate opponent move after delay for offline mode
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1 second delay
    
    def surrender_game(self):
        """Surrender the current game"""
        if self.network_client and hasattr(self.network_client, 'surrender_game'):
            try:
                self.network_client.surrender_game()
            except Exception as e:
                print(f"Failed to send surrender to server: {e}")
        self.game_over = True
    
    def draw(self):
        """Draw the game"""
        # Clear screen
        self.screen.fill(self.COLORS['background'])
        
        # Draw board
        self.draw_board()
        
        # Draw pieces
        self.draw_pieces()
        
        # Draw valid moves if it's your turn
        if self.your_turn and not self.game_over:
            self.draw_valid_moves()
        
        # Draw sidebar
        self.draw_sidebar()
        
        # Draw buttons
        self.draw_buttons()
        
        # Draw game status
        self.draw_game_status()
    
    def draw_board(self):
        """Draw the game board"""
        board_rect = pygame.Rect(
            self.board_margin, 
            self.board_margin, 
            self.board_width, 
            self.board_height
        )
        pygame.draw.rect(self.screen, self.COLORS['board'], board_rect)
        
        # Draw grid lines
        for i in range(self.board_size + 1):
            # Vertical lines
            x = self.board_margin + i * self.cell_size
            pygame.draw.line(
                self.screen, 
                self.COLORS['grid_line'], 
                (x, self.board_margin), 
                (x, self.board_margin + self.board_height), 
                2
            )
            
            # Horizontal lines
            y = self.board_margin + i * self.cell_size
            pygame.draw.line(
                self.screen, 
                self.COLORS['grid_line'], 
                (self.board_margin, y), 
                (self.board_margin + self.board_width, y), 
                2
            )
    
    def draw_pieces(self):
        """Draw game pieces"""
        grid = self.board.get_grid()
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if grid[row][col] != 0:
                    # Calculate center of cell
                    center_x = self.board_margin + col * self.cell_size + self.cell_size // 2
                    center_y = self.board_margin + row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 3
                    
                    # Choose color
                    color = self.COLORS['black'] if grid[row][col] == 1 else self.COLORS['white']
                    
                    # Draw piece
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
                    
                    # Draw border for white pieces
                    if grid[row][col] == 2:
                        pygame.draw.circle(self.screen, self.COLORS['black'], (center_x, center_y), radius, 2)
    
    def draw_valid_moves(self):
        """Draw valid move indicators"""
        valid_moves = self.board.get_valid_moves()
        
        for row, col in valid_moves:
            # Convert to 0-based indexing for drawing
            row_idx = row - 1
            col_idx = col - 1
            
            center_x = self.board_margin + col_idx * self.cell_size + self.cell_size // 2
            center_y = self.board_margin + row_idx * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 6
            
            pygame.draw.circle(self.screen, self.COLORS['valid_move'], (center_x, center_y), radius)
    
    def draw_sidebar(self):
        """Draw game information sidebar"""
        sidebar_x = self.board_margin + self.board_width + 20
        
        # Player info
        y_offset = 150
        
        # Your info
        your_color = self.COLORS['black'] if self.your_piece == 1 else self.COLORS['white']
        text = self.font.render(f"You: {self.your_name}", True, your_color)
        self.screen.blit(text, (sidebar_x, y_offset))
        
        # Draw your piece indicator
        # pygame.draw.circle(self.screen, your_color, (sidebar_x + 180, y_offset + 15), 12)
        # if self.your_piece == 2:  # White piece needs border
        #     pygame.draw.circle(self.screen, self.COLORS['black'], (sidebar_x + 180, y_offset + 15), 12, 2)
        
        y_offset += 40
        
        # Opponent info
        opponent_piece = 2 if self.your_piece == 1 else 1
        opponent_color = self.COLORS['black'] if opponent_piece == 1 else self.COLORS['white']
        text = self.font.render(f"Opponent: {self.opponent_name}", True, opponent_color)
        self.screen.blit(text, (sidebar_x, y_offset))
        
        # Draw opponent piece indicator
        # pygame.draw.circle(self.screen, opponent_color, (sidebar_x + 180, y_offset + 15), 12)
        # if opponent_piece == 2:  # White piece needs border
        #     pygame.draw.circle(self.screen, self.COLORS['black'], (sidebar_x + 180, y_offset + 15), 12, 2)
        
        y_offset += 60
        
        # Score
        black_score, white_score = self.board.get_score()
        
        text = self.font.render("Score:", True, self.COLORS['text'])
        self.screen.blit(text, (sidebar_x, y_offset))
        
        y_offset += 30
        text = self.small_font.render(f"Black: {black_score}", True, self.COLORS['text'])
        self.screen.blit(text, (sidebar_x, y_offset))
        
        y_offset += 25
        text = self.small_font.render(f"White: {white_score}", True, self.COLORS['text'])
        self.screen.blit(text, (sidebar_x, y_offset))
        
        y_offset += 40
        
        # Game over message
        if self.game_over:
            winner = self.board.get_winner()
            if winner == 0:
                text = self.font.render("Tie Game!", True, self.COLORS['text'])
            elif winner == self.your_piece:
                text = self.font.render("You Win!", True, self.COLORS['your_turn'])
            else:
                text = self.font.render("You Lose!", True, self.COLORS['opponent_turn'])
            
            self.screen.blit(text, (sidebar_x, y_offset))
        
        # Valid moves count (only if your turn)
        elif self.your_turn:
            valid_moves_count = len(self.board.get_valid_moves())
            text = self.small_font.render(f"Valid moves: {valid_moves_count}", True, self.COLORS['text'])
            self.screen.blit(text, (sidebar_x, y_offset))
    
    def draw_buttons(self):
        """Draw UI buttons"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Back button
        color = self.COLORS['button_hover'] if self.back_button.collidepoint(mouse_pos) else self.COLORS['button']
        pygame.draw.rect(self.screen, color, self.back_button)
        pygame.draw.rect(self.screen, self.COLORS['text'], self.back_button, 2)
        
        text = self.small_font.render("Back to Menu", True, self.COLORS['text'])
        text_rect = text.get_rect(center=self.back_button.center)
        self.screen.blit(text, text_rect)
        
        # Surrender button (only if game is active)
        if not self.game_over:
            color = self.COLORS['button_hover'] if self.surrender_button.collidepoint(mouse_pos) else self.COLORS['button']
            pygame.draw.rect(self.screen, color, self.surrender_button)
            pygame.draw.rect(self.screen, self.COLORS['text'], self.surrender_button, 2)
            
            text = self.small_font.render("Surrender", True, self.COLORS['text'])
            text_rect = text.get_rect(center=self.surrender_button.center)
            self.screen.blit(text, text_rect)
    
    def draw_game_status(self):
        """Draw current game status at the top"""
        status_text = ""
        status_color = self.COLORS['text']
        
        if self.game_over:
            winner = self.board.get_winner()
            if winner == 0:
                status_text = "Game Over - Tie!"
            elif winner == self.your_piece:
                status_text = "Game Over - You Win!"
                status_color = self.COLORS['your_turn']
            else:
                status_text = "Game Over - You Lose!"
                status_color = self.COLORS['opponent_turn']
        elif self.waiting_for_opponent:
            status_text = f"Waiting for Opponent..."
            status_color = self.COLORS['opponent_turn']
        elif self.your_turn:
            status_text = "Your Turn - Make a Move!"
            status_color = self.COLORS['your_turn']
        else:
            status_text = f"{self.opponent_name}'s Turn"
            status_color = self.COLORS['opponent_turn']
        
        # Draw status text
        text_surface = self.large_font.render(status_text, True, status_color)
        text_rect = text_surface.get_rect(center=(self.window_width // 2, 30))
        self.screen.blit(text_surface, text_rect)
    
    def update_board_from_server(self, game_state):
        """Update local board from server game state"""
        print(f"Updating board from server game state")
        
        # Get board data from server
        server_board = game_state.get('board', [])
        turn = game_state.get('turn', 'black')
        scores = game_state.get('scores', {'black': 2, 'white': 2})
        game_over = game_state.get('game_over', False)
        winner = game_state.get('winner')
        
        print(f"Server board: {server_board}")
        print(f"Current turn: {turn}")
        print(f"Scores: {scores}")
        print(f"Game over: {game_over}")
        
        if server_board and len(server_board) == 8:
            # Update local board grid
            for i in range(8):
                for j in range(8):
                    server_cell = server_board[i][j]
                    if server_cell == 'black':
                        self.board._grid[i][j] = 1
                    elif server_cell == 'white':
                        self.board._grid[i][j] = 2
                    else:
                        self.board._grid[i][j] = 0
            
            # Update current player
            self.board._current_player = 1 if turn == 'black' else 2
            
            # Update turn state
            self.your_turn = (self.board._current_player == self.your_piece)
            self.waiting_for_opponent = not self.your_turn
            
            # Update game over state
            self.game_over = game_over
            
            print(f"Board updated - Your turn: {self.your_turn}, Waiting: {self.waiting_for_opponent}")


def main():
    """Main function"""
    # You can change board size here (must be even number)
    game = ReversiGame(board_size=8)
    game.run()


if __name__ == "__main__":
    main()