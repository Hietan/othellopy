"""Board helpers for Othello/Reversi exercises."""

import sys

from othellopy.core import Board, Cell


def initial_board() -> Board:
    """Return the standard initial Othello board."""
    board = [[Cell.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = Cell.WHITE
    board[3][4] = Cell.BLACK
    board[4][3] = Cell.BLACK
    board[4][4] = Cell.WHITE
    return board


def copy_board(board: Board) -> Board:
    """Return a shallow row-by-row copy of a board."""
    return [row.copy() for row in board]


def board_to_str(board: Board) -> str:
    """Return a readable board string for notebooks and debugging."""
    lines = ["  0 1 2 3 4 5 6 7"]
    for row_number, row in enumerate(board):
        cells = " ".join(_cell_to_mark(cell) for cell in row)
        lines.append(f"{row_number} {cells}")
    return "\n".join(lines)


def print_board(board: Board) -> None:
    """Print a readable board for notebooks and debugging."""
    sys.stdout.write(f"{board_to_str(board)}\n")


def _cell_to_mark(cell: Cell) -> str:
    cell = Cell(cell)
    if cell == Cell.BLACK:
        return "B"
    if cell == Cell.WHITE:
        return "W"
    return "."
