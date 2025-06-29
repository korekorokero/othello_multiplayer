#!/usr/bin/env python3
"""
Main entry point for the Othello Multiplayer Server.
Run this file to start the server: python server/main.py
"""

import sys
import os

# Add the parent directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main_server import Server

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 55555      # Default port

def main():
    """Main function to start the Othello multiplayer server."""
    print("=" * 50)
    print("    OTHELLO MULTIPLAYER SERVER")
    print("=" * 50)
    print(f"Starting server on {HOST}:{PORT}")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Create and start the server
        server = Server(HOST, PORT)
        server.start()
    except KeyboardInterrupt:
        print("\n[Main] Server stopped by user.")
    except Exception as e:
        print(f"[Main] Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
