"""Store the board and game logic for Peg Solitaire."""


class SolitaireGame:
    """Manage the game independently from the graphical interface."""

    BOARD_TYPES = ("English", "Hexagon", "Diamond")
    BOARD_SIZES = (7, 9)

    def __init__(self, board_type="English", size=7):
        self.new_game(board_type, size)

    def new_game(self, board_type, size):
        """Create the selected board with its center empty."""
        if board_type not in self.BOARD_TYPES:
            raise ValueError("Unsupported board type.")

        if size not in self.BOARD_SIZES:
            raise ValueError("Board size must be 7 or 9.")

        self.board_type = board_type
        self.size = size
        self.board = {}

        center = size // 2

        for row in range(size):
            for column in range(size):
                if self.is_playable_position(row, column):
                    # True means a peg; False means an empty hole.
                    self.board[(row, column)] = True

        self.board[(center, center)] = False

    def is_playable_position(self, row, column):
        """Check whether a position belongs to the chosen layout."""
        if not (0 <= row < self.size and 0 <= column < self.size):
            return False

        center = self.size // 2

        if self.board_type == "English":
            # A cross with three-hole-wide horizontal and vertical arms.
            return (
                abs(row - center) <= 1
                or abs(column - center) <= 1
            )

        if self.board_type == "Diamond":
            return (
                abs(row - center) + abs(column - center)
                <= center
            )

        # Hexagon stored using offset coordinates.
        return abs(row - column) <= center

    def peg_count(self):
        """Return the number of pegs currently on the board."""
        return sum(self.board.values())
    
    def move_directions(self):
        """Return the allowed jump directions for this board."""
        if self.board_type == "Hexagon":
            # Six directions matching the offset hexagon display.
            return (
                (-1, -1), (-1, 0),
                (0, -1), (0, 1),
                (1, 0), (1, 1),
            )

        # The assignment allows orthogonal and diagonal jumps.
        return (
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        )

    def is_valid_move(self, start, destination):
        """Check a jump without changing the board."""
        if start not in self.board or destination not in self.board:
            return False

        if not self.board[start] or self.board[destination]:
            return False

        row_change = destination[0] - start[0]
        column_change = destination[1] - start[1]

        allowed_jumps = {
            (2 * row, 2 * column)
            for row, column in self.move_directions()
        }

        if (row_change, column_change) not in allowed_jumps:
            return False

        middle = (
            start[0] + row_change // 2,
            start[1] + column_change // 2,
        )

        return self.board.get(middle, False)

    def make_move(self, start, destination):
        """Apply a legal jump and leave invalid moves unchanged."""
        if not self.is_valid_move(start, destination):
            return False

        middle = (
            (start[0] + destination[0]) // 2,
            (start[1] + destination[1]) // 2,
        )

        self.board[start] = False
        self.board[middle] = False
        self.board[destination] = True
        return True

    def has_valid_moves(self):
        """Check whether any legal jump remains."""
        for start, has_peg in self.board.items():
            if not has_peg:
                continue

            for row_change, column_change in self.move_directions():
                destination = (
                    start[0] + 2 * row_change,
                    start[1] + 2 * column_change,
                )

                if self.is_valid_move(start, destination):
                    return True

        return False
    
    def game_result(self):
        """Report whether the game is won, blocked, or still playable."""
        if self.peg_count() == 1:
            return "win"

        if not self.has_valid_moves():
            return "no_moves"

        return "playing"
    
    def legal_moves(self):
        """Return all legal jumps from the current board."""
        moves = []

        for start, occupied in self.board.items():
            if not occupied:
                continue

            for row_change, column_change in self.move_directions():
                destination = (
                    start[0] + 2 * row_change,
                    start[1] + 2 * column_change,
                )

                if self.is_valid_move(start, destination):
                    moves.append((start, destination))

        return moves

    def randomize(self, rng=None):
        """Reposition pegs while preserving their count and board layout."""
        import random

        rng = rng or random
        positions = list(self.board)
        occupied = set(rng.sample(positions, self.peg_count()))

        self.board = {
            position: position in occupied
            for position in positions
        }