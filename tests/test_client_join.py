# test_client_joiner.py
import socket
import threading
import json
import time

class ClientJoiner:
    def __init__(self, host='localhost', port=55555, username='Player2'):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = username
        self.running = True

    def listen_to_server(self):
        """Runs in a thread to listen for and print server messages."""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(2048).decode('utf-8')
                if not data:
                    print("\n[INFO] Disconnected from server.")
                    self.running = False
                    break
                
                buffer += data
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str:
                        message = json.loads(message_str)
                        print(f"\n[SERVER] {message}")
            except Exception as e:
                if self.running:
                    print(f"\n[ERROR] An error occurred: {e}")
                self.running = False
                break

    def send_message(self, msg_type, payload):
        """Formats and sends a JSON message to the server."""
        try:
            message = json.dumps({"type": msg_type, "payload": payload}) + '\n'
            self.socket.sendall(message.encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError):
            print("[ERROR] Connection to server lost.")
            self.running = False

    def start(self):
        """Connects and runs the client logic."""
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return

        # Start the listening thread
        thread = threading.Thread(target=self.listen_to_server, daemon=True)
        thread.start()

        # --- Client Actions ---
        time.sleep(0.5)
        print("\n--- Step 1: Registering User ---")
        self.send_message("register_user", {"username": self.username})
        
        time.sleep(0.5)
        
        # Keep the main thread alive to allow sending messages or quitting
        try:
            # --- Step 2: Prompt user and join room ---
            room_code = input("Enter the room code to join: ").strip().upper()
            if room_code:
                print(f"\n--- Step 3: Joining Room {room_code} ---")
                self.send_message("join_room", {"room_code": room_code})
            
            print("\n[INFO] Once the game starts, you can enter moves.")
            
            # --- Step 4: Interactive move handling ---
            while self.running:
                move_input = input("Enter your move (row,col) or 'quit' to exit: ").strip().lower()
                
                if move_input == 'quit':
                    break
                
                try:
                    parts = move_input.split(',')
                    if len(parts) != 2:
                        print("[INVALID INPUT] Please use the format 'row,col', e.g., '2,3'")
                        continue
                    
                    row = int(parts[0])
                    col = int(parts[1])
                    
                    print(f"\n--- Sending move: ({row},{col}) ---")
                    self.send_message("make_move", {"move": [row, col]})

                except ValueError:
                    print("[INVALID INPUT] Row and column must be numbers.")
                except Exception as e:
                    print(f"[ERROR] Could not process your move: {e}")

        except KeyboardInterrupt:
            print("\nShutting down client.")
        except EOFError: # Happens if the input stream is closed
             print("\nInput stream closed, shutting down.")
        finally:
            self.running = False
            self.socket.close()

if __name__ == "__main__":
    client2 = ClientJoiner()
    client2.start()
