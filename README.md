# ci-workflows
Reusable GitHub Actions workflows and configs shared across my repos. Callers pin `uses:` to a full commit SHA with a version comment; Dependabot bumps it.

| Workflow | Owner | Purpose |
|---|---|---|
| license.yml | Ray | GPL-3.0-or-later SPDX headers on Kotlin and XML |
| lint.yml | Ray | Android lint, errors fail, baseline for existing warnings |
| ktlint.yml | Ray | ktlint format check |
| pr-title.yml | Ray | Conventional PR titles matching autosemver categories (release-note grouping only; `Release x.y.z` titles exempt) |
| secret-scan.yml | Adam | gitleaks |
| codeql.yml | Adam | CodeQL for Kotlin/Java and the workflow files |
| test.yml | Gali | Robolectric/unit tests and reports |

All workflows default to `permissions: {}` and grant per job.
