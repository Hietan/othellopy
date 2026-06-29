"""Game runner for Othello/Reversi players."""

from dataclasses import dataclass

from othellopy.board import board_to_str, copy_board, initial_board
from othellopy.core import Board, Cell
from othellopy.players.base import BasePlayer

_MAX_CONSECUTIVE_PASSES = 2
_MOVE_LENGTH = 2

MoveRecord = tuple[Cell, int, int]
PlayerClass = type[BasePlayer]


@dataclass(frozen=True)
class TurnRecord:
    """Information about one turn for debugging."""

    color: Cell
    board: Board
    valid_moves: list[tuple[int, int]]
    move: tuple[int, int] | None
    black_score: int
    white_score: int


@dataclass(frozen=True)
class GameResult:
    """Result returned after playing one game."""

    winner: Cell
    black_score: int
    white_score: int
    board: Board
    moves: list[MoveRecord]
    turns: list[TurnRecord]
    forfeit: "ForfeitRecord | None" = None

    @property
    def winner_name(self) -> str:
        """Return a readable winner name: BLACK, WHITE, or DRAW."""
        if self.winner == Cell.BLACK:
            return "BLACK"
        if self.winner == Cell.WHITE:
            return "WHITE"
        return "DRAW"


@dataclass(frozen=True)
class ForfeitRecord:
    """Information about a forfeit caused by an invalid move."""

    color: Cell
    move: object
    valid_moves: list[tuple[int, int]]
    board: Board
    message: str


class OthelloGame:
    """Play one Othello game between two player classes."""

    def __init__(
        self,
        black_player: PlayerClass | None = None,
        white_player: PlayerClass | None = None,
        *,
        black_player_class: PlayerClass | None = None,
        white_player_class: PlayerClass | None = None,
    ) -> None:
        """Initialize black and white players from their classes."""
        black_player = _resolve_player_class(
            player=black_player,
            player_class=black_player_class,
            color_name="black",
        )
        white_player = _resolve_player_class(
            player=white_player,
            player_class=white_player_class,
            color_name="white",
        )
        self.black_player = black_player(Cell.BLACK)
        self.white_player = white_player(Cell.WHITE)

    def play(self) -> GameResult:
        """Play until both players have no valid moves."""
        board = initial_board()
        moves: list[MoveRecord] = []
        turns: list[TurnRecord] = []
        current_color = Cell.BLACK
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
                return _forfeit_result(
                    board,
                    moves,
                    turns,
                    _forfeit_record(board, current_color, move, valid_moves),
                )

            row, col = move
            if not player.is_valid_move(board, row, col):
                return _forfeit_result(
                    board,
                    moves,
                    turns,
                    _forfeit_record(board, current_color, move, valid_moves),
                )

            _place_cell(board, player, row, col)
            moves.append((current_color, row, col))
            turns.append(_turn_record(current_color, board, valid_moves, move))
            current_color = _next_color(current_color)

        black_score = _count_cell(board, Cell.BLACK)
        white_score = _count_cell(board, Cell.WHITE)
        return GameResult(
            winner=_winner(black_score, white_score),
            black_score=black_score,
            white_score=white_score,
            board=copy_board(board),
            moves=moves,
            turns=turns,
        )

    def _player_for(self, color: Cell) -> BasePlayer:
        if color == Cell.BLACK:
            return self.black_player
        return self.white_player


def _resolve_player_class(
    *,
    player: PlayerClass | None,
    player_class: PlayerClass | None,
    color_name: str,
) -> PlayerClass:
    if player is not None and player_class is not None:
        msg = f"Use either {color_name}_player or {color_name}_player_class, not both."
        raise TypeError(msg)
    resolved_player = player if player is not None else player_class
    if resolved_player is None:
        msg = f"{color_name}_player is required."
        raise TypeError(msg)
    return resolved_player


def _place_cell(board: Board, player: BasePlayer, row: int, col: int) -> None:
    flips = player.get_flips(board, row, col)
    board[row][col] = player.color
    for flip_row, flip_col in flips:
        board[flip_row][flip_col] = player.color


def _next_color(color: Cell) -> Cell:
    if color == Cell.BLACK:
        return Cell.WHITE
    return Cell.BLACK


def _count_cell(board: Board, cell: Cell) -> int:
    return sum(row.count(cell) for row in board)


def _winner(black_score: int, white_score: int) -> Cell:
    if black_score > white_score:
        return Cell.BLACK
    if white_score > black_score:
        return Cell.WHITE
    return Cell.EMPTY


def _forfeit_record(
    board: Board,
    color: Cell,
    move: object,
    valid_moves: list[tuple[int, int]],
) -> ForfeitRecord:
    message = (
        f"{color.name} player forfeited by returning invalid move: {move!r}\n"
        f"Valid moves: {valid_moves}\n"
        f"{board_to_str(board)}"
    )
    return ForfeitRecord(
        color=color,
        move=move,
        valid_moves=valid_moves.copy(),
        board=copy_board(board),
        message=message,
    )


def _forfeit_result(
    board: Board,
    moves: list[MoveRecord],
    turns: list[TurnRecord],
    forfeit: ForfeitRecord,
) -> GameResult:
    black_score = _count_cell(board, Cell.BLACK)
    white_score = _count_cell(board, Cell.WHITE)
    return GameResult(
        winner=_next_color(forfeit.color),
        black_score=black_score,
        white_score=white_score,
        board=copy_board(board),
        moves=moves.copy(),
        turns=turns.copy(),
        forfeit=forfeit,
    )


def _is_move(move: object) -> bool:
    if not isinstance(move, tuple | list):
        return False
    if len(move) != _MOVE_LENGTH:
        return False
    row, col = move
    return isinstance(row, int) and isinstance(col, int)


def _turn_record(
    color: Cell,
    board: Board,
    valid_moves: list[tuple[int, int]],
    move: tuple[int, int] | None,
) -> TurnRecord:
    return TurnRecord(
        color=color,
        board=copy_board(board),
        valid_moves=valid_moves.copy(),
        move=move,
        black_score=_count_cell(board, Cell.BLACK),
        white_score=_count_cell(board, Cell.WHITE),
    )
