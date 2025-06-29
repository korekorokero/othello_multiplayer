import socket
import selectors
import types
import sys
import threading

class GameClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.connected = False
        
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
        return True
        
    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(2048)
            if recv_data:
                message = recv_data.decode('utf-8')
                print(message, end='')
                
                # Check if server is asking for input
                if message.endswith(': '):
                    # Start input thread
                    input_thread = threading.Thread(target=self.get_user_input, args=(data,))
                    input_thread.daemon = True
                    input_thread.start()
                    
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

    def get_user_input(self, data):
        """Get user input in a separate thread"""
        try:
            user_input = input()
            message = user_input + '\n'
            data.outb += message.encode('utf-8')
        except (EOFError, KeyboardInterrupt):
            data.should_close = True

    def run(self):
        if not self.start_connection():
            return
        
        try:
            while self.connected:
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask)
                        
                # Check if we still have connections
                if not self.sel.get_map():
                    break
                    
        except KeyboardInterrupt:
            print('\nDisconnecting...')
        finally:
            self.sel.close()

if __name__ == '__main__':
    client = GameClient()
    print("=== Othello Multiplayer Client ===")
    print("Instructions:")
    print("- Enter moves as: row,col (e.g., 3,4)")
    print("- Wait for your turn")
    print("- Press Ctrl+C to quit")
    print("=" * 35)
    
    client.run()