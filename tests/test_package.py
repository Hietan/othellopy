"""Package behavior tests."""

import random
import time
from io import StringIO

import pytest

from othellopy import __version__
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
from othellopy.validation import (
    test_player as player_test,
)
from othellopy.validation import (
    test_player_detail as player_test_detail,
)
from othellopy.validation import (
    validate,
    validate_detail,
)

BOARD_SIZE = 8
INITIAL_OCCUPIED_CELL_COUNT = 4
DEFAULT_MOVE_TIMEOUT_SECONDS = 2.0
CELL_VALUES = {
    Cell.EMPTY: 0,
    Cell.BLACK: 1,
    Cell.WHITE: 2,
}
INITIAL_BLACK_MOVES = [(2, 3), (3, 2), (4, 5), (5, 4)]
INITIAL_WHITE_MOVES = [(2, 4), (3, 5), (4, 2), (5, 3)]


def board_from_rows(rows: list[str]) -> Board:
    """Create a board from strings using '.', 'B', and 'W'."""
    cells = {
        ".": Cell.EMPTY,
        "B": Cell.BLACK,
        "W": Cell.WHITE,
    }
    return [[cells[mark] for mark in row] for row in rows]


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


class NoInitPlayer(BasePlayer):
    """Player that relies on BasePlayer.__init__."""

    def next_move(self, board: Board) -> tuple[int, int]:
        """Return the first available move."""
        return self.get_moves(board)[0]


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

    def next_move(self, _board: Board) -> object:  # type: ignore[override]
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
        import numpy as np  # type: ignore[import-not-found] # noqa: PLC0415

        _ = np.array([1])
        return self.get_moves(board)[0]


class DormantExternalImportPlayer(BasePlayer):
    """Player that contains an external import in unreachable code."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Contain source that a static analyzer may reject."""
        if False:
            import numpy as np  # noqa: PLC0415

            _ = np.array([1])
        return self.get_moves(board)[0]


