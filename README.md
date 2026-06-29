# othellopy

[![PyPI](https://img.shields.io/pypi/v/othellopy.svg)](https://pypi.org/project/othellopy/)
[![Python](https://img.shields.io/pypi/pyversions/othellopy.svg)](https://pypi.org/project/othellopy/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/Hietan/othellopy/blob/main/LICENSE)
[![CI](https://github.com/Hietan/othellopy/actions/workflows/ci.yml/badge.svg)](https://github.com/Hietan/othellopy/actions/workflows/ci.yml)

`othellopy` is a small Python package for Othello/Reversi exercises. It
provides a board model, a game runner, move validation helpers, and sample
players ranging from random play to alpha-beta search.

The package is currently `0.x` alpha software. Public APIs may change before
`1.0.0`.

Official distribution:

- PyPI package: [`othellopy`](https://pypi.org/project/othellopy/)
- Source repository: [`Hietan/othellopy`](https://github.com/Hietan/othellopy)
- Issues: <https://github.com/Hietan/othellopy/issues>

## Requirements

- Python 3.10 or later
- No runtime dependencies

## Installation

Install from PyPI:

```bash
python -m pip install othellopy
```

Upgrade an existing PyPI installation:

```bash
python -m pip install --upgrade othellopy
```

Check the installed version:

```bash
python -m pip show othellopy
```

Install an unreleased branch from GitHub only when you intentionally need
development code, for example in Google Colab:

```python
!pip install git+https://github.com/Hietan/othellopy.git@main
```

## Quick Start

Run a complete game between two sample players:

```python
from othellopy.board import print_board
from othellopy.game import OthelloGame
from othellopy.players import BeginnerPlayer, IntermediatePlayer

result = OthelloGame(BeginnerPlayer, IntermediatePlayer).play()

print(result.winner)
print(result.black_score, result.white_score)
print_board(result.board)
```

## Writing a Player

Subclass `BasePlayer` and implement `next_move()`.

```python
from othellopy.core import Board, Cell, Move
from othellopy.players import BasePlayer


class MyPlayer(BasePlayer):
    def __init__(self, color: Cell) -> None:
        super().__init__(color)

    def next_move(self, board: Board) -> Move:
        return self.get_moves(board)[0]
```

Coordinates are zero-based `(row, col)` pairs. `next_move()` is called only
when the player has at least one legal move.

## Pre-Submission Player Check

Use `validate()` before submitting a custom player from Google Colab or another
notebook environment.

```python
from othellopy.validation import validate, validate_detail

if validate(MyPlayer):
    print("OK to submit")
else:
    result = validate_detail(MyPlayer)
    for issue in result.errors:
        print(issue.code, issue.message)
```

The validator checks that the class inherits from `BasePlayer`, can be
constructed for black and white, returns legal moves on several board states,
and returns within one second by default. `print()` and `display_board()` are
allowed, so students can debug in Google Colab while running validation.

The board passed to `next_move()` is an isolated copy during validation and game
play, so accidental board edits do not change the real game state. Students
should still treat the board as read-only because only the returned move is used.

When Google Colab prevents source inspection, validation reports
`source-unavailable` as a warning and continues with runtime checks.

The validator also performs static checks when source code is available.
External packages such as `numpy` and `pandas` are not allowed for this course.
Most safe Python standard library modules are allowed, including:

- `random`
- `math`
- `statistics`
- `itertools`
- `collections`
- `functools`
- `operator`
- `heapq`
- `bisect`
- `copy`

File, process, network, import-system, threading, and arbitrary-code execution
APIs are rejected. Examples include `os`, `sys`, `pathlib`, `subprocess`,
`socket`, `urllib`, `pickle`, `importlib`, `threading`, `open()`, `input()`,
`eval()`, and `exec()`.

This is a pre-submission screen, not a security sandbox. Evaluation servers
should run the same validation again and execute submitted players in an
isolated sandbox.

## Manual CLI Play

Use `ManualPlayer` to enter moves interactively from a terminal. Input is
two digits in row-column order, such as `07`.

```python
from othellopy.game import OthelloGame
from othellopy.players import BeginnerPlayer, ManualPlayer

result = OthelloGame(ManualPlayer, BeginnerPlayer).play()
```

Equivalent one-off command:

```bash
uv run python - <<'PY'
from othellopy.game import OthelloGame
from othellopy.players import BeginnerPlayer, ManualPlayer

result = OthelloGame(ManualPlayer, BeginnerPlayer).play()
print(result.winner, result.black_score, result.white_score)
PY
```

## Sample Players

Import sample players from `othellopy.players`:

```python
from othellopy.players import (
    AdvancedPlayer,
    BeginnerPlayer,
    IntermediatePlayer,
    ManualPlayer,
)
```

- `BeginnerPlayer`: chooses a legal move randomly.
- `IntermediatePlayer`: scores legal moves with a simple one-ply heuristic.
- `AdvancedPlayer`: searches ahead with alpha-beta pruning.
- `ManualPlayer`: asks for row-column input in a CLI.

## Board Display

Board helpers render stones as `⚫️` and `⚪️` when the output encoding supports
them. If the output cannot encode those emoji, display falls back to `B` and
`W`.

Use `display_board()` in Google Colab or Jupyter notebooks. It renders a fixed
HTML table so emoji stones stay aligned even when the notebook font gives emoji
a different display width from ASCII characters.

```python
from othellopy.board import display_board, initial_board

display_board(initial_board())
```

Use `print_board()` for terminal output.

```python
from othellopy.board import initial_board, print_board

print_board(initial_board())
```

Use `board_to_str(..., use_emoji=False)` when you need stable ASCII output.

## Invalid Moves and Forfeits

If a player returns an invalid move, the player forfeits and the opponent wins.
The game still returns a `GameResult`.

```python
result = OthelloGame(MyPlayer, BeginnerPlayer).play()

if result.forfeit is not None:
    print(result.winner)
    print(result.forfeit.color)
    print(result.forfeit.move)
    print(result.forfeit.valid_moves)
```

## API Overview

### `othellopy.core`

`Cell`
: `IntEnum` representing board cell values.

```python
Cell.EMPTY
Cell.BLACK
Cell.WHITE
```

`Board`
: Type alias for `list[list[Cell]]`.

`Move`
: Type alias for `tuple[int, int]`.

`opponent(cell: Cell) -> Cell`
: Returns `Cell.WHITE` for `Cell.BLACK`, and `Cell.BLACK` for `Cell.WHITE`.
  Passing `Cell.EMPTY` raises `ValueError`.

### `othellopy.board`

`initial_board() -> Board`
: Returns the standard 8x8 initial Othello board.

`copy_board(board: Board) -> Board`
: Returns a row-by-row copy of a board.

`board_to_str(board: Board, *, use_emoji: bool | None = None) -> str`
: Converts a board to readable text.

`board_to_html(board: Board, *, use_emoji: bool | None = None) -> str`
: Converts a board to a fixed-cell HTML table for notebook display.

`display_board(board: Board, *, use_emoji: bool | None = None) -> None`
: Displays a board as HTML in IPython notebooks, falling back to text output
  outside IPython.

`print_board(board: Board, *, use_emoji: bool | None = None) -> None`
: Prints a readable board.

### `othellopy.players`

`BasePlayer`
: Base class for custom players. Provides:

- `color`
- `opponent_color`
- `get_moves(board)`
- `is_valid_move(board, row, col)`
- `get_flips(board, row, col)`

`BeginnerPlayer`
: Random legal move player.

`IntermediatePlayer`
: Simple heuristic player.

`AdvancedPlayer`
: Alpha-beta search player. Accepts `depth=` in the constructor.

`ManualPlayer`
: Interactive CLI player. Accepts optional `input_func`, `output`, and
  `use_emoji` parameters for testing or custom IO.

### `othellopy.game`

`OthelloGame(black_player_class, white_player_class)`
: Runs one game between two `BasePlayer` subclasses.

`GameResult`
: Return value from `OthelloGame(...).play()`.

Fields:

- `winner: Cell`
- `black_score: int`
- `white_score: int`
- `board: Board`
- `moves: list[tuple[Cell, int, int]]`
- `turns: list[TurnRecord]`
- `forfeit: ForfeitRecord | None`

`TurnRecord`
: Per-turn debug information.

Fields:

- `color: Cell`
- `board: Board`
- `valid_moves: list[tuple[int, int]]`
- `move: tuple[int, int] | None`
- `black_score: int`
- `white_score: int`

`ForfeitRecord`
: Invalid-move forfeit information.

Fields:

- `color: Cell`
- `move: object`
- `valid_moves: list[tuple[int, int]]`
- `board: Board`
- `message: str`

### `othellopy.validation`

`validate(player_class, *, max_seconds=1.0) -> bool`
: Returns `True` when a submitted player class passes pre-submission checks.

`validate_detail(player_class, *, max_seconds=1.0) -> ValidationResult`
: Returns detailed errors, warnings, and runtime case details.

`ValidationResult`
: Detailed validation result.

Fields:

- `passed: bool`
- `issues: list[ValidationIssue]`
- `errors: list[ValidationIssue]`
- `warnings: list[ValidationIssue]`
- `details: dict[str, object]`

`ValidationIssue`
: One validation issue.

Fields:

- `code: str`
- `message: str`
- `severity: ValidationSeverity`

## Development

```bash
uv venv
uv pip install -e ".[dev]"
```

Run checks:

```bash
uv run --extra dev ruff check .
uv run --extra dev mypy src/othellopy
uv run --extra dev pytest
uv build
```

## Release Policy

`othellopy` is published on PyPI from GitHub tags named `vX.Y.Z`.
Published PyPI files are immutable, so a broken release is fixed by publishing
a newer version instead of replacing an existing one.

The release checklist is documented in
[`RELEASE.md`](https://github.com/Hietan/othellopy/blob/main/RELEASE.md).

## Contributing

Contributions must follow the GitFlow rules in
[`CONTRIBUTING.md`](https://github.com/Hietan/othellopy/blob/main/CONTRIBUTING.md):

- `feat/*` pull requests target `dev`.
- `release/*` pull requests target `main`.
- Direct pushes to `main` and `dev` are not allowed.
- Required checks must pass before merge.

## Security

Please do not report vulnerabilities in public issues. See
[`SECURITY.md`](https://github.com/Hietan/othellopy/blob/main/SECURITY.md).

## License

Licensed under the Apache License, Version 2.0. See
[`LICENSE`](https://github.com/Hietan/othellopy/blob/main/LICENSE).
