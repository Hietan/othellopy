"""Core definitions for Othello/Reversi."""

from enum import IntEnum


class Piece(IntEnum):
    """Board cell values used by othellopy."""

    EMPTY = 0
    BLACK = 1
    WHITE = 2


def opponent(piece: Piece) -> Piece:
    """Return the opponent color for a player piece."""
    piece = Piece(piece)
    if piece == Piece.BLACK:
        return Piece.WHITE
    if piece == Piece.WHITE:
        return Piece.BLACK
    msg = "piece must be Piece.BLACK or Piece.WHITE"
    raise ValueError(msg)
