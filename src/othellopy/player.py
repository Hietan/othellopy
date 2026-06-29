"""Player base class for Othello/Reversi exercises."""

from abc import ABC, abstractmethod

from othellopy.core import Board, Move, Piece, opponent

_DIRECTIONS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


class BasePlayer(ABC):
    """Base class for students to build their own Othello players."""

    @abstractmethod
    def __init__(self, color: Piece) -> None:
        """Initialize a player with a black or white piece color."""
        color = Piece(color)
        if color not in (Piece.BLACK, Piece.WHITE):
            msg = "color must be Piece.BLACK or Piece.WHITE"
            raise ValueError(msg)

        self.color = color
        self.opponent_color = opponent(color)

    @abstractmethod
    def next_move(self, board: Board) -> Move:
        """Return the next move as a zero-based (row, col) pair."""
        raise NotImplementedError

    def get_moves(self, board: Board) -> list[Move]:
        """Return all valid moves for this player."""
        moves = []
        for row, line in enumerate(board):
            for col, _ in enumerate(line):
                if self.is_valid_move(board, row, col):
                    moves.append((row, col))
        return moves

    def is_valid_move(self, board: Board, row: int, col: int) -> bool:
        """Return True if this player can place a piece at (row, col)."""
        return bool(self.get_flips(board, row, col))

    def get_flips(self, board: Board, row: int, col: int) -> list[Move]:
        """Return the pieces that would be flipped by placing at (row, col)."""
        if not _is_on_board(board, row, col):
            return []
        if board[row][col] != Piece.EMPTY:
            return []

        flips = []
        for row_step, col_step in _DIRECTIONS:
            flips.extend(
                self._get_flips_in_direction(board, row, col, row_step, col_step)
            )
        return flips

    def _get_flips_in_direction(
        self,
        board: Board,
        row: int,
        col: int,
        row_step: int,
        col_step: int,
    ) -> list[Move]:
        flips = []
        current_row = row + row_step
        current_col = col + col_step

        while _is_on_board(board, current_row, current_col):
            piece = board[current_row][current_col]
            if piece == self.opponent_color:
                flips.append((current_row, current_col))
            elif piece == self.color:
                return flips
            else:
                return []

            current_row += row_step
            current_col += col_step

        return []


def _is_on_board(board: Board, row: int, col: int) -> bool:
    return 0 <= row < len(board) and 0 <= col < len(board[row])
