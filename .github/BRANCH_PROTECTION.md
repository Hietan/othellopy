# GitHub Branch Protection and Rulesets

Repository files can document and check GitFlow, but GitHub must enforce direct
push rejection through branch protection or repository rulesets.

Configure these settings in GitHub before treating the repository as protected.

## Required Rules

Create rules for `main`:

- Require a pull request before merging.
- Set required approvals to `0` for the single-maintainer fork-based workflow.
- Do not require Code Owner review.
- Require status checks to pass before merging:
  - `Branch Policy / gitflow`
  - `CI / required`
- Require branches to be up to date before merging.
- Block force pushes.
- Block deletions.
- Apply rules to administrators.
- Allow only `release/*` pull requests into `main`.

Create rules for `dev`:

- Require a pull request before merging.
- Set required approvals to `0` for the single-maintainer fork-based workflow.
- Do not require Code Owner review.
- Require status checks to pass before merging:
  - `Branch Policy / gitflow`
  - `CI / required`
- Block force pushes.
- Block deletions.
- Apply rules to administrators.
- Allow `feat/*` pull requests into `dev`.
- Allow `dependabot/*` pull requests into `dev` for automated dependency
  updates.

## Branch Naming

Allowed working branches:

- `feat/*` for feature and maintenance work.
- `release/*` for release preparation.
- `dependabot/*` for automated dependency update pull requests to `dev`.

Do not push directly to `main` or `dev`. Do not merge `feat/*` directly into
`main`.
Set the repository default branch to `dev` so new development pull requests and
Dependabot security updates target the integration branch by default.

## Review Policy

This repository is maintained by a single maintainer. External contributors are
expected to work from forks and open pull requests; they cannot push or merge
directly into `dev` or `main`.

Maintainer review is optional rather than a required GitHub gate. Required
status checks, branch routing, force-push blocking, and branch deletion blocking
are the enforced safeguards.

`.github/CODEOWNERS` documents ownership, but Code Owner review should not be
required while the repository uses this single-maintainer workflow.

## PyPI Publishing

Create and protect the GitHub Environment named `pypi`.

- Require maintainer approval before deployment.
- Configure PyPI Trusted Publishing for repository `Hietan/othellopy`,
  workflow `.github/workflows/publish.yml`, and environment `pypi`.
- Do not store broad PyPI credentials in repository secrets.
