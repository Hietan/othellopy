from othellopy import __version__
from othellopy.core import Piece
from othellopy.game import GameResult, OthelloGame
from othellopy.player import BasePlayer


class FirstMovePlayer(BasePlayer):
    def __init__(self, color: Piece) -> None:
        super().__init__(color)

    def next_move(self, board: list[list[Piece]]) -> tuple[int, int]:
        return self.get_moves(board)[0]


class LastMovePlayer(BasePlayer):
    def __init__(self, color: Piece) -> None:
        super().__init__(color)

    def next_move(self, board: list[list[Piece]]) -> tuple[int, int]:
        return self.get_moves(board)[-1]


class InvalidMovePlayer(BasePlayer):
    def __init__(self, color: Piece) -> None:
        super().__init__(color)

    def next_move(self, board: list[list[Piece]]) -> tuple[int, int]:
        return (0, 0)


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_piece_values() -> None:
    assert Piece.EMPTY == 0
    assert Piece.BLACK == 1
    assert Piece.WHITE == 2


def test_base_player_cannot_be_created_directly() -> None:
    try:
        BasePlayer(Piece.BLACK)
    except TypeError:
        return

    raise AssertionError("BasePlayer should be abstract")


def test_player_sets_colors() -> None:
    player = FirstMovePlayer(Piece.BLACK)

    assert player.color == Piece.BLACK
    assert player.opponent_color == Piece.WHITE


def test_empty_color_is_rejected() -> None:
    try:
        FirstMovePlayer(Piece.EMPTY)
    except ValueError:
        return

    raise AssertionError("Piece.EMPTY should not be accepted as a player color")


def test_black_moves_from_initial_board() -> None:
    player = FirstMovePlayer(Piece.BLACK)

    assert set(player.get_moves(_initial_board())) == {
        (2, 3),
        (3, 2),
        (4, 5),
        (5, 4),
    }


def test_white_moves_from_initial_board() -> None:
    player = FirstMovePlayer(Piece.WHITE)

    assert set(player.get_moves(_initial_board())) == {
        (2, 4),
        (3, 5),
        (4, 2),
        (5, 3),
    }


def test_get_flips_for_valid_move() -> None:
    player = FirstMovePlayer(Piece.BLACK)

    assert player.get_flips(_initial_board(), 2, 3) == [(3, 3)]


def test_invalid_moves_return_false() -> None:
    player = FirstMovePlayer(Piece.BLACK)
    board = _initial_board()

    assert not player.is_valid_move(board, 3, 3)
    assert not player.is_valid_move(board, 0, 0)
    assert not player.is_valid_move(board, -1, 0)


def test_next_move_returns_first_valid_move() -> None:
    player = FirstMovePlayer(Piece.BLACK)

    assert player.next_move(_initial_board()) == (2, 3)


def test_game_returns_result() -> None:
    result = OthelloGame(FirstMovePlayer, LastMovePlayer).play()

    assert isinstance(result, GameResult)
    assert result.winner in (Piece.EMPTY, Piece.BLACK, Piece.WHITE)
    assert result.black_score + result.white_score <= 64
    assert result.black_score + result.white_score > 4
    assert result.moves[0] == (Piece.BLACK, 2, 3)


def test_game_ends_with_no_valid_moves() -> None:
    result = OthelloGame(FirstMovePlayer, FirstMovePlayer).play()
    black_player = FirstMovePlayer(Piece.BLACK)
    white_player = FirstMovePlayer(Piece.WHITE)

    assert black_player.get_moves(result.board) == []
    assert white_player.get_moves(result.board) == []


def test_game_rejects_invalid_move() -> None:
    try:
        OthelloGame(InvalidMovePlayer, FirstMovePlayer).play()
    except ValueError:
        return

    raise AssertionError("invalid moves should raise ValueError")


def _initial_board() -> list[list[Piece]]:
    board = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = Piece.WHITE
    board[3][4] = Piece.BLACK
    board[4][3] = Piece.BLACK
    board[4][4] = Piece.WHITE
    return board
