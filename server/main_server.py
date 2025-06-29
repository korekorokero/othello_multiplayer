# server/main_server.py
import socket
import threading
from server.user_manager import UserManager
from server.room_manager import RoomManager

HOST = '0.0.0.0'
PORT = 55555

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Initialize managers
        self.room_manager = RoomManager()
        self.user_manager = UserManager(self.room_manager)

    def start(self):
        """Binds the server and starts listening for connections."""
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f"[MainServer] Server started and listening on {self.host}:{self.port}")

        try:
            while True:
                connection, address = self.socket.accept()
                # Create a new thread for each client to handle their connection
                thread = threading.Thread(target=self.handle_client, args=(connection, address))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\n[MainServer] Shutting down.")
        finally:
            self.socket.close()

    def handle_client(self, connection, address):
        """
        Manages a single client connection from start to finish.
        """
        user = self.user_manager.add_user(connection, address)
        
        buffer = ""
        try:
            while True:
                data = connection.recv(1024*1024).decode('utf-8')
                if not data:
                    break # Client disconnected
                
                buffer += data
                # Messages are delimited by newlines
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message:
                        self.user_manager.handle_message(user, message)

        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"[MainServer] Connection with {address} was lost: {e}")
        except Exception as e:
            print(f"[MainServer] An unexpected error occurred with {address}: {e}")
        finally:
            print(f"[MainServer] Closing connection for {address}.")
            self.user_manager.remove_user(user)
            connection.close()


if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.start()

