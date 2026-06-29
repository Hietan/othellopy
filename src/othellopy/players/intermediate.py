"""Intermediate sample player."""

from othellopy.core import Board, Cell, Move
from othellopy.player import BasePlayer
from othellopy.players._logic import (
    DISC_WEIGHT,
    MOBILITY_WEIGHT,
    POSITION_WEIGHTS,
    apply_move,
    flips_for,
    valid_moves,
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
        next_board = apply_move(board, self.color, move)
        return (
            POSITION_WEIGHTS[row][col]
            + len(flips_for(board, self.color, move)) * DISC_WEIGHT
            - len(valid_moves(next_board, self.opponent_color)) * MOBILITY_WEIGHT
        )
