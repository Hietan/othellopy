"""Advanced sample player."""

from othellopy.core import Board, Cell, Move
from othellopy.player import BasePlayer
from othellopy.players._logic import (
    MIN_SEARCH_DEPTH,
    SEARCH_DEPTH,
    WIN_SCORE,
    SearchState,
    alphabeta,
    apply_move,
)


class AdvancedPlayer(BasePlayer):
    """Advanced sample player that searches with alpha-beta pruning."""

    def __init__(self, color: Cell, *, depth: int = SEARCH_DEPTH) -> None:
        """Initialize the player color and search depth."""
        super().__init__(color)
        if depth < MIN_SEARCH_DEPTH:
            msg = "depth must be at least 1"
            raise ValueError(msg)

        self.depth = depth

    def next_move(self, board: Board) -> Move:
        """Return the legal move with the best alpha-beta search score."""
        moves = self.get_moves(board)
        return max(moves, key=lambda move: self._score_move(board, move))

    def _score_move(self, board: Board, move: Move) -> int:
        next_board = apply_move(board, self.color, move)
        return alphabeta(
            next_board,
            maximizing_color=self.color,
            state=SearchState(
                color=self.opponent_color,
                depth=self.depth - 1,
                alpha=-WIN_SCORE,
                beta=WIN_SCORE,
                pass_count=0,
            ),
        )
