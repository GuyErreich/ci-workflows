# Semver app ruleset bypasses (not applied)

Direct-main release commits `chore: release x.y.z` to `main` and creates `v*` tags with the GitHub App token. Those writes need an **always** bypass on both existing rulesets. App-API commits should show as verified on GitHub; confirm that on the first real run.

`rulesets/apply-bypasses.sh` **GETs the live ruleset**, adds only the actor in `rulesets/bypass-actor.json` if it is missing, and prints the PUT body. It does **not** store or PUT a full saved snapshot (a stale snapshot would overwrite later ruleset edits). **Do not apply from this change.**

## Required bypasses

| Ruleset | ID | Target | Bypass |
|---|---|---|---|
| Releases | `25303595` | `refs/tags/v*` | Integration `SEMVER_APP_ID`, `bypass_mode: always` |
| Standard Flow (main) | `25303593` | default branch | Integration `SEMVER_APP_ID`, `bypass_mode: always` |

`always` on main is required because the release commit is pushed directly, not via a pull request.

## Token hygiene

The release job writes the app token into the git remote (`git remote set-url` with `x-access-token`). After that, the **only** allowed third-party step is the pinned `GuyErreich/Action-Semver-Control` action at `7060fb502694ffdff0a40baf9c671c10afedcd66` (`v1` / 1.8.19). No other third-party step may run after the token is in the remote.

## How to apply later

1. Export `SEMVER_APP_ID` as the numeric GitHub App id (not the `Iv1.` client id).
2. Run `rulesets/apply-bypasses.sh` (print-only). Confirm the merged PUT body.
3. Re-run with `--i-understand-this-mutates-github` only when Guy is applying. The placeholder id is refused.
