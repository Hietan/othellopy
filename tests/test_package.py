"""Package behavior tests."""

import random
from io import StringIO

import pytest

from othellopy import __version__, validation
from othellopy.board import (
    board_to_html,
    board_to_str,
    copy_board,
    display_board,
    initial_board,
)
from othellopy.core import Board, Cell
from othellopy.game import GameResult, OthelloGame
from othellopy.players import (
    AdvancedPlayer,
    BasePlayer,
    BeginnerPlayer,
    IntermediatePlayer,
    ManualPlayer,
)
from othellopy.validation import validate, validate_detail

BOARD_SIZE = 8
INITIAL_OCCUPIED_CELL_COUNT = 4
CELL_VALUES = {
    Cell.EMPTY: 0,
    Cell.BLACK: 1,
    Cell.WHITE: 2,
}
INITIAL_BLACK_MOVES = [(2, 3), (3, 2), (4, 5), (5, 4)]
INITIAL_WHITE_MOVES = [(2, 4), (3, 5), (4, 2), (5, 3)]


class FirstMovePlayer(BasePlayer):
    """Player that picks the first valid move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Return the first available move."""
        return self.get_moves(board)[0]


class LastMovePlayer(BasePlayer):
    """Player that picks the last valid move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Return the last available move."""
        return self.get_moves(board)[-1]


class InvalidMovePlayer(BasePlayer):
    """Player that always returns an occupied move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, _board: Board) -> tuple[int, int]:
        """Return an invalid move."""
        return (0, 0)


class BrokenMovePlayer(BasePlayer):
    """Player that returns a malformed move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, _board: Board) -> object:
        """Return an object that is not a move."""
        return None


class PrintingPlayer(BasePlayer):
    """Player that prints while choosing a move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Print before returning a move."""
        print("debug")  # noqa: T201
        return self.get_moves(board)[0]


class DisplayingPlayer(BasePlayer):
    """Player that displays the board while choosing a move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Display the board before returning a move."""
        display_board(board, use_emoji=False)
        return self.get_moves(board)[0]


class MutatingPlayer(BasePlayer):
    """Player that mutates the board while choosing a move."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Mutate the board before returning a move."""
        moves = self.get_moves(board)
        board[0][0] = Cell.BLACK
        return moves[0]


class ExternalImportPlayer(BasePlayer):
    """Player that imports an external package."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Use a disallowed external import."""
        import numpy as np  # noqa: PLC0415

        _ = np.array([1])
        return self.get_moves(board)[0]


class RandomPlayer(BasePlayer):
    """Player that uses an allowed standard library module."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Use random from the standard library."""
        return random.choice(self.get_moves(board))  # noqa: S311


def test_version() -> None:
    """Expose the package version."""
    assert __version__ == "0.2.2"


def test_cell_values() -> None:
    """Define stable cell enum values."""
    assert {
        Cell.EMPTY: int(Cell.EMPTY),
        Cell.BLACK: int(Cell.BLACK),
        Cell.WHITE: int(Cell.WHITE),
    } == CELL_VALUES


def test_base_player_cannot_be_created_directly() -> None:
    """Keep BasePlayer abstract."""
    with pytest.raises(TypeError):
        BasePlayer(Cell.BLACK)


def test_player_sets_colors() -> None:
    """Set player and opponent colors during initialization."""
    player = FirstMovePlayer(Cell.BLACK)

    assert player.color == Cell.BLACK
    assert player.opponent_color == Cell.WHITE


def test_empty_color_is_rejected() -> None:
    """Reject empty cells as player colors."""
    with pytest.raises(ValueError, match=r"color must be Cell\.BLACK or Cell\.WHITE"):
        FirstMovePlayer(Cell.EMPTY)


def test_black_moves_from_initial_board() -> None:
    """Find the legal black moves from the initial board."""
    player = FirstMovePlayer(Cell.BLACK)

    assert player.get_moves(initial_board()) == INITIAL_BLACK_MOVES


