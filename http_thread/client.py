import webbrowser
import sys
import time
import socket
import argparse

def check_server_connection(host, port, timeout=5):
    """Check if the server is running and accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description='Othello Game Client')
    parser.add_argument('--host', '-H', default='localhost', 
                       help='Server hostname (default: localhost)')
    parser.add_argument('--port', '-p', type=int, default=8889, 
                       help='Server port (default: 8889)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    
    print("🔴⚫ OTHELLO MULTIPLAYER CLIENT ⚫🔴")
    print("=" * 50)
    print(f"🔍 Checking server connection to {args.host}:{args.port}...")
    
    # Check if server is running
    if not check_server_connection(args.host, args.port):
        print(f"❌ Cannot connect to server at {args.host}:{args.port}")
        print()
        print("💡 Make sure the server is running:")
        print("   python server.py")
        print()
        sys.exit(1)
    
    print(f"✅ Server is running at {args.host}:{args.port}")
    
    # Construct the URL
    url = f"http://{args.host}:{args.port}"
    
    if not args.no_browser:
        print(f"🌐 Opening browser to {url}")
        try:
            webbrowser.open(url)
            print("✅ Browser opened successfully!")
        except Exception as e:
            print(f"❌ Could not open browser automatically: {e}")
            print(f"📝 Please manually open your browser and go to: {url}")
    else:
        print(f"📝 Browser not opened (--no-browser flag used)")
        print(f"   Manually open your browser and go to: {url}")
    
    print()
    print("🎮 Game Instructions:")
    print("  1. Enter your player name")
    print("  2. Create a new game or join an existing one")
    print("  3. Wait for an opponent to join")
    print("  4. Take turns placing pieces")
    print("  5. Valid moves are highlighted in orange")
    print()
    print("📋 Multiple clients can connect to the same server!")
    print("   Run this script multiple times for multiple players.")
    print("=" * 50)

if __name__ == "__main__":
    main()