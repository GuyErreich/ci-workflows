# Semver app bypass (do not apply from CI)

`apply-bypasses.sh` **GETs the live ruleset**, adds the actor in `bypass-actor.json` if it is not already there, and prints the PUT body. It does not ship full snapshots.

| File | Purpose |
|---|---|
| `bypass-actor.json` | Minimal actor fragment (`Integration` + `always`) |
| `apply-bypasses.sh` | Live GET → merge → print PUT (apply only with the explicit flag) |

Set `SEMVER_APP_ID` to the numeric GitHub App id before applying. The placeholder is refused. See [docs/semver-bypass.md](../docs/semver-bypass.md).
