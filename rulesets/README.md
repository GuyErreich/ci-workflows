# Prepared ruleset updates (do not apply from CI)

Draft JSON + `gh api` commands for the semver GitHub App **always** bypasses described in [docs/semver-bypass.md](../docs/semver-bypass.md).

| File | Purpose |
|---|---|
| `releases-always-bypass.json` | PUT body for ruleset **Releases** (`25303595`, `v*` tags) |
| `main-always-bypass.json` | PUT body for ruleset **Standard Flow (main)** (`25303593`) |
| `apply-bypasses.sh` | Prints (or, only with an explicit flag, runs) the two `gh api` PUTs |

Replace `SEMVER_APP_ID` with the numeric App id before any apply. These files are documentation and command templates only.
