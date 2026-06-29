"""Board helpers for Othello/Reversi exercises."""

import html
import sys
from importlib import import_module
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable

from othellopy.core import Board, Cell

_EMOJI_MARKS = {
    Cell.EMPTY: ".",
    Cell.BLACK: "⚫️",
    Cell.WHITE: "⚪️",
}
_LETTER_MARKS = {
    Cell.EMPTY: ".",
    Cell.BLACK: "B",
    Cell.WHITE: "W",
}
_HTML_TABLE_STYLE = (
    "border-collapse:collapse;"
    "table-layout:fixed;"
    "font-family:Arial,'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',"
    "sans-serif;"
)
_HTML_HEADER_STYLE = (
    "width:2.25em;"
    "height:2.25em;"
    "min-width:2.25em;"
    "max-width:2.25em;"
    "padding:0;"
    "text-align:center;"
    "vertical-align:middle;"
    "font-size:0.9em;"
    "line-height:1;"
    "font-weight:600;"
    "color:#374151;"
)
_HTML_CELL_STYLE = (
    "width:2.25em;"
    "height:2.25em;"
    "min-width:2.25em;"
    "max-width:2.25em;"
    "padding:0;"
    "border:1px solid #9ca3af;"
    "background:#15803d;"
    "text-align:center;"
    "vertical-align:middle;"
    "font-size:1.25em;"
    "line-height:1;"
)


def initial_board() -> Board:
    """Return the standard initial Othello board."""
    board = [[Cell.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = Cell.WHITE
    board[3][4] = Cell.BLACK
    board[4][3] = Cell.BLACK
    board[4][4] = Cell.WHITE
    return board


def copy_board(board: Board) -> Board:
    """Return a shallow row-by-row copy of a board."""
    return [row.copy() for row in board]


def board_to_str(board: Board, *, use_emoji: bool | None = None) -> str:
    """Return a readable board string for notebooks and debugging."""
    marks = _EMOJI_MARKS if _should_use_emoji(use_emoji=use_emoji) else _LETTER_MARKS
    lines = ["  0 1 2 3 4 5 6 7"]
    for row_number, row in enumerate(board):
        cells = " ".join(_cell_to_mark(cell, marks) for cell in row)
        lines.append(f"{row_number} {cells}")
    return "\n".join(lines)


def board_to_html(board: Board, *, use_emoji: bool | None = None) -> str:
    """Return a fixed-cell HTML board string for notebook display."""
    marks = _EMOJI_MARKS if _should_use_emoji(use_emoji=use_emoji) else _LETTER_MARKS
    column_count = max((len(row) for row in board), default=0)
    lines = [
        '<table role="grid" aria-label="Othello board" '
        f'style="{_HTML_TABLE_STYLE}">'
    ]
    header_cells = [_html_cell("th", "", _HTML_HEADER_STYLE)]
    header_cells.extend(
        _html_cell("th", str(column_number), _HTML_HEADER_STYLE)
        for column_number in range(column_count)
    )
    lines.append(f"<tr>{''.join(header_cells)}</tr>")

    for row_number, row in enumerate(board):
        cells = [_html_cell("th", str(row_number), _HTML_HEADER_STYLE)]
        cells.extend(
            _html_cell("td", _cell_to_mark(cell, marks), _HTML_CELL_STYLE)
            for cell in row
        )
        lines.append(f"<tr>{''.join(cells)}</tr>")

    lines.append("</table>")
    return "".join(lines)


def display_board(board: Board, *, use_emoji: bool | None = None) -> None:
    """Display a board as HTML in notebooks, falling back to text output."""
    try:
        display_module = import_module("IPython.display")
    except ImportError:
        print_board(board, use_emoji=use_emoji)
        return

    html_factory = getattr(display_module, "HTML", None)
    display_func = getattr(display_module, "display", None)
    if not callable(html_factory) or not callable(display_func):
        print_board(board, use_emoji=use_emoji)
        return

    make_html = cast("Callable[[str], object]", html_factory)
    display = cast("Callable[[object], object]", display_func)
    display(make_html(board_to_html(board, use_emoji=use_emoji)))


def print_board(board: Board, *, use_emoji: bool | None = None) -> None:
    """Print a readable board for notebooks and debugging."""
    sys.stdout.write(f"{board_to_str(board, use_emoji=use_emoji)}\n")


def _should_use_emoji(*, use_emoji: bool | None) -> bool:
    if use_emoji is not None:
        return use_emoji

    encoding = sys.stdout.encoding
    if encoding is None:
        return False

    try:
        "⚫️⚪️".encode(encoding)
    except UnicodeEncodeError:
        return False

    return True


def _cell_to_mark(cell: Cell, marks: dict[Cell, str]) -> str:
    return marks[Cell(cell)]


def _html_cell(tag: str, content: str, style: str) -> str:
    return f'<{tag} style="{style}">{html.escape(content)}</{tag}>'
