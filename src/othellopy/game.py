"""Game runner for Othello/Reversi players."""

from dataclasses import dataclass

from othellopy.board import board_to_str, copy_board, initial_board
from othellopy.core import Board, Piece
from othellopy.player import BasePlayer

_MAX_CONSECUTIVE_PASSES = 2
_MOVE_LENGTH = 2

MoveRecord = tuple[Piece, int, int]


@dataclass(frozen=True)
class TurnRecord:
    """Information about one turn for debugging."""

    color: Piece
    board: Board
    valid_moves: list[tuple[int, int]]
    move: tuple[int, int] | None
    black_score: int
    white_score: int


@dataclass(frozen=True)
class GameResult:
    """Result returned after playing one game."""

    winner: Piece
    black_score: int
    white_score: int
    board: Board
    moves: list[MoveRecord]
    turns: list[TurnRecord]


class InvalidMoveError(ValueError):
    """Raised when a player returns a move that is not valid."""

    def __init__(
        self,
        color: Piece,
        move: object,
        valid_moves: list[tuple[int, int]],
        board: Board,
    ) -> None:
        """Build an error describing the rejected move."""
        self.color = color
        self.move = move
        self.valid_moves = valid_moves
        self.board = copy_board(board)
        message = (
            f"{color.name} player returned invalid move: {move!r}\n"
            f"Valid moves: {valid_moves}\n"
            f"{board_to_str(board)}"
        )
        super().__init__(message)


class OthelloGame:
    """Play one Othello game between two player classes."""

    def __init__(
        self,
        black_player_class: type[BasePlayer],
        white_player_class: type[BasePlayer],
    ) -> None:
        """Initialize black and white players from their classes."""
        self.black_player = black_player_class(Piece.BLACK)
        self.white_player = white_player_class(Piece.WHITE)

    def play(self) -> GameResult:
        """Play until both players have no valid moves."""
        board = initial_board()
        moves = []
        turns = []
        current_color = Piece.BLACK
        pass_count = 0

        while pass_count < _MAX_CONSECUTIVE_PASSES:
            player = self._player_for(current_color)
            valid_moves = player.get_moves(board)

            if not valid_moves:
                turns.append(_turn_record(current_color, board, valid_moves, None))
                pass_count += 1
                current_color = _next_color(current_color)
                continue

            pass_count = 0
            move = player.next_move(copy_board(board))
            if not _is_move(move):
                raise InvalidMoveError(current_color, move, valid_moves, board)

            row, col = move
            if not player.is_valid_move(board, row, col):
                raise InvalidMoveError(current_color, move, valid_moves, board)

            _place_piece(board, player, row, col)
            moves.append((current_color, row, col))
            turns.append(_turn_record(current_color, board, valid_moves, move))
            current_color = _next_color(current_color)

        black_score = _count_piece(board, Piece.BLACK)
        white_score = _count_piece(board, Piece.WHITE)
        return GameResult(
            winner=_winner(black_score, white_score),
            black_score=black_score,
            white_score=white_score,
            board=copy_board(board),
            moves=moves,
            turns=turns,
        )

    def _player_for(self, color: Piece) -> BasePlayer:
        if color == Piece.BLACK:
            return self.black_player
        return self.white_player


def _place_piece(board: Board, player: BasePlayer, row: int, col: int) -> None:
    flips = player.get_flips(board, row, col)
    board[row][col] = player.color
    for flip_row, flip_col in flips:
        board[flip_row][flip_col] = player.color


def _next_color(color: Piece) -> Piece:
    if color == Piece.BLACK:
        return Piece.WHITE
    return Piece.BLACK


def _count_piece(board: Board, piece: Piece) -> int:
    return sum(row.count(piece) for row in board)


def _winner(black_score: int, white_score: int) -> Piece:
    if black_score > white_score:
        return Piece.BLACK
    if white_score > black_score:
        return Piece.WHITE
    return Piece.EMPTY


def _is_move(move: object) -> bool:
    if not isinstance(move, tuple | list):
        return False
    if len(move) != _MOVE_LENGTH:
        return False
    row, col = move
    return isinstance(row, int) and isinstance(col, int)


def _turn_record(
    color: Piece,
    board: Board,
    valid_moves: list[tuple[int, int]],
    move: tuple[int, int] | None,
) -> TurnRecord:
    return TurnRecord(
        color=color,
        board=copy_board(board),
        valid_moves=valid_moves.copy(),
        move=move,
        black_score=_count_piece(board, Piece.BLACK),
        white_score=_count_piece(board, Piece.WHITE),
    )
