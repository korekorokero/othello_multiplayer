from socket import *
import socket
import threading
import time
import sys
import logging
import os
import webbrowser
from othello_http import OthelloHttpServer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create HTTP server instance
httpserver = OthelloHttpServer()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        rcv = ""
        content_length = 0
        headers_received = False
        
        try:
            while True:
                data = self.connection.recv(1024)
                if data:
                    # Convert bytes to string
                    d = data.decode('utf-8', errors='ignore')
                    rcv = rcv + d
                    
                    # Check if we have complete headers
                    if not headers_received and '\r\n\r\n' in rcv:
                        headers_received = True
                        headers, body = rcv.split('\r\n\r\n', 1)
                        
                        # Look for Content-Length header
                        for line in headers.split('\r\n'):
                            if line.lower().startswith('content-length:'):
                                try:
                                    content_length = int(line.split(':', 1)[1].strip())
                                except ValueError:
                                    content_length = 0
                                break
                        
                        # If we have all expected content, process request
                        if content_length == 0 or len(body.encode('utf-8')) >= content_length:
                            self.process_request(rcv)
                            break
                    
                    # If headers received but waiting for more body content
                    elif headers_received:
                        headers, body = rcv.split('\r\n\r\n', 1)
                        if len(body.encode('utf-8')) >= content_length:
                            self.process_request(rcv)
                            break
                    
                    # For GET requests (no body expected)
                    elif '\r\n\r\n' in rcv and rcv.startswith('GET'):
                        self.process_request(rcv)
                        break
                        
                else:
                    # No more data
                    break
                    
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {e}")
        finally:
            try:
                self.connection.close()
            except:
                pass

    def process_request(self, request_data):
        try:
            # Log the request
            first_line = request_data.split('\r\n')[0] if request_data else 'Invalid request'
            logging.info(f"Request from {self.address}: {first_line}")
            
            # Process the HTTP request
            response = httpserver.proses(request_data)
            
            # Send response
            self.connection.sendall(response)
            logging.info(f"Response sent to {self.address}")
            
        except Exception as e:
            logging.error(f"Error processing request from {self.address}: {e}")
            try:
                # Send basic error response
                error_response = httpserver.response(500, 'Internal Server Error', 'Server Error')
                self.connection.sendall(error_response)
            except:
                pass

class OthelloServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=8889):
        self.host = host
        self.port = port
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.my_socket.bind((self.host, self.port))
            self.my_socket.listen(10)
            
            logging.info(f"🎮 Othello HTTP Server started on {self.host}:{self.port}")
            logging.info(f"🌐 Open your browser and go to: http://localhost:{self.port}")
            logging.info("=" * 60)
            
            while self.running:
                try:
                    self.connection, self.client_address = self.my_socket.accept()
                    logging.info(f"New connection from {self.client_address}")

                    # Create new thread for each client
                    client_thread = ProcessTheClient(self.connection, self.client_address)
                    client_thread.daemon = True
                    client_thread.start()
                    
                    self.the_clients.append(client_thread)
                    
                    # Clean up finished threads periodically
                    self.the_clients = [t for t in self.the_clients if t.is_alive()]
                    
                except KeyboardInterrupt:
                    logging.info("Keyboard interrupt received")
                    break
                except Exception as e:
                    if self.running:
                        logging.error(f"Error accepting connection: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        logging.info("Shutting down server...")
        self.running = False
        
        try:
            self.my_socket.close()
        except:
            pass
        
        # Wait for client threads to finish
        for client_thread in self.the_clients:
            if client_thread.is_alive():
                client_thread.join(timeout=1)
        
        logging.info("Server shutdown complete")

def main():
    try:
        print("🔴⚫ OTHELLO MULTIPLAYER SERVER ⚫🔴")
        print("=" * 50)
        print("HTTP Server with Threading for Othello Game")
        print()
        print("Features:")
        print("  ✓ Multi-threaded HTTP server")
        print("  ✓ Web-based Othello interface")
        print("  ✓ Real-time multiplayer support")
        print("  ✓ Multiple concurrent games")
        print("  ✓ Session management")
        print("  ✓ JSON API endpoints")
        print("=" * 50)
        
        # Create and start server
        server = OthelloServer()
        server.daemon = True
        server.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        
        # Try to open browser automatically
        try:
            print(f"🌐 Opening browser to http://localhost:8889")
            webbrowser.open('http://localhost:8889')
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please open your browser and go to: http://localhost:8889")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            server.shutdown()
            
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()