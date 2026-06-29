"""Beginner sample player."""

from random import Random

from othellopy.core import Board, Cell, Move
from othellopy.player import BasePlayer


class BeginnerPlayer(BasePlayer):
    """Beginner sample player that chooses a legal move randomly."""

    def __init__(self, color: Cell, *, seed: int | None = None) -> None:
        """Initialize the player with an optional random seed."""
        super().__init__(color)
        self._random = Random(seed)  # noqa: S311

    def next_move(self, board: Board) -> Move:
        """Return a random legal move."""
        return self._random.choice(self.get_moves(board))
