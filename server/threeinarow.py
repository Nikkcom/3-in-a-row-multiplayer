__all__ = ["PLAYER_ONE", "PLAYER_TWO", "Threeinarow"]

PLAYER_ONE = "cross"
PLAYER_TWO = "circle"

class Threeinarow:
    """
    A Three in a Row game.
    """

    def __init__(self):
        self.moves = []
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.winner = None
        self.winning_position = None

    @property
    def last_player(self):
        """
        Player who played the last move.

        """
        return PLAYER_ONE if len(self.moves) % 2 else PLAYER_TWO

    @property
    def last_player_won(self):
        """
        If the last move is a winning move.
        Returns the winning position.
        """
        if self.winning_position is not None:
            return self.winning_position

        # Checks for a winning position vertically.
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                self.winner = self.board[0][col]
                self.winning_position = [(0, col), (1, col), (2, col)]
                return self.winning_position

        # Checks if a there is a winning position horizontally
        for row in self.board:
            if row[0] == row[1] == row[2] != "":
                self.winner = row[0]
                # Redo this \/
                self.winning_position = [(self.board.index(row), i) for i in range(3)]
                return self.winning_position


        # Checks for a winning position diagonally
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            self.winner = self.board[0][0]
            self.winning_position = [(0, 0), (1, 1), (2, 2)]
            return self.winning_position
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            self.winner = self.board[0][2]
            self.winning_position = [(0, 2), (1, 1), (2, 0)]
            return self.winning_position

        return []

    def play(self, player, row, col):
        """
        Play a move at the specified row and column.

        Returns the current state of the board.

        Raises ValueError exception if the move is illegal.
        """

        if player == self.last_player:
            raise ValueError("It is not your turn.")

        if row < 0 or row > 2 or col < 0 or col > 2:
            raise ValueError("Invalid row or column.")

        if self.board[row][col] != "":
            raise ValueError("This cell is already taken.")

        self.board[row][col] = player
        self.moves.append((row, col))

        _ = self.last_player_won
