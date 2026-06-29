# Changelog

All notable changes to this project will be documented in this file.

The project follows semantic versioning where practical. While the major
version is `0`, public APIs may change between minor releases.

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
