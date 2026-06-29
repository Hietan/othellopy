# Contributing

Thank you for considering a contribution to `othellopy`.

The official package is published on PyPI as
[`othellopy`](https://pypi.org/project/othellopy/), from the source repository
[`Hietan/othellopy`](https://github.com/Hietan/othellopy).

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
- `dependabot/*`: automated dependency update branches targeting `dev`.

Expected flow:

```bash
git switch dev
git switch -c feat/my-change
# work and commit
git push -u origin feat/my-change
# open a pull request from feat/my-change to dev

git switch dev
git pull --ff-only
git switch -c release/vX.Y.Z
# final release checks
git push -u origin release/vX.Y.Z
# open a pull request from release/vX.Y.Z to main
```

Pull request routing:

- Open `feat/*` pull requests into `dev`.
- Open `dependabot/*` pull requests into `dev`.
- Open `release/*` pull requests into `main`.
- Do not open `feat/*` pull requests directly into `main`.
- `main` requires a release pull request and passing required checks.

Direct pushes to `main` and `dev`, force pushes, and branch deletion should be
blocked by GitHub branch protection or rulesets.

## Commit Messages

Use this format for commit messages:

```text
<prefix>: <summary>

<details>
```

The first line is required. Use a short prefix such as `feat`, `fix`, `docs`,
`test`, `refactor`, `chore`, `ci`, `build`, `style`, or `perf`, followed by a
concise summary.

Leave the second line blank when adding details. Details are optional and start
on the third line.

Examples:

```text
feat: add manual player
```

```text
fix: treat invalid moves as forfeits

Report the buggy player as the loser when it returns an illegal move.
```

## Pull Requests

- Keep changes focused.
- Include tests for behavior changes.
- Update README or other docs when public behavior changes.
- Update `CHANGELOG.md` for user-visible behavior, public API, packaging, or
  release process changes.
- Follow the commit message format above.

## Releases

Only maintainers publish to PyPI. Releases are prepared from `dev` on a
`release/vX.Y.Z` branch, merged into `main`, tagged as `vX.Y.Z`, and published
by the GitHub Actions `Publish` workflow.

Before opening a release pull request:

- Update the version in `pyproject.toml` and `src/othellopy/__init__.py`.
- Update `CHANGELOG.md` and replace `Unreleased` with the release date.
- Run ruff, mypy, pytest, and `uv build`.
- Confirm that PyPI does not already have the target version.

PyPI does not allow replacing a released file. If a release is broken, publish
a new patch or minor version instead of reusing the same version number.

See [`RELEASE.md`](RELEASE.md) for the full checklist.

## Dependency Updates

Dependabot checks Python dependencies managed by `uv` and GitHub Actions
weekly. These pull requests target `dev` and use `dependabot/*` branches as the
only automated exception to human `feat/*` work branches.

## Public API

Public APIs are imported from these modules:

- `othellopy.core`
- `othellopy.board`
- `othellopy.game`
- `othellopy.players`

Modules, functions, or names beginning with `_` are internal and may change
without notice while the package is in `0.x`.
