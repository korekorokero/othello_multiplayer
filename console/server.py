import socket
import selectors
import types
from board import Board

class GameServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.board = Board()
        self.players = {}  # {socket: player_number}
        self.player_addresses = {}  # {player_number: address}
        self.connections = {}  # {socket: data}
        
    def start_server(self):
        # Create listening socket
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print(f'Server listening on {self.host}:{self.port}')
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)
        
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.sel.close()

    def accept_connection(self, sock):
        conn, addr = sock.accept()
        print(f'Accepted connection from {addr}')
        
        # Only allow 2 players
        if len(self.players) >= 2:
            print(f'Rejecting connection from {addr} - game full')
            conn.close()
            return
        
        conn.setblocking(False)
        
        # Assign player number (1 or 2)
        player_num = len(self.players) + 1
        
        data = types.SimpleNamespace(
            addr=addr,
            inb=b'',
            outb=b'',
            player_num=player_num
        )
        
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        
        # Store player info
        self.players[conn] = player_num
        self.player_addresses[player_num] = addr
        self.connections[conn] = data
        
        print(f'Player {player_num} connected from {addr}')
        
        # Send welcome message
        welcome_msg = f"Welcome! You are Player {player_num} ({'Black' if player_num == 1 else 'White'})\n"
        if len(self.players) < 2:
            welcome_msg += "Waiting for another player...\n"
        
        data.outb += welcome_msg.encode('utf-8')
        
        # If we have 2 players, start the game
        if len(self.players) == 2:
            self.start_game()

    def start_game(self):
        print("Starting game with 2 players!")
        self.broadcast_board()

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(2048)
            if recv_data:
                data.inb += recv_data
                self.process_message(sock, data)
            else:
                print(f'Closing connection to {data.addr}')
                self.close_connection(sock)

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                try:
                    sent = sock.send(data.outb)
                    data.outb = data.outb[sent:]
                except BrokenPipeError:
                    print(f'Connection to {data.addr} broken')
                    self.close_connection(sock)

    def process_message(self, sock, data):
        # Process complete messages (assume one message per recv for simplicity)
        if b'\n' in data.inb:
            message = data.inb.decode('utf-8').strip()
            data.inb = b''
            
            print(f'Received from Player {data.player_num}: {message}')
            
            # Check if it's this player's turn
            current_player = self.board.get_current_player()
            if data.player_num != current_player:
                response = "It's not your turn! Please wait...\n"
                data.outb += response.encode('utf-8')
                return
            
            # Parse move (format: "row,col" or "row col")
            try:
                if ',' in message:
                    row, col = map(int, message.split(','))
                else:
                    row, col = map(int, message.split())
                
                # Try to make the move
                if self.board.make_move(row, col):
                    print(f'Player {data.player_num} played: {row},{col}')
                    
                    # Check if game is over
                    if self.board.is_game_over():
                        self.end_game()
                    else:
                        self.broadcast_board()
                else:
                    response = "Invalid move! Try again.\n"
                    data.outb += response.encode('utf-8')
                    # Show valid moves to help the player
                    valid_moves = self.board.get_valid_moves()
                    if valid_moves:
                        response += f"Valid moves: {valid_moves}\nEnter your move (row,col): "
                        data.outb += response.encode('utf-8')
                    
            except (ValueError, IndexError):
                response = "Invalid format! Use: row,col (e.g., 3,4)\n"
                valid_moves = self.board.get_valid_moves()
                if valid_moves:
                    response += f"Valid moves: {valid_moves}\n"
                response += "Enter your move (row,col): "
                data.outb += response.encode('utf-8')

    def broadcast_board(self):
        """Send current board state to all players"""
        board_str = self.board.get_display()
        current_player = self.board.get_current_player()
        
        # Add valid moves info
        valid_moves = self.board.get_valid_moves()
        if valid_moves:
            board_str += f"Valid moves: {valid_moves}\n"
        else:
            board_str += "No valid moves available!\n"
        
        # Send to all players, but only ask for input from current player
        for sock, data in self.connections.items():
            message = board_str
            
            # Only show input prompt to current player
            if data.player_num == current_player:
                if valid_moves:
                    message += "Your turn! Enter your move (row,col): "
                else:
                    message += "You have no valid moves. Turn will be skipped.\n"
            else:
                if valid_moves:
                    player_name = "Black" if current_player == 1 else "White"
                    message += f"Waiting for {player_name} (Player {current_player}) to move...\n"
                else:
                    message += "Waiting for turn to be processed...\n"
            
            data.outb += message.encode('utf-8')

    def end_game(self):
        """End the game and announce winner"""
        winner = self.board.get_winner()
        
        # Send personalized messages to each player
        for sock, data in self.connections.items():
            player_num = data.player_num
            
            # Personal message
            if winner == 0:
                personal_msg = "\n🎭 YOU TIE! 🎭\n"
            elif winner == player_num:
                personal_msg = "\n🎉 YOU WIN! 🎉\n"
            else:
                personal_msg = "\n😔 YOU LOSE! 😔\n"
            
            # Game result message
            if winner == 0:
                result_msg = "=== GAME OVER - IT'S A TIE! ===\n"
            else:
                winner_name = "Black" if winner == 1 else "White"
                result_msg = f"=== GAME OVER - {winner_name} (Player {winner}) WINS! ===\n"
            
            # Complete message
            message = personal_msg + result_msg + self.board.get_display()
            message += "\nThanks for playing!\n"
            
            data.outb += message.encode('utf-8')
        
        print(f"Game ended. Winner: Player {winner}")

    def close_connection(self, sock):
        """Clean up when a connection closes"""
        if sock in self.players:
            player_num = self.players[sock]
            print(f'Player {player_num} disconnected')
            
            # Clean up
            del self.players[sock]
            del self.player_addresses[player_num]
            del self.connections[sock]
            
            # Notify remaining player
            if self.connections:
                msg = f"Player {player_num} disconnected. Game ended.\n"
                for remaining_sock, data in self.connections.items():
                    data.outb += msg.encode('utf-8')
        
        try:
            self.sel.unregister(sock)
        except:
            pass
        
        try:
            sock.close()
        except:
            pass

if __name__ == '__main__':
    server = GameServer()
    server.start_server()