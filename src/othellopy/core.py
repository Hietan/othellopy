"""Core definitions for Othello/Reversi."""

from enum import IntEnum


class Cell(IntEnum):
    """Board cell values used by othellopy."""

    EMPTY = 0
    BLACK = 1
    WHITE = 2


Board = list[list[Cell]]
Move = tuple[int, int]


def opponent(cell: Cell) -> Cell:
    """Return the opponent color for a player cell value."""
    cell = Cell(cell)
    if cell == Cell.BLACK:
        return Cell.WHITE
    if cell == Cell.WHITE:
        return Cell.BLACK
    msg = "cell must be Cell.BLACK or Cell.WHITE"
    raise ValueError(msg)
