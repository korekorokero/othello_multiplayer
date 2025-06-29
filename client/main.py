import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from client.screens.screen_manager import ScreenManager


def main():
    app = ScreenManager()
    app.run()

if __name__ == "__main__":
    main()