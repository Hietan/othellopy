"""Advanced sample player."""

from dataclasses import dataclass

from othellopy.core import Board, Cell, Move, opponent
from othellopy.players.base import BasePlayer

_MAX_CONSECUTIVE_PASSES = 2
_MIN_SEARCH_DEPTH = 1
_SEARCH_DEPTH = 4
_WIN_SCORE = 100_000
_CORNER_BONUS = 1_000
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
_CORNERS = ((0, 0), (0, 7), (7, 0), (7, 7))


@dataclass(frozen=True)
class _SearchState:
    color: Cell
    depth: int
    alpha: int
    beta: int
    pass_count: int


class AdvancedPlayer(BasePlayer):
    """Advanced sample player that searches with alpha-beta pruning."""

    def __init__(self, color: Cell, *, depth: int = _SEARCH_DEPTH) -> None:
        """Initialize the player color and search depth."""
        super().__init__(color)
        if depth < _MIN_SEARCH_DEPTH:
            msg = "depth must be at least 1"
            raise ValueError(msg)

        self.depth = depth

    def next_move(self, board: Board) -> Move:
        """Return the legal move with the best alpha-beta search score."""
        moves = self.get_moves(board)
        return max(moves, key=lambda move: self._score_move(board, move))

    def _score_move(self, board: Board, move: Move) -> int:
        next_board = _apply_move(board, self.color, move)
        return _alphabeta(
            next_board,
            maximizing_color=self.color,
            state=_SearchState(
                color=self.opponent_color,
                depth=self.depth - 1,
                alpha=-_WIN_SCORE,
                beta=_WIN_SCORE,
                pass_count=0,
            ),
        )


def _alphabeta(
    board: Board,
    *,
    maximizing_color: Cell,
    state: _SearchState,
) -> int:
    if state.depth <= 0 or state.pass_count == _MAX_CONSECUTIVE_PASSES:
        return _evaluate_board(board, maximizing_color)

    moves = _valid_moves(board, state.color)
    next_color = opponent(state.color)
    if not moves:
        return _alphabeta(
            board,
            maximizing_color=maximizing_color,
            state=_SearchState(
                color=next_color,
                depth=state.depth - 1,
                alpha=state.alpha,
                beta=state.beta,
                pass_count=state.pass_count + 1,
            ),
        )

    alpha = state.alpha
    beta = state.beta
    if state.color == maximizing_color:
        best_score = -_WIN_SCORE
        for move in moves:
            score = _alphabeta(
                _apply_move(board, state.color, move),
                maximizing_color=maximizing_color,
                state=_SearchState(
                    color=next_color,
                    depth=state.depth - 1,
                    alpha=alpha,
                    beta=beta,
                    pass_count=0,
                ),
            )
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return best_score

    best_score = _WIN_SCORE
    for move in moves:
        score = _alphabeta(
            _apply_move(board, state.color, move),
            maximizing_color=maximizing_color,
            state=_SearchState(
                color=next_color,
                depth=state.depth - 1,
                alpha=alpha,
                beta=beta,
                pass_count=0,
            ),
        )
        best_score = min(best_score, score)
        beta = min(beta, best_score)
        if alpha >= beta:
            break
    return best_score


def _evaluate_board(board: Board, color: Cell) -> int:
    other_color = opponent(color)
    color_moves = _valid_moves(board, color)
    other_moves = _valid_moves(board, other_color)

    if not color_moves and not other_moves:
        score_difference = _count_cell(board, color) - _count_cell(board, other_color)
        if score_difference > 0:
            return _WIN_SCORE
        if score_difference < 0:
            return -_WIN_SCORE
        return 0

    return (
        _weighted_cells(board, color)
        - _weighted_cells(board, other_color)
        + (len(color_moves) - len(other_moves)) * _MOBILITY_WEIGHT
        + (_corner_count(board, color) - _corner_count(board, other_color))
        * _CORNER_BONUS
        + (_count_cell(board, color) - _count_cell(board, other_color)) * _DISC_WEIGHT
    )


def _weighted_cells(board: Board, color: Cell) -> int:
    return sum(
        _POSITION_WEIGHTS[row][col]
        for row, line in enumerate(board)
        for col, cell in enumerate(line)
        if cell == color
    )


def _corner_count(board: Board, color: Cell) -> int:
    return sum(1 for row, col in _CORNERS if board[row][col] == color)


def _count_cell(board: Board, color: Cell) -> int:
    return sum(row.count(color) for row in board)


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
        flips.extend(
            _flips_in_direction(board, color, move, (row_step, col_step))
        )
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
