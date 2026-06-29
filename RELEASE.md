# Release Process

`othellopy` is published on PyPI as
[`othellopy`](https://pypi.org/project/othellopy/) from the GitHub repository
[`Hietan/othellopy`](https://github.com/Hietan/othellopy).

Releases follow the repository GitFlow rules:

- Feature work is merged into `dev` through `feat/*` pull requests.
- Release preparation happens on `release/vX.Y.Z` branches.
- Release pull requests target `main`.
- `main` requires maintainer approval and passing checks.

## Versioning

Use PEP 440-compatible versions and SemVer-style meaning where practical:

- Patch releases fix bugs without changing public APIs.
- Minor releases may add features and, while the project is `0.x`, may change
  public APIs.
- Existing PyPI versions are immutable. Never try to replace a file already
  uploaded to PyPI.

## Checklist

1. Start from an up-to-date `dev` branch.
2. Create `release/vX.Y.Z`.
3. Update `version` in `pyproject.toml`.
4. Update `__version__` in `src/othellopy/__init__.py`.
5. Update `CHANGELOG.md`, replacing `Unreleased` with the release date.
6. Confirm that `https://pypi.org/project/othellopy/X.Y.Z/` does not already
   exist.
7. Run:

   ```bash
   uv run --extra dev ruff check .
   uv run --extra dev mypy src/othellopy
   uv run --extra dev pytest
   uv build
   ```

8. Open a pull request from `release/vX.Y.Z` to `main`.
9. Merge only after approval and required checks pass.
10. Tag the merge commit on `main`:

    ```bash
    git tag vX.Y.Z
    git push origin vX.Y.Z
    ```

11. Confirm that the `Publish` workflow succeeds.
12. Verify the PyPI page and a fresh install:

    ```bash
    python -m pip install --upgrade othellopy
    python -m pip show othellopy
    ```

## PyPI Trusted Publishing

The `Publish` workflow is designed for PyPI Trusted Publishing. The PyPI
project must trust this GitHub repository, the workflow
`.github/workflows/publish.yml`, and the GitHub Environment named `pypi`.

Do not store a long-lived PyPI API token in repository secrets unless Trusted
Publishing is unavailable and the token is scoped to this single project.

## Failed Releases

If a release contains a bug, do not delete or overwrite the PyPI files.
Prepare a new patch or minor version and explain the fix in `CHANGELOG.md`.
