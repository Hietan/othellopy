"""Intermediate sample player."""

from othellopy.core import Board, Cell, Move, opponent
from othellopy.players.base import BasePlayer

_MOBILITY_WEIGHT = 8
_DISC_WEIGHT = 2
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
_POSITION_WEIGHTS = (
    (120, -20, 20, 5, 5, 20, -20, 120),
    (-20, -40, -5, -5, -5, -5, -40, -20),
    (20, -5, 15, 3, 3, 15, -5, 20),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (20, -5, 15, 3, 3, 15, -5, 20),
    (-20, -40, -5, -5, -5, -5, -40, -20),
    (120, -20, 20, 5, 5, 20, -20, 120),
)


class IntermediatePlayer(BasePlayer):
    """Intermediate sample player that uses a simple board evaluation."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> Move:
        """Return the legal move with the best one-ply heuristic score."""
        return max(
            self.get_moves(board),
            key=lambda move: self._score_move(board, move),
        )

    def _score_move(self, board: Board, move: Move) -> int:
        row, col = move
        next_board = _apply_move(board, self.color, move)
        return (
            _POSITION_WEIGHTS[row][col]
            + len(_flips_for(board, self.color, move)) * _DISC_WEIGHT
            - len(_valid_moves(next_board, self.opponent_color)) * _MOBILITY_WEIGHT
        )


def _valid_moves(board: Board, color: Cell) -> list[Move]:
    return [
        (row, col)
        for row, line in enumerate(board)
        for col, _ in enumerate(line)
        if _flips_for(board, color, (row, col))
    ]


def _apply_move(board: Board, color: Cell, move: Move) -> Board:
    next_board = [row.copy() for row in board]
    row, col = move
    next_board[row][col] = color
    for flip_row, flip_col in _flips_for(board, color, move):
        next_board[flip_row][flip_col] = color
    return next_board


def _flips_for(board: Board, color: Cell, move: Move) -> list[Move]:
    row, col = move
    if not _is_on_board(board, row, col):
        return []
    if board[row][col] != Cell.EMPTY:
        return []

    flips = []
    for row_step, col_step in _DIRECTIONS:
        flips.extend(_flips_in_direction(board, color, move, (row_step, col_step)))
    return flips


def _flips_in_direction(
    board: Board,
    color: Cell,
    move: Move,
    direction: Move,
) -> list[Move]:
    flips = []
    other_color = opponent(color)
    row, col = move
    row_step, col_step = direction
    current_row = row + row_step
    current_col = col + col_step

    while _is_on_board(board, current_row, current_col):
        cell = board[current_row][current_col]
        if cell == other_color:
            flips.append((current_row, current_col))
        elif cell == color:
            return flips
        else:
            return []

        current_row += row_step
        current_col += col_step

    return []


def _is_on_board(board: Board, row: int, col: int) -> bool:
    return 0 <= row < len(board) and 0 <= col < len(board[row])
