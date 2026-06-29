# othellopy

Python package scaffold for Othello/Reversi-related utilities.

## Google Colab

Install the latest `main` branch in a Colab notebook:

```python
!pip install git+https://github.com/Hietan/othellopy.git@main
```

Then import the package:

```python
from othellopy.core import Cell
from othellopy.game import OthelloGame
from othellopy.players import BasePlayer
```

## Player example

Use `BasePlayer` to build your own player class.

```python
from othellopy.core import Cell
from othellopy.players import BasePlayer


class MyPlayer(BasePlayer):
    def __init__(self, color: Cell) -> None:
        super().__init__(color)

    def next_move(self, board: list[list[Cell]]) -> tuple[int, int]:
        return self.get_moves(board)[0]
```

Board cells use `Cell.EMPTY`, `Cell.BLACK`, and `Cell.WHITE`.
Coordinates are zero-based `(row, col)` pairs, matching `board[row][col]`.
`next_move()` is called only when the player has at least one valid move.

Use sample players when you want a ready-made baseline:

```python
from othellopy.players import AdvancedPlayer, BeginnerPlayer, IntermediatePlayer
```

- `BeginnerPlayer`: chooses a legal move randomly.
- `IntermediatePlayer`: scores legal moves with a simple heuristic.
- `AdvancedPlayer`: searches ahead with alpha-beta pruning.

## Game example

Pass two player classes to `OthelloGame` and call `play()`.

```python
from othellopy.game import OthelloGame

result = OthelloGame(MyPlayer, MyPlayer).play()

print(result.winner)
print(result.black_score, result.white_score)
```

Use board helpers when debugging in notebooks. Board output uses `⚫️` and `⚪️`
when the output encoding supports them, and falls back to `B` and `W`
otherwise.

```python
from othellopy.board import print_board

print_board(result.board)

last_turn = result.turns[-1]
print(last_turn.valid_moves)
print_board(last_turn.board)
```

If a player returns an invalid move, the error message includes the move,
valid moves, and the board for that turn.

## Git Flow

Use these branch roles:

- `main`: deployment branch for Colab installs.
- `dev`: integration branch before release.
- `release/*`: release preparation branch.
- `feat/*`: feature work branch.

Recommended flow:

```bash
git switch dev
git switch -c feat/my-feature
# work and commit
git switch dev
git merge --no-ff feat/my-feature
git switch -c release/v0.1.0
# final checks
git switch main
git merge --no-ff release/v0.1.0
git push origin main
```

## Development

Create a virtual environment and install the package in editable mode:

```bash
uv venv
uv pip install -e ".[dev]"
```

Run tests:

```bash
uv run pytest
```

Run type checks:

```bash
uv run mypy src/othellopy
```

Build distributions:

```bash
uv build
```
