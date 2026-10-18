# ci-workflows
Reusable GitHub Actions workflows and configs shared across my repos. Callers pin `uses:` to a full commit SHA with a version comment; Dependabot bumps it.

| Workflow | Owner | Purpose |
|---|---|---|
| license.yml | Ray | GPL-3.0-or-later SPDX headers on Kotlin and XML |
| lint.yml | Ray | Android lint, errors fail, baseline for existing warnings |
| ktlint.yml | Ray | ktlint format check |
| pr-title.yml | Ray | Conventional PR titles matching autosemver categories (release-note grouping only; `Release x.y.z` titles from `auto-semver-bot[bot]` exempt) |
| secret-scan.yml | Adam | gitleaks |
| codeql.yml | Adam | CodeQL for Kotlin/Java and the workflow files |
| test.yml | Gali | Robolectric/unit tests and reports |
| auto-semver.yml | Guy | Version bump, changelog, and `v*` tag on push to `main` |

All reusable workflows default to `permissions: {}` and grant per job.

## Auto-semver (this repo)

This repository **tags and releases directly from `main`**. `.github/workflows/auto-semver.yml` runs only on `push` to `main` (never `pull_request` / `pull_request_target`). It uses the same GitHub App pattern as [Backpin](https://github.com/GuyErreich/Backpin) and pins [Action-Semver-Control](https://github.com/GuyErreich/Action-Semver-Control) at `7060fb502694ffdff0a40baf9c671c10afedcd66` (`v1` / 1.8.19) **for version math only**.

ASC 1.8.19 `bump` always opens a `Release x.y.z` PR (`cli/bump.py` `_publish_release`). That path is not invoked. There is no `pull_request` / `release.strategy` template here. After `chore: release x.y.z` lands, the workflow skips so there is no second bump.

**Bumps:** ASC classic mode defaults **unknown prefixes (including `cursor/`) to patch** (`version.py` `detect_bump_type`). This repo maps the merged PR title onto a prefix ASC understands (`feat`/`feature`/`add`/`enhance` → `feature/` = minor; `fix`/`bug`/`hotfix`/`patch` → `fix/` = patch; `BREAKING CHANGE:` / `breaking:` / `major:` / `type!` → `breaking/` = major). Evidence: `ASC_SRC=... python3 scripts/dry-run-cursor-bump.py`.

**Release-note categories** follow Backpin headings (Breaking, Features, Refactoring, Infrastructure, Fixes, Testing, Documentation). The union of type prefixes is exactly the 27 `pr-title.yml` types. No `Other Changes`.

The `tag and release` job uses `contents: read` on `GITHUB_TOKEN`. All writes use the GitHub App token, scoped to this repository with `permission-contents: write`. The `chore: release x.y.z` commit is created with GraphQL `createCommitOnBranch` (`expectedHeadOid` = the starting `main` SHA) so GitHub signs it and the mutation fails if `main` has moved. The `v*` tag is created on that commit SHA via the REST refs API, then the GitHub Release. The token is not written into the git remote. **No third-party step may run while the app token is available.** App-API commits should be verified; confirm on the first run.

Ruleset **always** bypasses (GET live ruleset, add actor if missing, PUT) are in [docs/semver-bypass.md](docs/semver-bypass.md) and [rulesets/](rulesets/). Not applied by this change.
