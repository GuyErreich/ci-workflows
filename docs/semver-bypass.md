# Semver app ruleset bypasses (not applied)

Action-Semver-Control uses a GitHub App installation token (`signed-commits: true`) so finalize can write `chore: finalize semver lock` directly to `main` and create `v*` tags. Those writes need an **always** bypass on both existing rulesets. App-API commits should show as verified on GitHub; confirm that on the first real run.

Prepared payloads and commands live in `rulesets/`. **Do not apply them from this change.** Guy applies them later after substituting `SEMVER_APP_ID`.

## Required bypasses

| Ruleset | ID | Target | Bypass |
|---|---|---|---|
| Releases | `25303595` | `refs/tags/v*` | Integration `SEMVER_APP_ID`, `bypass_mode: always` |
| Standard Flow (main) | `25303593` | default branch | Integration `SEMVER_APP_ID`, `bypass_mode: always` |

`always` on main is required because finalize is a direct commit, not a pull request. A `pull_request` bypass (Backpin's current main draft) is not enough here.

## How to apply later

1. Replace every `SEMVER_APP_ID` placeholder with the numeric GitHub App id (the app's `id`, not the client id / `Iv1.` value).
2. Review `rulesets/releases-always-bypass.json` and `rulesets/main-always-bypass.json` — they snapshot the live rulesets at authoring time plus the bypass.
3. Run the commands in `rulesets/apply-bypasses.sh` (prints `gh api` PUTs; refuses to execute unless you pass `--i-understand-this-mutates-github`).

See `rulesets/README.md`.