def test_white_moves_from_initial_board() -> None:
    """Find the legal white moves from the initial board."""
    player = FirstMovePlayer(Cell.WHITE)

    assert player.get_moves(initial_board()) == INITIAL_WHITE_MOVES


def test_get_flips_for_valid_move() -> None:
    """Return flipped cells for a valid move."""
    player = FirstMovePlayer(Cell.BLACK)

    assert player.get_flips(initial_board(), 2, 3) == [(3, 3)]


def test_invalid_moves_return_false() -> None:
    """Report invalid moves as false."""
    player = FirstMovePlayer(Cell.BLACK)
    board = initial_board()

    assert not player.is_valid_move(board, 3, 3)
    assert not player.is_valid_move(board, 0, 0)
    assert not player.is_valid_move(board, -1, 0)


def test_next_move_returns_first_valid_move() -> None:
    """Return the first valid move from FirstMovePlayer."""
    player = FirstMovePlayer(Cell.BLACK)

    assert player.next_move(initial_board()) == (2, 3)


def test_board_helpers() -> None:
    """Create, copy, and render boards."""
    board = initial_board()
    board_copy = copy_board(board)

    assert board_copy == board
    assert board_copy is not board
    assert board_copy[0] is not board[0]
    assert board_to_str(board, use_emoji=True).splitlines()[4] == "3 . . . ⚪️ ⚫️ . . ."
    assert board_to_str(board, use_emoji=False).splitlines()[4] == "3 . . . W B . . ."


def test_board_to_html_uses_fixed_cells() -> None:
    """Render a fixed-cell HTML table for notebook display."""
    html = board_to_html(initial_board(), use_emoji=True)

    assert html.startswith('<table role="grid" aria-label="Othello board"')
    assert "table-layout:fixed;" in html
    assert "width:2.25em;" in html
    assert "font-family:Arial," in html
    assert "⚪️" in html
    assert "⚫️" in html
    assert html.count("<tr>") == BOARD_SIZE + 1
    assert html.count("<td") == BOARD_SIZE * BOARD_SIZE


def test_board_to_html_can_disable_emoji() -> None:
    """Render an ASCII fallback HTML table when emoji are disabled."""
    html = board_to_html(initial_board(), use_emoji=False)

    assert "W" in html
    assert "B" in html
    assert "⚪️" not in html
    assert "⚫️" not in html


def test_game_returns_result() -> None:
    """Play a game and return a populated result."""
    result = OthelloGame(FirstMovePlayer, LastMovePlayer).play()

    assert isinstance(result, GameResult)
    assert result.winner in (Cell.EMPTY, Cell.BLACK, Cell.WHITE)
    assert result.black_score + result.white_score <= BOARD_SIZE * BOARD_SIZE
    assert result.black_score + result.white_score > INITIAL_OCCUPIED_CELL_COUNT
    assert result.moves[0] == (Cell.BLACK, 2, 3)
    assert result.turns[0].color == Cell.BLACK
    assert result.turns[0].valid_moves == INITIAL_BLACK_MOVES
    assert result.turns[0].move == (2, 3)


def test_game_ends_with_no_valid_moves() -> None:
    """Stop the game once neither player has valid moves."""
    result = OthelloGame(FirstMovePlayer, FirstMovePlayer).play()
    black_player = FirstMovePlayer(Cell.BLACK)
    white_player = FirstMovePlayer(Cell.WHITE)

    assert black_player.get_moves(result.board) == []
    assert white_player.get_moves(result.board) == []


def test_game_forfeits_invalid_move() -> None:
    """Declare the opponent as winner when a player returns an illegal move."""
    result = OthelloGame(InvalidMovePlayer, FirstMovePlayer).play()

    assert result.winner == Cell.WHITE
    assert result.forfeit is not None
    assert result.forfeit.color == Cell.BLACK
    assert result.forfeit.move == (0, 0)
    assert result.forfeit.valid_moves == INITIAL_BLACK_MOVES
    assert "Valid moves:" in result.forfeit.message
    assert "0 1 2 3 4 5 6 7" in result.forfeit.message


