# othellopy

Python package scaffold for Othello/Reversi-related utilities.

## Player example

Use `BasePlayer` to build your own player class.

```python
from othellopy.core import Piece
from othellopy.player import BasePlayer


class MyPlayer(BasePlayer):
    def __init__(self, color: Piece) -> None:
        super().__init__(color)

    def next_move(self, board: list[list[Piece]]) -> tuple[int, int]:
        return self.get_moves(board)[0]
```

Board cells use `Piece.EMPTY`, `Piece.BLACK`, and `Piece.WHITE`.
Coordinates are zero-based `(row, col)` pairs, matching `board[row][col]`.
`next_move()` is called only when the player has at least one valid move.

## Game example

Pass two player classes to `OthelloGame` and call `play()`.

```python
from othellopy.game import OthelloGame

result = OthelloGame(MyPlayer, MyPlayer).play()

print(result.winner)
print(result.black_score, result.white_score)
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

Build distributions:

```bash
uv build
```