class RaisingPlayer(BasePlayer):
    """Player that raises during move selection."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, _board: Board) -> tuple[int, int]:
        """Raise a runtime error."""
        msg = "boom"
        raise RuntimeError(msg)


class SlowPlayer(BasePlayer):
    """Player that sleeps too long during move selection."""

    def __init__(self, color: Cell) -> None:
        """Initialize the player color."""
        super().__init__(color)

    def next_move(self, board: Board) -> tuple[int, int]:
        """Sleep before returning a move."""
        time.sleep(0.05)
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
    assert __version__ == "0.2.3"


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
        BasePlayer(Cell.BLACK)  # type: ignore[abstract]


def test_player_sets_colors() -> None:
    """Set player and opponent colors during initialization."""
    player = FirstMovePlayer(Cell.BLACK)

    assert player.color == Cell.BLACK
    assert player.opponent_color == Cell.WHITE


def test_player_can_inherit_base_init() -> None:
    """Allow simple players to implement only next_move."""
    player = NoInitPlayer(Cell.BLACK)

    assert player.color == Cell.BLACK
    assert player.opponent_color == Cell.WHITE
    assert player.next_move(initial_board()) == (2, 3)


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
    assert result.winner_name in ("BLACK", "WHITE", "DRAW")
    assert result.black_score + result.white_score <= BOARD_SIZE * BOARD_SIZE
    assert result.black_score + result.white_score > INITIAL_OCCUPIED_CELL_COUNT
    assert result.moves[0] == (Cell.BLACK, 2, 3)
    assert result.turns[0].color == Cell.BLACK
    assert result.turns[0].valid_moves == INITIAL_BLACK_MOVES
    assert result.turns[0].move == (2, 3)


def test_game_result_reports_readable_winner_names() -> None:
    """Provide display-friendly winner names."""
    assert (
        GameResult(
            winner=Cell.BLACK,
            black_score=1,
            white_score=0,
            board=[],
            moves=[],
            turns=[],
        ).winner_name
        == "BLACK"
    )
    assert (
        GameResult(
            winner=Cell.WHITE,
            black_score=0,
            white_score=1,
            board=[],
            moves=[],
            turns=[],
        ).winner_name
        == "WHITE"
    )
    assert (
        GameResult(
            winner=Cell.EMPTY,
            black_score=1,
            white_score=1,
            board=[],
            moves=[],
            turns=[],
        ).winner_name
        == "DRAW"
    )


def test_game_accepts_player_keyword_names() -> None:
    """Use black_player and white_player as the notebook-friendly keywords."""
    result = OthelloGame(
        black_player=FirstMovePlayer,
        white_player=LastMovePlayer,
    ).play()

    assert isinstance(result, GameResult)
    assert result.moves[0] == (Cell.BLACK, 2, 3)


def test_game_keeps_player_class_keyword_compatibility() -> None:
    """Keep the old keyword names working for existing notebooks."""
    result = OthelloGame(
        black_player_class=FirstMovePlayer,
        white_player_class=LastMovePlayer,
    ).play()

    assert isinstance(result, GameResult)
    assert result.moves[0] == (Cell.BLACK, 2, 3)


def test_game_rejects_duplicate_player_keywords() -> None:
    """Reject ambiguous player class arguments."""
    with pytest.raises(TypeError, match="black_player"):
        OthelloGame(
            FirstMovePlayer,
            LastMovePlayer,
            black_player_class=FirstMovePlayer,
        )


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


def test_game_forfeits_timeout() -> None:
    """Declare the opponent as winner when a player exceeds the move timeout."""
    result = OthelloGame(
        SlowPlayer,
        FirstMovePlayer,
        move_timeout_seconds=0.001,
    ).play()

    assert result.winner == Cell.WHITE
    assert result.forfeit is not None
    assert result.forfeit.color == Cell.BLACK
    assert result.forfeit.move is None
    assert result.forfeit.valid_moves == INITIAL_BLACK_MOVES
    assert "exceeded 0.001 seconds" in result.forfeit.message


def test_game_rejects_non_positive_timeout() -> None:
    """Require positive timeouts while allowing None to disable the limit."""
    with pytest.raises(ValueError, match="move_timeout_seconds"):
        OthelloGame(FirstMovePlayer, FirstMovePlayer, move_timeout_seconds=0)


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


def test_advanced_player_passes_two_second_runtime_check() -> None:
    """Keep AdvancedPlayer under the default two-second runtime limit."""
    result = player_test_detail(AdvancedPlayer)

    assert result.passed
    assert all(
        case["elapsed_seconds"] is not None
        and case["elapsed_seconds"] <= DEFAULT_MOVE_TIMEOUT_SECONDS
        for case in result.details["runtime_cases"]
    )


def test_advanced_player_stays_under_two_seconds_in_midgame() -> None:
    """Keep AdvancedPlayer fast enough on a wider midgame move set."""
    board = board_from_rows(
        [
            "........",
            "..W.....",
            ".BBW....",
            "..BBWW..",
            "...BBWW.",
            ".....W.W",
            ".....W..",
            ".....W..",
        ]
    )
    player = AdvancedPlayer(Cell.BLACK)

    start = time.perf_counter()
    move = player.next_move(board)
    elapsed = time.perf_counter() - start

    assert move in player.get_moves(board)
    assert elapsed <= DEFAULT_MOVE_TIMEOUT_SECONDS


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


def test_player_accepts_valid_player() -> None:
    """Accept a valid submitted player."""
    assert player_test(FirstMovePlayer)


def test_player_accepts_player_without_init() -> None:
    """Accept a player that inherits BasePlayer.__init__."""
    assert player_test(NoInitPlayer)


def test_player_allows_standard_library_imports() -> None:
    """Allow safe standard library imports such as random."""
    assert player_test(RandomPlayer)


def test_player_rejects_invalid_move_player() -> None:
    """Reject players that return illegal moves."""
    result = player_test_detail(InvalidMovePlayer)

    assert not result.passed
    assert result.errors[0].code == "illegal-move"


def test_player_allows_print_output() -> None:
    """Allow players to print while debugging in notebooks."""
    assert player_test(PrintingPlayer)


def test_player_allows_display_board() -> None:
    """Allow players to display boards while debugging in notebooks."""
    assert player_test(DisplayingPlayer)


def test_player_allows_board_mutation_on_copied_board() -> None:
    """Allow board mutation because tests pass an isolated board copy."""
    assert player_test(MutatingPlayer)


def test_player_reports_runtime_case_details() -> None:
    """Run a broad set of runtime board cases."""
    result = player_test_detail(FirstMovePlayer)

    assert result.passed
    case_names = {case["name"] for case in result.details["runtime_cases"]}
    assert {
        "initial-black",
        "initial-white",
        "black-corner",
        "white-corner",
        "black-edge",
        "white-edge",
        "black-multi-direction",
        "white-multi-direction",
        "black-single-move",
        "white-single-move",
        "black-late-game",
        "white-late-game",
    } <= case_names


def test_player_rejects_runtime_errors() -> None:
    """Reject players that raise during runtime tests."""
    result = player_test_detail(RaisingPlayer)

    assert not result.passed
    assert result.errors[0].code == "runtime-error"


def test_player_rejects_timeout() -> None:
    """Reject players that exceed the configured time limit."""
    result = player_test_detail(SlowPlayer, max_seconds=0.001)

    assert not result.passed
    assert result.errors[0].code == "timeout"


def test_player_does_not_perform_static_import_checks() -> None:
    """Leave import/package policy to the client-side static analyzer."""
    assert player_test(DormantExternalImportPlayer)


def test_validate_aliases_test_player() -> None:
    """Keep the old validation API as a compatibility alias."""
    assert validate(FirstMovePlayer) == player_test(FirstMovePlayer)
    assert validate_detail(FirstMovePlayer).passed