def test_game_forfeits_broken_move_shape() -> None:
    """Declare the opponent as winner when a player returns an invalid shape."""
    result = OthelloGame(BrokenMovePlayer, FirstMovePlayer).play()

    assert result.winner == Cell.WHITE
    assert result.forfeit is not None
    assert result.forfeit.color == Cell.BLACK
    assert result.forfeit.move is None
    assert result.forfeit.valid_moves == INITIAL_BLACK_MOVES
    assert "Valid moves:" in result.forfeit.message


def test_beginner_player_returns_legal_move() -> None:
    """Choose one legal move randomly."""
    player = BeginnerPlayer(Cell.BLACK, seed=0)
    board = initial_board()

    assert player.next_move(board) in INITIAL_BLACK_MOVES


def test_intermediate_player_prefers_corner() -> None:
    """Prefer a corner when the heuristic makes it available."""
    player = IntermediatePlayer(Cell.BLACK)
    board = [[Cell.WHITE for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[0][0] = Cell.EMPTY
    board[0][1] = Cell.WHITE
    board[0][2] = Cell.BLACK
    board[7][7] = Cell.EMPTY

    assert player.next_move(board) == (0, 0)


def test_advanced_player_returns_legal_move() -> None:
    """Choose a legal move with alpha-beta search."""
    player = AdvancedPlayer(Cell.BLACK)
    board = initial_board()

    assert player.next_move(board) in INITIAL_BLACK_MOVES


def test_manual_player_reads_row_then_column() -> None:
    """Read manual moves as row then column."""
    output = StringIO()
    player = ManualPlayer(
        Cell.BLACK,
        input_func=lambda _prompt: "23",
        output=output,
        use_emoji=False,
    )

    assert player.next_move(initial_board()) == (2, 3)
    assert "BLACK to move" in output.getvalue()
    assert "Valid moves: 23, 32, 45, 54" in output.getvalue()


def test_manual_player_retries_invalid_input() -> None:
    """Keep asking until a manual move is valid."""
    moves = iter(["99", "23"])
    output = StringIO()
    player = ManualPlayer(
        Cell.BLACK,
        input_func=lambda _prompt: next(moves),
        output=output,
        use_emoji=False,
    )

    assert player.next_move(initial_board()) == (2, 3)
    assert "Invalid move: '99'" in output.getvalue()


def test_validate_accepts_valid_player() -> None:
    """Accept a valid submitted player."""
    assert validate(FirstMovePlayer)


def test_validate_allows_standard_library_imports() -> None:
    """Allow safe standard library imports such as random."""
    assert validate(RandomPlayer)


def test_validate_rejects_invalid_move_player() -> None:
    """Reject players that return illegal moves."""
    result = validate_detail(InvalidMovePlayer)

    assert not result.passed
    assert result.errors[0].code == "illegal-move"


def test_validate_allows_print_output() -> None:
    """Allow players to print while debugging in notebooks."""
    assert validate(PrintingPlayer)


def test_validate_allows_display_board() -> None:
    """Allow players to display boards while debugging in notebooks."""
    assert validate(DisplayingPlayer)


def test_validate_allows_board_mutation_on_copied_board() -> None:
    """Allow board mutation because validation passes an isolated board copy."""
    assert validate(MutatingPlayer)


def test_validate_warns_when_source_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Continue runtime checks when source inspection fails in notebooks."""

    def raise_os_error(_obj: object) -> str:
        raise OSError

    monkeypatch.setattr(validation.inspect, "getsource", raise_os_error)

    result = validate_detail(FirstMovePlayer)

    assert result.passed
    assert any(issue.code == "source-unavailable" for issue in result.warnings)


def test_validate_rejects_external_packages() -> None:
    """Reject external package imports such as numpy."""
    result = validate_detail(ExternalImportPlayer)

    assert not result.passed
    assert any(issue.code == "external-module" for issue in result.errors)
