"""Pre-submission validation helpers for student players."""

from __future__ import annotations

import ast
import builtins
import contextlib
import dis
import inspect
import signal
import sys
import textwrap
import time
import types
from dataclasses import dataclass, field
from enum import Enum
from types import ModuleType
from typing import TYPE_CHECKING, Any

from othellopy.board import copy_board, initial_board
from othellopy.core import Board, Cell, Move
from othellopy.players.base import BasePlayer

if TYPE_CHECKING:
    from collections.abc import Iterator

_DEFAULT_MAX_SECONDS = 1.0
_BOARD_SIZE = 8
_MOVE_LENGTH = 2

_BANNED_MODULES = {
    "asyncio",
    "builtins",
    "ctypes",
    "ftplib",
    "glob",
    "http",
    "importlib",
    "marshal",
    "multiprocessing",
    "os",
    "pathlib",
    "pickle",
    "runpy",
    "shlex",
    "shutil",
    "signal",
    "socket",
    "ssl",
    "subprocess",
    "sys",
    "tempfile",
    "threading",
    "urllib",
    "webbrowser",
}
_BANNED_CALLS = {
    "__import__",
    "breakpoint",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}
_BANNED_ATTRIBUTES = {
    "__bases__",
    "__builtins__",
    "__class__",
    "__code__",
    "__dict__",
    "__func__",
    "__getattribute__",
    "__globals__",
    "__mro__",
    "__subclasses__",
}
_ALLOWED_BUILTIN_GLOBALS = {
    "abs",
    "all",
    "any",
    "bool",
    "dict",
    "enumerate",
    "float",
    "int",
    "len",
    "list",
    "max",
    "min",
    "print",
    "range",
    "reversed",
    "round",
    "set",
    "sorted",
    "str",
    "sum",
    "super",
    "tuple",
    "zip",
}
_ALLOWED_GLOBAL_OBJECTS = {
    "BasePlayer",
    "Board",
    "Cell",
    "Move",
}
_ALLOWED_OTHELLOPY_MODULES = {
    "othellopy",
    "othellopy.board",
    "othellopy.core",
    "othellopy.players",
}


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
    """Detailed result returned by validate_detail()."""

    passed: bool
    issues: list[ValidationIssue]
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Return issues that make validation fail."""
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.ERROR
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
    """Return True if player_class passes the pre-submission checks."""
    return validate_detail(player_class, max_seconds=max_seconds).passed


def validate_detail(
    player_class: type[BasePlayer],
    *,
    max_seconds: float = _DEFAULT_MAX_SECONDS,
) -> ValidationResult:
    """Return detailed pre-submission validation results for player_class."""
    issues: list[ValidationIssue] = []
    details: dict[str, Any] = {"max_seconds": max_seconds}

    issues.extend(_validate_class_shape(player_class))
    source = _source_for(player_class)
    if source is None:
        issues.append(
            ValidationIssue(
                "source-unavailable",
                "Could not inspect the Player source code. Define the class in a "
                "normal Python cell or file to enable static checks. Runtime "
                "checks will still run.",
                ValidationSeverity.WARNING,
            )
        )
    else:
        details["source_length"] = len(source)
        issues.extend(_validate_source(source))

    issues.extend(_validate_global_usage(player_class))

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
                "validate() expects a Player class, such as validate(MyPlayer).",
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


def _source_for(player_class: type[BasePlayer]) -> str | None:
    try:
        return textwrap.dedent(inspect.getsource(player_class))
    except (OSError, TypeError):
        return None


def _validate_source(source: str) -> list[ValidationIssue]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [
            ValidationIssue(
                "syntax-error",
                f"Player source has a syntax error: {exc.msg}.",
            )
        ]

    visitor = _StaticValidationVisitor()
    visitor.visit(tree)
    return visitor.issues


class _StaticValidationVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.issues: list[ValidationIssue] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._validate_module(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            self._add(
                "relative-import",
                node.lineno,
                "Relative imports are not allowed.",
            )
        else:
            self._validate_module(node.module, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _call_name(node.func)
        if call_name in _BANNED_CALLS:
            self._add(
                "banned-call",
                node.lineno,
                f"Calling {call_name}() is not allowed in submitted players.",
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in _BANNED_ATTRIBUTES:
            self._add(
                "banned-attribute",
                node.lineno,
                f"Accessing {node.attr} is not allowed in submitted players.",
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.generic_visit(node)

    def _validate_module(self, module_name: str, lineno: int) -> None:
        top_level = module_name.split(".", maxsplit=1)[0]
        if top_level in _BANNED_MODULES:
            self._add(
                "banned-module",
                lineno,
                f"Importing {module_name!r} is not allowed.",
            )
            return

        if _is_allowed_module(module_name):
            return

        self._add(
            "external-module",
            lineno,
            f"External package {module_name!r} is not allowed. Use only the "
            "Python standard library and othellopy.",
        )

    def _add(self, code: str, lineno: int, message: str) -> None:
        self.issues.append(
            ValidationIssue(
                code,
                f"Line {lineno}: {message}",
            )
        )


def _validate_global_usage(player_class: type[BasePlayer]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for method_name, method in player_class.__dict__.items():
        if not inspect.isfunction(method):
            continue
        issues.extend(
            _validate_code_globals(method.__code__, method.__globals__, method_name)
        )
    return issues


def _validate_code_globals(
    code: types.CodeType,
    globals_: dict[str, Any],
    context: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for name in _load_global_names(code):
        if name in _BANNED_CALLS:
            issues.append(
                ValidationIssue(
                    "banned-call",
                    f"{context} uses banned global {name!r}.",
                )
            )
            continue
        if name in _ALLOWED_BUILTIN_GLOBALS or name in _ALLOWED_GLOBAL_OBJECTS:
            continue
        if name in vars(builtins):
            issues.append(
                ValidationIssue(
                    "banned-builtin",
                    f"{context} uses builtin {name!r}, which is not allowed.",
                )
            )
            continue
        if name not in globals_:
            issues.append(
                ValidationIssue(
                    "unknown-global",
                    f"{context} uses global name {name!r}. Keep submitted players "
                    "self-contained.",
                )
            )
            continue
        if not _is_allowed_global_object(globals_[name]):
            issues.append(
                ValidationIssue(
                    "external-global",
                    f"{context} uses global name {name!r} from a disallowed module.",
                )
            )

    for constant in code.co_consts:
        if isinstance(constant, types.CodeType):
            issues.extend(_validate_code_globals(constant, globals_, context))

    return issues


def _load_global_names(code: types.CodeType) -> set[str]:
    names = set()
    for instruction in dis.get_instructions(code):
        if instruction.opname in {"LOAD_GLOBAL", "LOAD_NAME"}:
            names.add(str(instruction.argval))
    return names


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


def _runtime_cases() -> list[_RuntimeCase]:
    return [
        _RuntimeCase("initial-black", Cell.BLACK, initial_board()),
        _RuntimeCase("initial-white", Cell.WHITE, initial_board()),
        _RuntimeCase("black-corner", Cell.BLACK, _corner_board(Cell.BLACK)),
        _RuntimeCase("white-corner", Cell.WHITE, _corner_board(Cell.WHITE)),
        _RuntimeCase("black-single-move", Cell.BLACK, _single_move_board(Cell.BLACK)),
        _RuntimeCase("white-single-move", Cell.WHITE, _single_move_board(Cell.WHITE)),
    ]


def _validate_runtime_case(
    player_class: type[BasePlayer],
    case: _RuntimeCase,
    *,
    max_seconds: float,
) -> tuple[ValidationIssue | None, float | None]:
    board = copy_board(case.board)
    valid_moves = _valid_moves(case.board, case.color)
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

    if tuple(move) not in valid_moves:
        return (
            ValidationIssue(
                "illegal-move",
                f"{case.name}: next_move() returned {tuple(move)!r}; valid moves "
                f"are {valid_moves}.",
            ),
            elapsed,
        )

    return None, elapsed


@contextlib.contextmanager
def _time_limit(seconds: float) -> Iterator[None]:
    if not hasattr(signal, "setitimer"):
        yield
        return

    def handler(_signum: int, _frame: types.FrameType | None) -> None:
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
    opponent = Cell.WHITE if color == Cell.BLACK else Cell.BLACK
    board[0][1] = opponent
    board[0][2] = color
    board[1][0] = opponent
    board[2][0] = color
    return board


def _single_move_board(color: Cell) -> Board:
    opponent = Cell.WHITE if color == Cell.BLACK else Cell.BLACK
    board = [[opponent for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
    board[0][0] = Cell.EMPTY
    board[0][1] = opponent
    board[0][2] = color
    return board


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _is_allowed_module(module_name: str) -> bool:
    if module_name in _ALLOWED_OTHELLOPY_MODULES:
        return True
    if module_name.startswith("othellopy."):
        return module_name.rsplit(".", maxsplit=1)[0] in _ALLOWED_OTHELLOPY_MODULES
    top_level = module_name.split(".", maxsplit=1)[0]
    return top_level in sys.stdlib_module_names


def _is_allowed_global_object(value: object) -> bool:
    if inspect.ismodule(value):
        return _is_allowed_object_module(value)

    module_name = getattr(value, "__module__", None)
    if not isinstance(module_name, str):
        return False
    return (
        _is_allowed_module(module_name)
        and _module_top_level(module_name) not in _BANNED_MODULES
    )


def _is_allowed_object_module(module: ModuleType) -> bool:
    name = module.__name__
    return _is_allowed_module(name) and _module_top_level(name) not in _BANNED_MODULES


def _module_top_level(module_name: str) -> str:
    return module_name.split(".", maxsplit=1)[0]


def _has_errors(issues: list[ValidationIssue]) -> bool:
    return any(issue.severity == ValidationSeverity.ERROR for issue in issues)


__all__ = [
    "ValidationIssue",
    "ValidationResult",
    "ValidationSeverity",
    "validate",
    "validate_detail",
]
