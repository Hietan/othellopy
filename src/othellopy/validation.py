"""Runtime test helpers for student players."""

from __future__ import annotations

import contextlib
import inspect
import signal
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from othellopy.board import copy_board, initial_board
from othellopy.core import Board, Cell, Move
from othellopy.players.base import BasePlayer

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import FrameType

_DEFAULT_MAX_SECONDS = 1.0
_BOARD_SIZE = 8
_MOVE_LENGTH = 2


class ValidationSeverity(str, Enum):
    """Severity for a validation issue."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ValidationIssue:
    """One validation issue found in a submitted player."""

    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR


@dataclass(frozen=True)
class ValidationResult:
    """Detailed result returned by test_player_detail()."""

    passed: bool
    issues: list[ValidationIssue]
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Return issues that make validation fail."""
        return [
            issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR
        ]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Return non-fatal validation issues."""
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]


class _MoveTimeoutError(TimeoutError):
    """Raised when next_move takes too long."""


class _ReferencePlayer(BasePlayer):
    def __init__(self, color: Cell) -> None:
        super().__init__(color)

    def next_move(self, board: Board) -> Move:
        return self.get_moves(board)[0]


def validate(
    player_class: type[BasePlayer],
    *,
    max_seconds: float = _DEFAULT_MAX_SECONDS,
) -> bool:
    """
    Return True if player_class passes the runtime tests.

    Prefer test_player() for new course materials.
    """
    return test_player(player_class, max_seconds=max_seconds)


def validate_detail(
    player_class: type[BasePlayer],
    *,
    max_seconds: float = _DEFAULT_MAX_SECONDS,
) -> ValidationResult:
    """
    Return detailed runtime test results.

    Prefer test_player_detail() for new course materials.
    """
    return test_player_detail(player_class, max_seconds=max_seconds)


def _test_player(
    player_class: type[BasePlayer],
    *,
    max_seconds: float = _DEFAULT_MAX_SECONDS,
) -> bool:
    """Return True if player_class passes the runtime player tests."""
    return test_player_detail(player_class, max_seconds=max_seconds).passed


def _test_player_detail(
    player_class: type[BasePlayer],
    *,
    max_seconds: float = _DEFAULT_MAX_SECONDS,
) -> ValidationResult:
    """Return detailed runtime test results for player_class."""
    issues: list[ValidationIssue] = []
    details: dict[str, Any] = {
        "max_seconds": max_seconds,
        "validation_kind": "runtime_player_tests",
    }

    issues.extend(_validate_class_shape(player_class))
    if not _has_errors(issues):
        runtime_issues, runtime_details = _validate_runtime(
            player_class,
            max_seconds=max_seconds,
        )
        issues.extend(runtime_issues)
        details.update(runtime_details)

    return ValidationResult(
        passed=not _has_errors(issues),
        issues=issues,
        details=details,
    )


def _validate_class_shape(player_class: type[BasePlayer]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not inspect.isclass(player_class):
        return [
            ValidationIssue(
                "not-class",
                "test_player() expects a Player class, such as test_player(MyPlayer).",
            )
        ]

    if not issubclass(player_class, BasePlayer):
        issues.append(
            ValidationIssue(
                "not-base-player",
                "Player must inherit from othellopy.players.BasePlayer.",
            )
        )

    if "next_move" not in player_class.__dict__:
        issues.append(
            ValidationIssue(
                "missing-next-move",
                "Player must define next_move(self, board).",
            )
        )

    return issues


test_player = _test_player
test_player_detail = _test_player_detail
test_player.__test__ = False  # type: ignore[attr-defined]
test_player_detail.__test__ = False  # type: ignore[attr-defined]


def _validate_runtime(
    player_class: type[BasePlayer],
    *,
    max_seconds: float,
) -> tuple[list[ValidationIssue], dict[str, Any]]:
    issues: list[ValidationIssue] = []
    details: dict[str, Any] = {"runtime_cases": []}

    for color in (Cell.BLACK, Cell.WHITE):
        issue = _try_create_player(player_class, color)
        if issue is not None:
            issues.append(issue)

    if issues:
        return issues, details

    for case in _runtime_cases():
        issue, elapsed = _validate_runtime_case(
            player_class,
            case,
            max_seconds=max_seconds,
        )
        details["runtime_cases"].append(
            {
                "name": case.name,
                "color": case.color.name,
                "valid_moves": case.valid_moves,
                "elapsed_seconds": elapsed,
            }
        )
        if issue is not None:
            issues.append(issue)

    return issues, details


def _try_create_player(
    player_class: type[BasePlayer],
    color: Cell,
) -> ValidationIssue | None:
    try:
        player_class(color)
    except Exception as exc:  # noqa: BLE001
        return ValidationIssue(
            "init-failed",
            f"Player({color.name}) raised {type(exc).__name__}: {exc}.",
        )
    return None


@dataclass(frozen=True)
class _RuntimeCase:
    name: str
    color: Cell
    board: Board
    valid_moves: list[Move]


def _runtime_cases() -> list[_RuntimeCase]:
    cases = [
        _case("initial-black", Cell.BLACK, initial_board()),
        _case("initial-white", Cell.WHITE, initial_board()),
        _case("black-corner", Cell.BLACK, _corner_board(Cell.BLACK)),
        _case("white-corner", Cell.WHITE, _corner_board(Cell.WHITE)),
        _case("black-edge", Cell.BLACK, _edge_board(Cell.BLACK)),
        _case("white-edge", Cell.WHITE, _edge_board(Cell.WHITE)),
        _case("black-multi-direction", Cell.BLACK, _multi_direction_board(Cell.BLACK)),
        _case("white-multi-direction", Cell.WHITE, _multi_direction_board(Cell.WHITE)),
        _case("black-single-move", Cell.BLACK, _single_move_board(Cell.BLACK)),
        _case("white-single-move", Cell.WHITE, _single_move_board(Cell.WHITE)),
        _case("black-late-game", Cell.BLACK, _late_game_board(Cell.BLACK)),
        _case("white-late-game", Cell.WHITE, _late_game_board(Cell.WHITE)),
    ]
    return [case for case in cases if case.valid_moves]


def _case(name: str, color: Cell, board: Board) -> _RuntimeCase:
    return _RuntimeCase(
        name=name,
        color=color,
        board=board,
        valid_moves=_valid_moves(board, color),
    )


def _validate_runtime_case(
    player_class: type[BasePlayer],
    case: _RuntimeCase,
    *,
    max_seconds: float,
) -> tuple[ValidationIssue | None, float | None]:
    board = copy_board(case.board)
    player = player_class(case.color)

    start = time.perf_counter()
    try:
        with _time_limit(max_seconds):
            move = player.next_move(board)
    except _MoveTimeoutError:
        return (
            ValidationIssue(
                "timeout",
                f"{case.name}: next_move() exceeded {max_seconds:.3g} seconds.",
            ),
            None,
        )
    except Exception as exc:  # noqa: BLE001
        return (
            ValidationIssue(
                "runtime-error",
                f"{case.name}: next_move() raised {type(exc).__name__}: {exc}.",
            ),
            None,
        )
    elapsed = time.perf_counter() - start

    if elapsed > max_seconds:
        return (
            ValidationIssue(
                "timeout",
                f"{case.name}: next_move() took {elapsed:.3g} seconds.",
            ),
            elapsed,
        )

    if not _is_move(move):
        return (
            ValidationIssue(
                "invalid-move-shape",
                f"{case.name}: next_move() returned {move!r}, not (row, col).",
            ),
            elapsed,
        )

    normalized_move: Move = (move[0], move[1])
    if normalized_move not in case.valid_moves:
        return (
            ValidationIssue(
                "illegal-move",
                f"{case.name}: next_move() returned {normalized_move!r}; valid moves "
                f"are {case.valid_moves}.",
            ),
            elapsed,
        )

    return None, elapsed


@contextlib.contextmanager
def _time_limit(seconds: float) -> Iterator[None]:
    if not hasattr(signal, "setitimer"):
        yield
        return

    def handler(_signum: int, _frame: FrameType | None) -> None:
        msg = "next_move timed out"
        raise _MoveTimeoutError(msg)

    previous_handler = signal.signal(signal.SIGALRM, handler)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


def _valid_moves(board: Board, color: Cell) -> list[Move]:
    return _ReferencePlayer(color).get_moves(board)


def _is_move(move: object) -> bool:
    if not isinstance(move, tuple | list):
        return False
    if len(move) != _MOVE_LENGTH:
        return False
    row, col = move
    return isinstance(row, int) and isinstance(col, int)


def _corner_board(color: Cell) -> Board:
    board = [[Cell.EMPTY for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
    other_color = _other_color(color)
    board[0][1] = other_color
    board[0][2] = color
    board[1][0] = other_color
    board[2][0] = color
    return board


def _edge_board(color: Cell) -> Board:
    board = [[Cell.EMPTY for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
    other_color = _other_color(color)
    board[0][2] = color
    board[0][3] = other_color
    board[0][4] = other_color
    board[0][5] = Cell.EMPTY
    board[1][5] = other_color
    board[2][5] = color
    return board


def _multi_direction_board(color: Cell) -> Board:
    board = [[Cell.EMPTY for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
    other_color = _other_color(color)
    center = 3
    for row_step, col_step in (
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ):
        board[center + row_step][center + col_step] = other_color
        board[center + row_step * 2][center + col_step * 2] = color
    board[center][center] = Cell.EMPTY
    return board


def _single_move_board(color: Cell) -> Board:
    other_color = _other_color(color)
    board = [[other_color for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
    board[0][0] = Cell.EMPTY
    board[0][1] = other_color
    board[0][2] = color
    return board


def _late_game_board(color: Cell) -> Board:
    other_color = _other_color(color)
    board = [[color for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
    board[6][6] = other_color
    board[6][7] = other_color
    board[7][6] = other_color
    board[7][7] = Cell.EMPTY
    return board


def _other_color(color: Cell) -> Cell:
    if color == Cell.BLACK:
        return Cell.WHITE
    return Cell.BLACK


def _has_errors(issues: list[ValidationIssue]) -> bool:
    return any(issue.severity == ValidationSeverity.ERROR for issue in issues)


__all__ = [
    "ValidationIssue",
    "ValidationResult",
    "ValidationSeverity",
    "test_player",
    "test_player_detail",
    "validate",
    "validate_detail",
]
