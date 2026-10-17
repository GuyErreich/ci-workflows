# Semver app ruleset bypasses (not applied)

Direct-main release commits `chore: release x.y.z` to `main` and creates `v*` tags with the GitHub App token. Those writes need an **always** bypass on both existing rulesets. App-API commits should show as verified on GitHub; confirm that on the first real run.

`rulesets/apply-bypasses.sh` **GETs the live ruleset**, adds only the actor in `rulesets/bypass-actor.json` if it is missing, and prints the PUT body. It does **not** store or PUT a full saved snapshot (a stale snapshot would overwrite later ruleset edits). **Do not apply from this change.**

## Required bypasses

| Ruleset | ID | Target | Bypass |
|---|---|---|---|
| Releases | `25303595` | `refs/tags/v*` | Integration `SEMVER_APP_ID`, `bypass_mode: always` |
| Standard Flow (main) | `25303593` | default branch | Integration `SEMVER_APP_ID`, `bypass_mode: always` |

`always` on main is required because the release commit is pushed directly, not via a pull request.

## How to apply later

1. Export `SEMVER_APP_ID` as the numeric GitHub App id (not the `Iv1.` client id).
2. Run `rulesets/apply-bypasses.sh` (print-only). Confirm the merged PUT body.
3. Re-run with `--i-understand-this-mutates-github` only when Guy is applying. The placeholder id is refused.
