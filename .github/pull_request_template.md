## Summary

- 

## Checklist

- [ ] The change follows the GitFlow branch rules in `CONTRIBUTING.md`.
- [ ] Commit messages follow the format in `CONTRIBUTING.md`.
- [ ] Tests were added or updated when behavior changed.
- [ ] Documentation was updated when public behavior changed.
- [ ] `CHANGELOG.md` was updated for user-visible or public API changes.
- [ ] PyPI package metadata remains accurate when packaging or release files
      changed.
- [ ] `uv run --extra dev ruff format --check .` passes.
- [ ] `uv run --extra dev ruff check .` passes.
- [ ] `uv run --extra dev mypy .` passes.
- [ ] `uv run --extra dev pytest` passes.

## Notes for Reviewers

Mention any API compatibility concerns, release notes, or follow-up work here.
