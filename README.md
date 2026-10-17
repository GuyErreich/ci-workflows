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

This repository is a **direct `main` flow**. `.github/workflows/auto-semver.yml` runs only on `push` to `main` (never `pull_request` / `pull_request_target`). It uses the same GitHub App pattern as [Backpin](https://github.com/GuyErreich/Backpin) (`vars.GH_APP_CLIENT_ID`, `secrets.GH_APP_PRIVATE_KEY`, local `app-authentication` composite) and pins [Action-Semver-Control](https://github.com/GuyErreich/Action-Semver-Control) to the current `v1` commit (`7060fb502694ffdff0a40baf9c671c10afedcd66`, 1.8.19).

Action-Semver-Control still reads a merged-PR payload. On push, `scripts/write-auto-semver-event.sh` builds that payload from the commit's associated PR (title via jq, not `run:` interpolation). The finalize commit `chore: finalize semver lock` is skipped so the bot does not loop.

**Bumps** are branch-based inside the action (classic mode): `feature/` → minor, `fix/` (also `bug/` / `hotfix/` / `chore/` / `devops/`) → patch. That is the `feat` = minor, `fix` = patch policy. PR titles still only group release notes.

**Release-note categories** in `auto_semver_config.yml` are exactly the allowed types in `pr-title.yml` (including `ci`). There is no `Other Changes` section; unmatched lines go to an internal `Ignore` group that the changelog template omits.

`contents: write` is granted only on the `tag and release` job. App-API commits should be verified; confirm on the first run.

Required ruleset **always** bypasses for the semver app (Releases `v*` tags + `main`, so finalize can commit to `main`) are documented in [docs/semver-bypass.md](docs/semver-bypass.md) and prepared as JSON/`gh api` files under [rulesets/](rulesets/). Those files are not applied by this change.
