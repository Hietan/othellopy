# Contributing

Thank you for considering a contribution to `othellopy`.

## Development Setup

```bash
uv venv
uv pip install -e ".[dev]"
```

Run the local checks before opening a pull request:

```bash
uv run --extra dev ruff check .
uv run --extra dev mypy src/othellopy
uv run --extra dev pytest
uv build
```

## GitFlow

This repository follows a GitFlow-style branch model.

- `main`: release/deployment branch. Do not push directly.
- `dev`: integration branch for completed work.
- `feat/*`: feature and maintenance work branches.
- `release/*`: release preparation branches.

Expected flow:

```bash
git switch dev
git switch -c feat/my-change
# work and commit
git switch dev
git merge --no-ff feat/my-change
git switch -c release/v0.1.0
# final release checks
git switch main
git merge --no-ff release/v0.1.0
```

Pull request routing:

- Open `feat/*` pull requests into `dev`.
- Open `release/*` pull requests into `main`.
- Do not open `feat/*` pull requests directly into `main`.
- `main` requires maintainer approval and passing required checks.

Direct pushes to `main`, force pushes, and branch deletion should be blocked by
GitHub branch protection or rulesets.

## Pull Requests

- Keep changes focused.
- Include tests for behavior changes.
- Update README or other docs when public behavior changes.
- Use Conventional Commit style for commit subjects when practical, such as
  `feat: add manual player` or `fix: validate moves`.

## Public API

Public APIs are imported from these modules:

- `othellopy.core`
- `othellopy.board`
- `othellopy.game`
- `othellopy.players`

Modules, functions, or names beginning with `_` are internal and may change
without notice while the package is in `0.x`.
