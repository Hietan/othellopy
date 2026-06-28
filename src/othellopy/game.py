"""Game runner for Othello/Reversi players."""

from dataclasses import dataclass

from othellopy.core import Piece
from othellopy.player import BasePlayer, Board

MoveRecord = tuple[Piece, int, int]


@dataclass(frozen=True)
class GameResult:
    """Result returned after playing one game."""

    winner: Piece
    black_score: int
    white_score: int
    board: Board
    moves: list[MoveRecord]


class OthelloGame:
    """Play one Othello game between two player classes."""

    def __init__(
        self,
        black_player_class: type[BasePlayer],
        white_player_class: type[BasePlayer],
    ) -> None:
        self.black_player = black_player_class(Piece.BLACK)
        self.white_player = white_player_class(Piece.WHITE)

    def play(self) -> GameResult:
        """Play until both players have no valid moves."""
        board = _initial_board()
        moves = []
        current_color = Piece.BLACK
        pass_count = 0

        while pass_count < 2:
            player = self._player_for(current_color)
            valid_moves = player.get_moves(board)

            if not valid_moves:
                pass_count += 1
                current_color = _next_color(current_color)
                continue

            pass_count = 0
            row, col = player.next_move(_copy_board(board))
            if not player.is_valid_move(board, row, col):
                move = (row, col)
                msg = f"{current_color.name} player returned invalid move: {move!r}"
                raise ValueError(msg)

            _place_piece(board, player, row, col)
            moves.append((current_color, row, col))
            current_color = _next_color(current_color)

        black_score = _count_piece(board, Piece.BLACK)
        white_score = _count_piece(board, Piece.WHITE)
        return GameResult(
            winner=_winner(black_score, white_score),
            black_score=black_score,
            white_score=white_score,
            board=_copy_board(board),
            moves=moves,
        )

    def _player_for(self, color: Piece) -> BasePlayer:
        if color == Piece.BLACK:
            return self.black_player
        return self.white_player


def _initial_board() -> Board:
    board = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = Piece.WHITE
    board[3][4] = Piece.BLACK
    board[4][3] = Piece.BLACK
    board[4][4] = Piece.WHITE
    return board


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


def _copy_board(board: Board) -> Board:
    return [row.copy() for row in board]
