from functools import reduce

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

    def get_grid(self):
        """Get the grid for pygame rendering"""
        return self._grid

    def get_size(self):
        """Get board size"""
        return self._size

    def get_score(self):
        """Get current scores as (black_count, white_count)"""
        black_count = sum(row.count(1) for row in self._grid)
        white_count = sum(row.count(2) for row in self._grid)
        return black_count, white_count

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

# Test the display
if __name__ == "__main__":
    board = Board()
    print(board.get_display())