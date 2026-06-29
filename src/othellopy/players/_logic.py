"""Shared logic for sample players."""

from dataclasses import dataclass

from othellopy.core import Board, Cell, Move, opponent

MAX_CONSECUTIVE_PASSES = 2
MIN_SEARCH_DEPTH = 1
SEARCH_DEPTH = 4
WIN_SCORE = 100_000
CORNER_BONUS = 1_000
MOBILITY_WEIGHT = 8
DISC_WEIGHT = 2
DIRECTIONS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)
POSITION_WEIGHTS = (
    (120, -20, 20, 5, 5, 20, -20, 120),
    (-20, -40, -5, -5, -5, -5, -40, -20),
    (20, -5, 15, 3, 3, 15, -5, 20),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (20, -5, 15, 3, 3, 15, -5, 20),
    (-20, -40, -5, -5, -5, -5, -40, -20),
    (120, -20, 20, 5, 5, 20, -20, 120),
)
CORNERS = ((0, 0), (0, 7), (7, 0), (7, 7))


@dataclass(frozen=True)
class SearchState:
    """Alpha-beta search state."""

    color: Cell
    depth: int
    alpha: int
    beta: int
    pass_count: int


def alphabeta(
    board: Board,
    *,
    maximizing_color: Cell,
    state: SearchState,
) -> int:
    """Return an alpha-beta search score."""
    if state.depth <= 0 or state.pass_count == MAX_CONSECUTIVE_PASSES:
        return evaluate_board(board, maximizing_color)

    moves = valid_moves(board, state.color)
    next_color = opponent(state.color)
    if not moves:
        return alphabeta(
            board,
            maximizing_color=maximizing_color,
            state=SearchState(
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
        best_score = -WIN_SCORE
        for move in moves:
            score = alphabeta(
                apply_move(board, state.color, move),
                maximizing_color=maximizing_color,
                state=SearchState(
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

    best_score = WIN_SCORE
    for move in moves:
        score = alphabeta(
            apply_move(board, state.color, move),
            maximizing_color=maximizing_color,
            state=SearchState(
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


def evaluate_board(board: Board, color: Cell) -> int:
    """Return a heuristic score for a board."""
    other_color = opponent(color)
    color_moves = valid_moves(board, color)
    other_moves = valid_moves(board, other_color)

    if not color_moves and not other_moves:
        score_difference = count_cell(board, color) - count_cell(board, other_color)
        if score_difference > 0:
            return WIN_SCORE
        if score_difference < 0:
            return -WIN_SCORE
        return 0

    return (
        weighted_cells(board, color)
        - weighted_cells(board, other_color)
        + (len(color_moves) - len(other_moves)) * MOBILITY_WEIGHT
        + (corner_count(board, color) - corner_count(board, other_color))
        * CORNER_BONUS
        + (count_cell(board, color) - count_cell(board, other_color)) * DISC_WEIGHT
    )


def weighted_cells(board: Board, color: Cell) -> int:
    """Return the weighted position score for one color."""
    return sum(
        POSITION_WEIGHTS[row][col]
        for row, line in enumerate(board)
        for col, cell in enumerate(line)
        if cell == color
    )


def corner_count(board: Board, color: Cell) -> int:
    """Return how many corners one color owns."""
    return sum(1 for row, col in CORNERS if board[row][col] == color)


def count_cell(board: Board, color: Cell) -> int:
    """Return how many cells one color owns."""
    return sum(row.count(color) for row in board)


def valid_moves(board: Board, color: Cell) -> list[Move]:
    """Return all valid moves for one color."""
    return [
        (row, col)
        for row, line in enumerate(board)
        for col, _ in enumerate(line)
        if flips_for(board, color, (row, col))
    ]


def apply_move(board: Board, color: Cell, move: Move) -> Board:
    """Return a copied board after applying one move."""
    next_board = [row.copy() for row in board]
    row, col = move
    next_board[row][col] = color
    for flip_row, flip_col in flips_for(board, color, move):
        next_board[flip_row][flip_col] = color
    return next_board


def flips_for(board: Board, color: Cell, move: Move) -> list[Move]:
    """Return cells flipped by one move."""
    row, col = move
    if not is_on_board(board, row, col):
        return []
    if board[row][col] != Cell.EMPTY:
        return []

    flips = []
    for row_step, col_step in DIRECTIONS:
        flips.extend(
            flips_in_direction(board, color, move, (row_step, col_step))
        )
    return flips


def flips_in_direction(
    board: Board,
    color: Cell,
    move: Move,
    direction: Move,
) -> list[Move]:
    """Return cells flipped by one move in one direction."""
    flips = []
    other_color = opponent(color)
    row, col = move
    row_step, col_step = direction
    current_row = row + row_step
    current_col = col + col_step

    while is_on_board(board, current_row, current_col):
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


def is_on_board(board: Board, row: int, col: int) -> bool:
    """Return whether a coordinate is on the board."""
    return 0 <= row < len(board) and 0 <= col < len(board[row])
