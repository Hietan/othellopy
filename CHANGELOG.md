# Changelog

All notable changes to this project will be documented in this file.

The project follows semantic versioning where practical. While the major
version is `0`, public APIs may change between minor releases.

## Unreleased

- Add a default one-second per-move timeout to `OthelloGame`; timed-out players
  forfeit and the opponent wins.
- Tune the default `AdvancedPlayer` search depth so normal games finish within
  the per-move timeout.

## 0.2.3 - 2026-06-29

- Rename the recommended runtime check API to `test_player()` and
  `test_player_detail()`, keeping `validate()` and `validate_detail()` as
  compatibility aliases.
- Make `BasePlayer.__init__` inheritable so beginner players can implement only
  `next_move()`.
- Prefer `display_board()` for both notebook and terminal board output while
  keeping `print_board()` as a text-output compatibility helper.
- Prefer `black_player=` and `white_player=` keyword arguments in
  `OthelloGame`, keeping the previous `*_player_class` names compatible.
- Add `GameResult.winner_name` for display-friendly `BLACK`, `WHITE`, or
  `DRAW` output.
- Expand runtime player tests across more board states and keep validation
  dynamic-only for Google Colab workflows.

## 0.2.2 - 2026-06-29

- Allow `print()` and `display_board()` during player checks for Google Colab
  debugging.
- Pass copied boards into player checks and games so accidental board mutation
  does not change the real game state.
- Continue runtime checks even when source inspection is unavailable in notebook
  environments.

## 0.2.1 - 2026-06-29

- Add `board_to_html()` and `display_board()` for fixed-cell notebook board
  display with emoji stones.
- Recommend `display_board()` for Google Colab to avoid emoji width alignment
  issues in plain text output.

## 0.2.0 - 2026-06-29

- Rename the public board value enum from `Piece` to `Cell`.
- Move public player classes under `othellopy.players`.
- Add `BeginnerPlayer`, `IntermediatePlayer`, `AdvancedPlayer`, and
  `ManualPlayer`.
- Add `othellopy.validation.validate()` and `validate_detail()` for
  pre-submission player checks.
- Treat invalid player moves as forfeits and expose `GameResult.forfeit`.
- Render boards with emoji stones when supported, with ASCII fallback.
- Add strict ruff and mypy checks, CI, Apache-2.0 metadata, and OSS project
  governance documents.

## 0.1.0 - 2026-06-28

- Initial PyPI release of the Othello/Reversi board, game, and player
  utilities.
