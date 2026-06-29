"""Board helpers for Othello/Reversi exercises."""

import sys

from othellopy.core import Board, Piece


def initial_board() -> Board:
    """Return the standard initial Othello board."""
    board = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = Piece.WHITE
    board[3][4] = Piece.BLACK
    board[4][3] = Piece.BLACK
    board[4][4] = Piece.WHITE
    return board


def copy_board(board: Board) -> Board:
    """Return a shallow row-by-row copy of a board."""
    return [row.copy() for row in board]


def board_to_str(board: Board) -> str:
    """Return a readable board string for notebooks and debugging."""
    lines = ["  0 1 2 3 4 5 6 7"]
    for row_number, row in enumerate(board):
        cells = " ".join(_piece_to_mark(piece) for piece in row)
        lines.append(f"{row_number} {cells}")
    return "\n".join(lines)


def print_board(board: Board) -> None:
    """Print a readable board for notebooks and debugging."""
    sys.stdout.write(f"{board_to_str(board)}\n")


def _piece_to_mark(piece: Piece) -> str:
    piece = Piece(piece)
    if piece == Piece.BLACK:
        return "B"
    if piece == Piece.WHITE:
        return "W"
    return "."
