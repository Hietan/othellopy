"""Manual CLI player."""

import sys
from collections.abc import Callable
from typing import TextIO

from othellopy.board import board_to_str
from othellopy.core import Board, Cell, Move
from othellopy.players.base import BasePlayer

_MOVE_INPUT_LENGTH = 2


class ManualPlayer(BasePlayer):
    """Manual player that asks for moves in a CLI."""

    def __init__(
        self,
        color: Cell,
        *,
        input_func: Callable[[str], str] = input,
        output: TextIO | None = None,
        use_emoji: bool | None = None,
    ) -> None:
        """Initialize a manual player with optional IO overrides."""
        super().__init__(color)
        self._input = input_func
        self._output = output
        self._use_emoji = use_emoji

    def next_move(self, board: Board) -> Move:
        """Ask for a move as row then column, such as 07."""
        valid_moves = self.get_moves(board)
        self._write_turn(board, valid_moves)

        while True:
            raw_move = self._input("move row-col (example: 07): ").strip()
            move = _parse_move(raw_move)
            if move in valid_moves:
                return move

            self._write(f"Invalid move: {raw_move!r}\n")
            self._write(f"Valid moves: {_format_moves(valid_moves)}\n")

    def _write_turn(self, board: Board, valid_moves: list[Move]) -> None:
        self._write(f"{self.color.name} to move\n")
        self._write(f"{board_to_str(board, use_emoji=self._use_emoji)}\n")
        self._write(f"Valid moves: {_format_moves(valid_moves)}\n")

    def _write(self, message: str) -> None:
        output = sys.stdout if self._output is None else self._output
        output.write(message)


def _parse_move(raw_move: str) -> Move | None:
    if len(raw_move) != _MOVE_INPUT_LENGTH:
        return None
    if not raw_move.isdecimal():
        return None

    return int(raw_move[0]), int(raw_move[1])


def _format_moves(moves: list[Move]) -> str:
    return ", ".join(f"{row}{col}" for row, col in moves)
