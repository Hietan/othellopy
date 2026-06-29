"""Board helpers for Othello/Reversi exercises."""

import sys

from othellopy.core import Board, Cell

_EMOJI_MARKS = {
    Cell.EMPTY: ".",
    Cell.BLACK: "⚫️",
    Cell.WHITE: "⚪️",
}
_LETTER_MARKS = {
    Cell.EMPTY: ".",
    Cell.BLACK: "B",
    Cell.WHITE: "W",
}


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


def board_to_str(board: Board, *, use_emoji: bool | None = None) -> str:
    """Return a readable board string for notebooks and debugging."""
    marks = _EMOJI_MARKS if _should_use_emoji(use_emoji=use_emoji) else _LETTER_MARKS
    lines = ["  0 1 2 3 4 5 6 7"]
    for row_number, row in enumerate(board):
        cells = " ".join(_cell_to_mark(cell, marks) for cell in row)
        lines.append(f"{row_number} {cells}")
    return "\n".join(lines)


def print_board(board: Board, *, use_emoji: bool | None = None) -> None:
    """Print a readable board for notebooks and debugging."""
    sys.stdout.write(f"{board_to_str(board, use_emoji=use_emoji)}\n")


def _should_use_emoji(*, use_emoji: bool | None) -> bool:
    if use_emoji is not None:
        return use_emoji

    encoding = sys.stdout.encoding
    if encoding is None:
        return False

    try:
        "⚫️⚪️".encode(encoding)
    except UnicodeEncodeError:
        return False

    return True


def _cell_to_mark(cell: Cell, marks: dict[Cell, str]) -> str:
    return marks[Cell(cell)]
