# GitHub Branch Protection and Rulesets

Repository files can document and check GitFlow, but GitHub must enforce direct
push rejection through branch protection or repository rulesets.

Configure these settings in GitHub before treating the repository as protected.

## Required Rules

Create rules for `main`:

- Require a pull request before merging.
- Require at least 1 approval.
- Require review from Code Owners.
- Dismiss stale approvals when new commits are pushed.
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
- Require at least 1 approval.
- Require review from Code Owners.
- Dismiss stale approvals when new commits are pushed.
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

Do not push directly to `main`. Do not merge `feat/*` directly into `main`.
Set the repository default branch to `dev` so new development pull requests and
Dependabot security updates target the integration branch by default.

## Approval Ownership

`.github/CODEOWNERS` assigns ownership to `@Hietan`. With code owner review
enabled, pull requests require Hietan approval before merge.

## PyPI Publishing

Create and protect the GitHub Environment named `pypi`.

- Require maintainer approval before deployment.
- Configure PyPI Trusted Publishing for repository `Hietan/othellopy`,
  workflow `.github/workflows/publish.yml`, and environment `pypi`.
- Do not store broad PyPI credentials in repository secrets.
